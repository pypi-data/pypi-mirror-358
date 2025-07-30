import warnings
from typing import Callable, Optional, List

import numpy as np
import sklearn
import torch
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from torch import nn

from probmetrics.distributions import CategoricalDistribution, CategoricalProbs, CategoricalLogits


class Calibrator(BaseEstimator, ClassifierMixin):
    """
    Calibrator base class. To implement,
    - override at least one of _fit_impl and _fit_torch_impl
    - override at least one of predict_proba and predict_proba_torch
    """

    def __init__(self):
        assert self.__class__.fit == Calibrator.fit
        assert self.__class__.fit_torch == Calibrator.fit_torch

    def fit(self, X, y) -> 'Calibrator':
        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)

        self.classes_ = list(range(X.shape[-1]))

        if self.__class__._fit_impl != Calibrator._fit_impl:
            self._fit_impl(X, y)
            return self

        if self.__class__._fit_torch_impl != Calibrator._fit_torch_impl:
            self._fit_torch_impl(y_pred=CategoricalProbs(torch.as_tensor(X)),
                                 y_true_labels=torch.as_tensor(y, dtype=torch.long))
            return self

        raise NotImplementedError()

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        raise NotImplementedError()

    def fit_torch(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor) -> 'Calibrator':
        assert isinstance(y_true_labels, torch.Tensor)
        assert isinstance(y_pred, CategoricalDistribution)
        # default implementation, using sklearn
        self.classes_ = list(range(y_pred.get_n_classes()))

        if self.__class__._fit_torch_impl != Calibrator._fit_torch_impl:
            self._fit_torch_impl(y_pred, y_true_labels)
            return self

        if self.__class__._fit_impl != Calibrator._fit_impl:
            self._fit_impl(y_pred.get_probs().detach().cpu().numpy(), y_true_labels.detach().cpu().numpy())
            return self

        raise NotImplementedError()

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        raise NotImplementedError()

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.__class__.predict_proba_torch != Calibrator.predict_proba_torch:
            return self.predict_proba_torch(CategoricalProbs(torch.as_tensor(X))).get_probs().numpy()

        raise NotImplementedError()

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        if self.__class__.predict_proba != Calibrator.predict_proba:
            y_pred_probs = y_pred.get_probs()
            probs = self.predict_proba(y_pred_probs.detach().cpu().numpy())
            return CategoricalProbs(torch.as_tensor(probs, device=y_pred_probs.device, dtype=y_pred_probs.dtype))

        raise NotImplementedError()

    def predict(self, X):
        y_probs = self.predict_proba(X)
        class_idxs = np.argmax(y_probs, axis=-1)
        return np.asarray(self.classes_)[class_idxs]


class ApplyToLogitsCalibrator(Calibrator):
    def __init__(self, calib: BaseEstimator):
        super().__init__()
        self.calib = calib

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        self.calib_ = sklearn.base.clone(self.calib)
        self.calib_.fit(np.log(X + 1e-10), y)

    def predict_proba(self, X):
        return self.calib_.predict_proba(np.log(X + 1e-10))


def bisection_search(f: Callable[[float], float], a: float, b: float, n_steps: int):
    for _ in range(n_steps):
        c = a + 0.5 * (b - a)
        f_c = f(c)
        if f_c > 0:
            b = c
        else:
            a = c

    return 0.5 * (a + b)


class TemperatureScalingCalibrator(Calibrator):
    def __init__(self, opt: str = 'bisection', max_bisection_steps: int = 30, lr: float = 0.1, max_iter: int = 200,
                 use_inv_temp: bool = True, inv_temp_init: float = 1 / 1.5):
        super().__init__()
        self.lr = lr
        self.max_bisection_steps = max_bisection_steps
        self.max_iter = max_iter
        self.use_inv_temp = use_inv_temp
        self.inv_temp_init = inv_temp_init
        self.opt = opt

    def _get_loss_grad(self, invtemp: float, logits: torch.Tensor, y: torch.Tensor):
        part_1 = torch.mean(torch.sum(logits * torch.softmax(invtemp * logits, dim=-1), dim=-1))
        part_2 = torch.mean(logits[torch.arange(logits.shape[0]), y])
        return (part_1 - part_2).item()

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        logits = y_pred.get_logits()
        labels = y_true_labels

        if self.opt in ['lbfgs', 'lbfgs_line_search']:
            self._fit_lbfgs(logits, labels)
        elif self.opt == 'bisection':
            self._fit_bisection(logits, labels)
        else:
            raise ValueError(f'Unknown optimizer "{self.opt}"')

        # print(f'{self.invtemp_=}')

    def _fit_lbfgs(self, logits: torch.Tensor, labels: torch.Tensor):
        # following https://github.com/gpleiss/temperature_scaling/blob/master/temperature_scaling.py
        param = nn.Parameter(
            torch.ones(1, device=logits.device) * (self.inv_temp_init if self.use_inv_temp else 1 / self.inv_temp_init))
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([param], lr=self.lr, max_iter=self.max_iter,
                                      line_search_fn='strong_wolfe' if self.opt == 'lbfgs_line_search' else None)

        def eval():
            optimizer.zero_grad()
            y_pred = logits * param[:, None] if self.use_inv_temp else logits / param[:, None]
            loss = criterion(y_pred, labels)
            loss.backward()
            return loss

        optimizer.step(eval)

        self.invtemp_ = param.item() if self.use_inv_temp else 1 / param.item()

    def _fit_bisection(self, logits: torch.Tensor, labels: torch.Tensor):
        objective_grad = lambda u, l=logits, tar=labels: self._get_loss_grad(np.exp(u), l, tar)

        # should reach about float32 accuracy
        # need log_2(32) = 5 steps to get to length 1 and then 24 more steps to get to float32 epsilon (2^{-24})
        self.invtemp_ = np.exp(bisection_search(objective_grad, a=-16, b=16, n_steps=self.max_bisection_steps))
        # print(f'{self.invtemp_=}')

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        return CategoricalLogits(self.invtemp_ * y_pred.get_logits())


class GuoTemperatureScalingCalibrator(Calibrator):
    # adapted from https://github.com/gpleiss/temperature_scaling/blob/master/temperature_scaling.py
    def __init__(self):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)

    def temperature_scale(self, logits):
        """
        Perform temperature scaling on logits
        """
        # Expand temperature to match the size of logits
        temperature = self.temperature.unsqueeze(1).expand(logits.size(0), logits.size(1))
        return logits / temperature

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        logits = y_pred.get_logits()
        labels = y_true_labels

        nll_criterion = nn.CrossEntropyLoss().cuda()

        # Next: optimize the temperature w.r.t. NLL
        optimizer = torch.optim.LBFGS([self.temperature], lr=0.01, max_iter=50)

        def eval():
            optimizer.zero_grad()
            loss = nll_criterion(self.temperature_scale(logits), labels)
            loss.backward()
            return loss

        optimizer.step(eval)

        return self

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        with torch.no_grad():
            return CategoricalLogits(y_pred.get_logits() / self.temperature)


class AutoGluonTemperatureScalingCalibrator(Calibrator):
    # adapted from
    # https://github.com/autogluon/autogluon/blob/c1181326cf6b7e3b27a7420273f1a82808d939e2/core/src/autogluon/core/calibrate/temperature_scaling.py#L9
    # https://github.com/autogluon/autogluon/blob/28a242ebe8d55ba770c991b9db153ab4623c9abd/tabular/src/autogluon/tabular/trainer/abstract_trainer.py#L4433-L4457
    def __init__(self, init_val: float = 1, max_iter: int = 200, lr: float = 0.1):
        super().__init__()
        self.init_val = init_val
        self.max_iter = max_iter
        self.lr = lr
        self.temperature = init_val

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        y_val_tensor = y_true_labels
        temperature_param = torch.nn.Parameter(torch.ones(1).fill_(self.init_val))
        logits = y_pred.get_logits()

        is_invalid = torch.isinf(logits).any().tolist()
        if is_invalid:
            return

        nll_criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([temperature_param], lr=self.lr, max_iter=self.max_iter)
        scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.99)

        optimizer_trajectory = []

        if self.init_val != 1.0:
            # need to check 1.0 as well since AutoGluon does it outside
            optimizer_trajectory.append((nll_criterion(logits, y_val_tensor).item(), 1.0))

        def temperature_scale_step():
            optimizer.zero_grad()
            temp = temperature_param.unsqueeze(1).expand(logits.size(0), logits.size(1))
            new_logits = logits / temp
            loss = nll_criterion(new_logits, y_val_tensor)
            loss.backward()
            scheduler.step()
            optimizer_trajectory.append((loss.item(), temperature_param.item()))
            return loss

        optimizer.step(temperature_scale_step)

        try:
            best_loss_index = np.nanargmin(np.array(optimizer_trajectory)[:, 0])
        except ValueError:
            self.temperature = 1.0
            return
        temperature_scale = float(np.array(optimizer_trajectory)[best_loss_index, 1])

        if np.isnan(temperature_scale) or temperature_scale <= 0.0:
            self.temperature = 1.0
            return

        self.temperature = temperature_scale

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        with torch.no_grad():
            return CategoricalLogits(y_pred.get_logits() / self.temperature)


class AutoGluonInverseTemperatureScalingCalibrator(Calibrator):
    # adapted from
    # https://github.com/autogluon/autogluon/blob/c1181326cf6b7e3b27a7420273f1a82808d939e2/core/src/autogluon/core/calibrate/temperature_scaling.py#L9
    # but optimizing the inverse temperature instead
    def __init__(self, init_val: float = 1, max_iter: int = 200, lr: float = 0.1):
        super().__init__()
        self.init_val = init_val
        self.max_iter = max_iter
        self.lr = lr
        self.inv_temp = init_val

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        y_val_tensor = y_true_labels
        inv_temperature_param = torch.nn.Parameter(torch.ones(1).fill_(self.init_val))
        logits = y_pred.get_logits()

        is_invalid = torch.isinf(logits).any().tolist()
        if is_invalid:
            return

        nll_criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.LBFGS([inv_temperature_param], lr=self.lr, max_iter=self.max_iter)
        scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.99)

        optimizer_trajectory = []

        def temperature_scale_step():
            optimizer.zero_grad()
            inv_temp = inv_temperature_param.unsqueeze(1).expand(logits.size(0), logits.size(1))
            new_logits = logits * inv_temp
            loss = nll_criterion(new_logits, y_val_tensor)
            loss.backward()
            scheduler.step()
            optimizer_trajectory.append((loss.item(), inv_temperature_param.item()))
            return loss

        optimizer.step(temperature_scale_step)

        try:
            best_loss_index = np.nanargmin(np.array(optimizer_trajectory)[:, 0])
        except ValueError:
            return
        inv_temperature_scale = float(np.array(optimizer_trajectory)[best_loss_index, 1])

        if np.isnan(inv_temperature_scale):
            return

        self.inv_temp = inv_temperature_scale

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        with torch.no_grad():
            return CategoricalLogits(y_pred.get_logits() * self.inv_temp)


class TorchUncertaintyTemperatureScalingCalibrator(TemperatureScalingCalibrator):
    # adapted from
    # https://github.com/ENSTA-U2IS-AI/torch-uncertainty/blob/3a021d2e34e183b8aad3a0345e6d750c08c72af3/torch_uncertainty/post_processing/calibration/scaler.py#L1
    # https://github.com/ENSTA-U2IS-AI/torch-uncertainty/blob/3a021d2e34e183b8aad3a0345e6d750c08c72af3/torch_uncertainty/post_processing/calibration/temperature_scaler.py#L9
    def __init__(self, init_val: float = 1, lr: float = 0.1, max_iter: int = 100):
        super().__init__(opt='lbfgs', lr=lr, max_iter=max_iter, use_inv_temp=False, inv_temp_init=1. / init_val)
        # need to save these values here to comply with sklearn cloneability conventions
        self.init_val = init_val
        self.lr = lr
        self.max_iter = max_iter


class NetcalTemperatureScalingCalibrator(Calibrator):
    # this one does nothing due to https://github.com/EFS-OpenSource/calibration-framework/issues/61
    def __init__(self):
        super().__init__()

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        from netcal.scaling import TemperatureScaling

        self.cal_ = TemperatureScaling()
        if X.shape[1] == 2:
            # binary, convert
            X = X[:, 1]
        self.cal_.fit(X, y, random_state=0)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if X.shape[1] == 2:
            # binary, convert
            X = X[:, 1]
        result = self.cal_.transform(X)
        if len(result.shape) == 1:
            return np.stack([1. - result, result], axis=1)
        elif result.shape[1] == 1:
            return np.concatenate([1. - result, result], axis=1)

        return result


class TorchcalTemperatureScalingCalibrator(Calibrator):
    # adapted from
    # https://github.com/rishabh-ranjan/torchcal/blob/3fb65f6423d33d680cd68c7f40a0259d41e8fb0b/torchcal.py#L8
    def __init__(self):
        super().__init__()
        self.temperature = 1.0

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        import torchmin
        y_pred_logits = y_pred.get_logits()

        temp = torch.ones(1, device=y_pred_logits.device)

        def loss(t):
            return torch.nn.functional.cross_entropy(y_pred_logits / t, y_true_labels)

        res = torchmin.minimize(loss, temp, method='newton-exact')
        if not res.success:
            warnings.warn(
                f"{self.__class__}: {res.message} Not updating calibrator params."
            )
        else:
            temp = res.x

        self.temperature = temp.item()

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        return CategoricalLogits(y_pred.get_logits() / self.temperature)


class CenteredIsotonicRegressionCalibrator(Calibrator):
    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        assert not np.any(np.isnan(X))
        # print(f'{np.unique(y)=}')
        # print(f'{np.unique(X)=}')
        # we have to use float64 since with float32 it can happen that somewhere internally
        # a rounding error occurs (?) and interp1d thinks that it is asked to extrapolate at the boundary value,
        # which causes it to output nan values,
        # which are seen as a separate possible value but (y==value) is empty because nan==nan is false,
        # so an error occurs because the method attempts to take an average of an empty set
        X = X.astype(np.float64)
        y = y.astype(np.float64)
        from cir_model import CenteredIsotonicRegression
        self.cal_ = CenteredIsotonicRegression()
        self.cal_.fit(X[:, 1], y)
        self.min_ = np.min(X[:, 1])
        self.max_ = np.max(X[:, 1])

    def predict_proba(self, X):
        # have to clip since CenteredIsotonicRegression refuses to extrapolate (?)
        X = X.astype(np.float64)
        X = np.clip(X, self.min_, self.max_)
        pred_probs = self.cal_.transform(X[:, 1])
        pred_probs = np.clip(pred_probs, 0.0, 1.0)
        return np.stack([1. - pred_probs, pred_probs], axis=-1)


class BinaryVennAbersCalibrator(Calibrator):
    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        from venn_abers import VennAbers
        self.va_ = VennAbers()
        self.va_.fit(X, y)

    def predict_proba(self, X):
        return self.va_.predict_proba(X)[0]


class VennAbersCalibrator(Calibrator):
    def __init__(self, use_ovo: bool = False):
        super().__init__()
        self.use_ovo = use_ovo

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        self.X_ = np.copy(X)
        self.y_ = np.copy(y)

    def predict_proba(self, X):
        from venn_abers import VennAbersCalibrator
        va = VennAbersCalibrator()
        return va.predict_proba(p_cal=self.X_, y_cal=self.y_, p_test=X, p0_p1_output=False,
                                va_type='one_vs_one' if self.use_ovo else 'one_vs_all')


class MulticlassOneVsOneCalibrator(Calibrator):
    def __init__(self, binary_calibrator: BaseEstimator):
        super().__init__()
        self.binary_calibrator = binary_calibrator

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        self.n_classes_ = X.shape[-1]
        self.bin_calibs_ = []

        if self.n_classes_ == 2:
            # binary classification
            bin_calib = sklearn.base.clone(self.binary_calibrator)
            bin_calib.fit(X, y)
            self.bin_calibs_.append(bin_calib)
        else:
            for i in range(self.n_classes_):
                for j in range(i + 1, self.n_classes_):
                    idxs = np.logical_or((y == i), (y == j))
                    # idxs = np.arange(X.shape[0])
                    bin_probs = np.stack([X[idxs, j], X[idxs, i]], axis=-1)
                    bin_probs += 1e-30
                    bin_probs /= np.sum(bin_probs, axis=-1, keepdims=True)
                    # print(f'{np.any(np.isnan(bin_probs))=}')
                    bin_labels = (y[idxs] == i).astype(np.int32)
                    bin_calib = sklearn.base.clone(self.binary_calibrator)
                    bin_calib.fit(bin_probs, bin_labels)
                    self.bin_calibs_.append(bin_calib)

    def predict_proba(self, X):
        if self.n_classes_ == 2:
            # binary classification
            return self.bin_calibs_[0].predict_proba(X)
        else:
            # use PKPD formula in http://proceedings.mlr.press/v60/manokhin17a/manokhin17a.pdf
            pair_probs = [[None] * self.n_classes_ for i in range(self.n_classes_)]
            multi_probs = []
            calib_idx = 0
            for i in range(self.n_classes_):
                for j in range(i + 1, self.n_classes_):
                    bin_probs = np.stack([X[:, j], X[:, i]], axis=-1)
                    bin_probs += 1e-30
                    bin_probs /= np.sum(bin_probs, axis=-1, keepdims=True)
                    pred_probs = self.bin_calibs_[calib_idx].predict_proba(bin_probs)
                    pair_probs[i][j] = pred_probs[:, 1]
                    pair_probs[j][i] = pred_probs[:, 0]
                    # if i == 0 and j == 1:
                    #     print(f'{bin_probs=}')
                    #     print(f'{pred_probs=}')
                    calib_idx += 1

            for i in range(self.n_classes_):
                sum_inv_probs = sum([1. / (1e-30 + pair_probs[i][j]) for j in range(self.n_classes_) if j != i])
                multi_probs.append(1. / np.clip(sum_inv_probs - (self.n_classes_ - 2), 1e-30, np.inf))

            multi_probs = np.stack(multi_probs, axis=-1)
            multi_probs = np.clip(multi_probs, a_min=1e-30, a_max=np.inf)
            multi_probs = multi_probs / np.sum(multi_probs, axis=-1, keepdims=True)
            return multi_probs


class MulticlassOneVsRestCalibrator(Calibrator):
    def __init__(self, binary_calibrator: BaseEstimator):
        super().__init__()
        self.binary_calibrator = binary_calibrator

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        self.n_classes_ = X.shape[-1]
        self.bin_calibs_ = []

        X[np.isnan(X)] = 0.0

        if self.n_classes_ == 2:
            # binary classification
            bin_calib = sklearn.base.clone(self.binary_calibrator)
            bin_calib.fit(X, y)
            self.bin_calibs_.append(bin_calib)
        else:
            for i in range(self.n_classes_):
                pos_probs = X[:, i]
                neg_probs = 1. - pos_probs
                bin_probs = np.stack([neg_probs, pos_probs], axis=-1)
                bin_labels = (y == i).astype(np.int32)
                bin_calib = sklearn.base.clone(self.binary_calibrator)
                bin_calib.fit(bin_probs, bin_labels)
                self.bin_calibs_.append(bin_calib)

    def predict_proba(self, X):
        X[np.isnan(X)] = 0.0
        if self.n_classes_ == 2:
            # binary classification
            return self.bin_calibs_[0].predict_proba(X)
        else:
            multi_probs = []
            for i in range(self.n_classes_):
                pos_probs = X[:, i]
                neg_probs = 1. - pos_probs
                bin_probs = np.stack([neg_probs, pos_probs], axis=-1)
                pred_probs = self.bin_calibs_[i].predict_proba(bin_probs)
                multi_probs.append(pred_probs[:, 1])
            multi_probs = np.stack(multi_probs, axis=-1)
            multi_probs = np.clip(multi_probs, a_min=1e-30, a_max=np.inf)
            multi_probs = multi_probs / np.sum(multi_probs, axis=-1, keepdims=True)
            return multi_probs


class IdentityEstimator(ClassifierMixin, BaseEstimator):
    def __init__(self, n_classes: int):
        self.n_classes = n_classes
        # somehow it can fail if we don't do the np.asarray()
        self.classes_ = np.asarray(list(range(n_classes)))

    def fit(self, X, y):
        # self.classes_ = np.unique(y)  # if we do this we have a problem for missing classes
        return self

    def predict_proba(self, X):
        return X

    def predict(self, X):
        # having this as a dummy here for the FrozenEstimator solution
        # which hovewer doesn't work right now
        raise NotImplementedError()


class SklearnCalibrator(Calibrator):
    def __init__(self, method: str, cv: str):
        super().__init__()
        self.method = method
        self.cv = cv

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        n_classes = X.shape[-1]
        est = IdentityEstimator(n_classes)
        est.fit(X, y)

        # tried this workaround for deprecation warnings, but it complains in case of missing classes because it still tries to fit the estimator
        # try:
        #     # cv='prefit' option is deprecated from sklearn 1.6, FrozenEstimator was introduced in sklearn 1.6
        #     from sklearn.frozen import FrozenEstimator
        #     self.calib_ = CalibratedClassifierCV(FrozenEstimator(est), method=self.method, cv=[(np.arange(0), np.arange(X.shape[0]))])
        # except ImportError:
        #     self.calib_ = CalibratedClassifierCV(est, method=self.method, cv=self.cv)

        self.calib_ = CalibratedClassifierCV(est, method=self.method, cv=self.cv)
        self.calib_.fit(X, y)
        self.classes_ = est.classes_

    def predict_proba(self, X):
        return self.calib_.predict_proba(X)


class WrapCalibratorAsClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, calib: BaseEstimator):
        self.calib = calib

    def fit(self, X, y):
        # print(f'Fitting calibrator: {self.calib}')
        self.calib_ = sklearn.base.clone(self.calib)
        self.calib_.fit(X, y)
        self.classes_ = list(range(np.max(y) + 1))
        return self

    def predict_proba(self, X):
        return self.calib_.predict_proba(X)


def logloss_np(y_true: np.ndarray, y_proba: np.ndarray):
    return -np.mean(np.take_along_axis(np.log(y_proba), y_true[:, None], axis=1))


class DirichletCalibrator(Calibrator):
    def __init__(self, n_cv: int = 0, use_odir: bool = False,
                 reg_lambda: float = 0.0, reg_mu: Optional[float] = None,
                 reg_lambda_grid: Optional[List[float]] = None, reg_mu_grid: Optional[List[float]] = None):
        super().__init__()

        self.n_cv = n_cv
        self.use_odir = use_odir
        self.reg_lambda = reg_lambda
        self.reg_mu = reg_mu
        self.reg_lambda_grid = reg_lambda_grid
        self.reg_mu_grid = reg_mu_grid

    def _fit_impl(self, X: np.ndarray, y: np.ndarray) -> None:
        from dirichletcal.calib.fulldirichlet import FullDirichletCalibrator
        if self.n_cv == 0:
            self.cal_ = FullDirichletCalibrator(reg_lambda=self.reg_lambda, reg_mu=self.reg_mu)
        elif self.n_cv >= 2:
            reg_lambda_grid = self.reg_lambda_grid or [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
            reg_mu_grid = self.reg_mu_grid or [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]
            calibrator = FullDirichletCalibrator(reg_lambda=reg_lambda_grid,
                                                 reg_mu=reg_mu_grid if self.use_odir else None)
            calibrator = WrapCalibratorAsClassifier(calibrator)
            skf = StratifiedKFold(n_splits=self.n_cv, shuffle=True, random_state=0)
            self.cal_ = GridSearchCV(calibrator, param_grid={'calib__reg_lambda': reg_lambda_grid,
                                                             'calib__reg_mu': reg_mu_grid if self.use_odir else [None]},
                                     cv=skf,
                                     # use this because scikit-learn's logloss scorer fails in case of missing classes
                                     scoring=lambda est, X_test, y_test: -logloss_np(y_test, est.predict_proba(X_test)))
        else:
            raise ValueError(f'n_cv must be either 0 or >=2, but is {self.n_cv}')

        self.cal_.fit(X, y)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.cal_.predict_proba(X)


class MixtureCalibrator(Calibrator):
    def __init__(self, calibrator: Calibrator, output_constant: float = 1.0, input_constant: float = 0.0):
        super().__init__()
        self.calibrator = calibrator
        self.output_constant = output_constant
        self.input_constant = input_constant

    def _get_mixture(self, dist_1: CategoricalDistribution, unif_coef: float):
        probs = dist_1.get_probs()
        unif_probs = (1.0 / probs.shape[-1]) * torch.ones_like(probs)
        return CategoricalProbs((1.0 - unif_coef) * probs + unif_coef * unif_probs)

    def _fit_torch_impl(self, y_pred: CategoricalDistribution, y_true_labels: torch.Tensor):
        self.n_samples_ = y_pred.get_n_samples()
        if self.input_constant != 0.0:
            y_pred = self._get_mixture(y_pred, self.input_constant / (self.n_samples_ + 1))
        self.cal_ = sklearn.base.clone(self.calibrator)
        self.cal_.fit_torch(y_pred, y_true_labels)

    def predict_proba_torch(self, y_pred: CategoricalDistribution) -> CategoricalDistribution:
        if self.input_constant != 0.0:
            y_pred = self._get_mixture(y_pred, self.input_constant / (self.n_samples_ + 1))
        y_pred = self.cal_.predict_proba_torch(y_pred)
        if self.output_constant != 0.0:
            y_pred = self._get_mixture(y_pred, self.output_constant / (self.n_samples_ + 1))

        return y_pred


def get_calibrator(calibration_method: str, calibrate_with_mixture: bool = False,
                   cal_mixture_output_constant: float = 1.0,
                   cal_mixture_input_constant: float = 0.0, **config) -> Calibrator:
    if calibration_method == 'platt':
        cal = SklearnCalibrator(method='sigmoid', cv='prefit')
    elif calibration_method == 'platt-logits':
        cal = ApplyToLogitsCalibrator(SklearnCalibrator(method='sigmoid', cv='prefit'))
    elif calibration_method == 'isotonic':
        cal = SklearnCalibrator(method='isotonic', cv='prefit')
    elif calibration_method == 'ivap':
        cal = VennAbersCalibrator(use_ovo=config.get('va_use_ovo', False))
    elif calibration_method == 'ivap-ovr':
        cal = MulticlassOneVsRestCalibrator(BinaryVennAbersCalibrator())
    elif calibration_method == 'ivap-ovo':
        cal = MulticlassOneVsOneCalibrator(BinaryVennAbersCalibrator())
    elif calibration_method == 'isotonic-naive-ovr':
        # should be the same as 'isotonic', this is just to check
        cal = MulticlassOneVsRestCalibrator(SklearnCalibrator(method='isotonic', cv='prefit'))
    elif calibration_method == 'cir':
        cal = MulticlassOneVsRestCalibrator(CenteredIsotonicRegressionCalibrator())
    elif calibration_method in ['temp-scaling', 'ts-mix']:
        cal = TemperatureScalingCalibrator(opt=config.get('ts_opt', 'bisection'),
                                           max_bisection_steps=config.get('ts_max_bisection_steps', 30),
                                           lr=config.get('ts_lr', 0.1),
                                           max_iter=config.get('ts_max_iter', 200),
                                           use_inv_temp=config.get('ts_use_inv_temp', True),
                                           inv_temp_init=config.get('ts_inv_temp_init', 1 / 1.5),
                                           )
    elif calibration_method == 'torchunc-ts':
        cal = TorchUncertaintyTemperatureScalingCalibrator(init_val=config.get('ts_init_val', 1),
                                                           lr=config.get('ts_lr', 0.1),
                                                           max_iter=config.get('ts_max_iter', 100))
    elif calibration_method == 'guo-ts':
        cal = GuoTemperatureScalingCalibrator()
    elif calibration_method == 'torchcal-ts':
        cal = TorchcalTemperatureScalingCalibrator()
    elif calibration_method == 'autogluon-ts':
        cal = AutoGluonTemperatureScalingCalibrator(init_val=config.get('ts_init_val', 1),
                                                    max_iter=config.get('ts_max_iter', 200),
                                                    lr=config.get('ts_lr', 0.1))
    elif calibration_method == 'autogluon-inv-ts':
        cal = AutoGluonInverseTemperatureScalingCalibrator(init_val=config.get('ts_init_val', 1),
                                                           max_iter=config.get('ts_max_iter', 200),
                                                           lr=config.get('ts_lr', 0.1))
    elif calibration_method == 'dircal':
        cal = DirichletCalibrator(n_cv=0, reg_lambda=config.get('dircal_reg_lambda', 0.0),
                                  reg_mu=config.get('dircal_reg_mu', None))
    elif calibration_method == 'dircal-cv':
        cal = DirichletCalibrator(n_cv=config.get('dircal_n_cv', 5), use_odir=config.get('dircal_use_odir', False),
                                  reg_lambda_grid=config.get('dircal_reg_lambda_grid', None),
                                  reg_mu_grid=config.get('dircal_reg_mu_grid', None))
    else:
        raise ValueError(f'Unknown calibration method "{calibration_method}"')

    if calibrate_with_mixture or calibration_method.endswith('-mix'):
        cal = MixtureCalibrator(cal, output_constant=cal_mixture_output_constant,
                                input_constant=cal_mixture_input_constant)

    return cal
