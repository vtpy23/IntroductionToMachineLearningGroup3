"""DS-AL equations (4)-(19), independently implemented from the publication.

All samples of a phase update the main stream BEFORE compensation targets are
computed. Updating compensation after each main-stream minibatch changes the
algorithm because the residual targets would depend on minibatch boundaries.
"""
from typing import Optional

import torch
from torch import Tensor
from torch.nn import functional as F


class AnalyticRidge:
    """Incremental multi-output ridge regression with expanding label columns.

    Args:
        dimension: Number of fixed input features.
        gamma: Positive ridge coefficient, applied once to the global objective.
        solver: ``rls`` for Woodbury updates or ``stats`` for sufficient-statistic
            accumulation followed by a Cholesky solve at the end of a phase.
        device: PyTorch computation device.
        dtype: Floating point type. float64 is the reproducibility default.
    """

    def __init__(self, dimension: int, gamma: float = 0.1, solver: str = "stats",
                 device: str = "cpu", dtype: torch.dtype = torch.float64):
        if dimension < 1 or gamma <= 0:
            raise ValueError("dimension and gamma must be positive")
        if solver not in {"rls", "stats"}:
            raise ValueError("solver must be rls or stats")
        self.dimension, self.gamma, self.solver = dimension, gamma, solver
        self.device, self.dtype = torch.device(device), dtype
        identity = torch.eye(dimension, device=self.device, dtype=dtype)
        self.matrix = identity / gamma if solver == "rls" else identity * gamma
        self.weight = torch.zeros(dimension, 0, device=self.device, dtype=dtype)
        self.cross = self.weight.clone() if solver == "stats" else None
        self.samples = 0

    def expand(self, classes: int) -> None:
        """Pad weights/statistics to ``classes`` outputs without changing old ones."""
        old = self.weight.shape[1]
        if classes < old:
            raise ValueError("class count cannot decrease")
        if classes > old:
            self.weight = F.pad(self.weight, (0, classes - old))
            if self.cross is not None:
                self.cross = F.pad(self.cross, (0, classes - old))

    @torch.no_grad()
    def update(self, x: Tensor, y: Tensor) -> None:
        """Accumulate a batch with global, zero-padded targets; return nothing."""
        x, y = x.to(self.device, self.dtype), y.to(self.device, self.dtype)
        if x.ndim != 2 or y.ndim != 2 or len(x) != len(y):
            raise ValueError("x and y must be 2-D with equal sample counts")
        if x.shape[1] != self.dimension or y.shape[1] < self.weight.shape[1]:
            raise ValueError("feature dimension or target width is inconsistent")
        if not torch.isfinite(x).all() or not torch.isfinite(y).all():
            raise ValueError("features and targets must be finite")
        self.expand(y.shape[1])
        if self.solver == "stats":
            self.matrix.addmm_(x.T, x)
            self.cross.addmm_(x.T, y)
        else:
            rx = self.matrix @ x.T
            middle = torch.eye(len(x), device=self.device, dtype=self.dtype) + x @ rx
            gain = torch.linalg.solve(middle, rx.T).T
            self.weight.add_(gain @ (y - x @ self.weight))
            self.matrix.sub_(gain @ rx.T)
            self.matrix.copy_((self.matrix + self.matrix.T) * 0.5)
        self.samples += len(x)

    @torch.no_grad()
    def finalize(self) -> Tensor:
        """Solve accumulated normal equations and return classifier weights."""
        if self.solver == "stats":
            chol = torch.linalg.cholesky(self.matrix)
            self.weight = torch.cholesky_solve(self.cross, chol)
        return self.weight

    def predict(self, x: Tensor) -> Tensor:
        """Return unnormalized class scores for feature rows ``x``."""
        return x.to(self.device, self.dtype) @ self.weight


class DualStreamAnalytic:
    """Frozen-feature DS-AL classifier, with optional DAC/PLC ablations.

    The ``buffer`` is a random feature-expansion layer, not an exemplar memory.
    Only parameter matrices and second-order statistics survive phase updates.
    """

    def __init__(self, input_dimension: int, buffer_size: int = 8192,
                 gamma: float = 0.1, gamma_comp: Optional[float] = None,
                 compensation_ratio: float = 0.6, activation: str = "tanh",
                 use_compensation: bool = True, plc: bool = True,
                 seed: int = 0, solver: str = "stats", device: str = "cpu",
                 dtype: torch.dtype = torch.float64, projection_std: float = 1.0,
                 random_bias: bool = False):
        if activation not in {"tanh", "relu", "mish", "hardswish", "leaky_relu"}:
            raise ValueError("unsupported compensation activation")
        gen = torch.Generator(device="cpu").manual_seed(seed)
        self.device, self.dtype = torch.device(device), dtype
        self.projection = (torch.randn(input_dimension, buffer_size, generator=gen,
                                       dtype=dtype) * projection_std).to(self.device)
        self.bias = (torch.randn(buffer_size, generator=gen, dtype=dtype).to(self.device)
                     if random_bias else torch.zeros(buffer_size, device=self.device, dtype=dtype))
        self.main = AnalyticRidge(buffer_size, gamma, solver, device, dtype)
        self.comp = (AnalyticRidge(buffer_size, gamma if gamma_comp is None else gamma_comp,
                                   solver, device, dtype) if use_compensation else None)
        self.ratio, self.activation, self.plc = compensation_ratio, activation, plc
        self.phase, self.classes = -1, 0

    def embeddings(self, features: Tensor):
        """Return ReLU main features and independently activated compensation features."""
        z = features.to(self.device, self.dtype) @ self.projection + self.bias
        return F.relu(z), getattr(F, self.activation)(z) if self.activation != "tanh" else z.tanh()

    @torch.no_grad()
    def fit_phase(self, features: Tensor, labels: Tensor, classes: int,
                  batch_size: int = 512) -> None:
        """Learn one complete phase from globally remapped labels.

        Args:
            features: Frozen backbone features for the current phase only.
            labels: Integer indices in the cumulative class order.
            classes: Total number of classes observed through this phase.
            batch_size: Computational chunk size, not a new learning phase.
        Returns:
            None. Updates classifier parameters and phase count in place.
        """
        if len(features) == 0 or len(features) != len(labels) or batch_size < 1:
            raise ValueError("a nonempty aligned phase and positive batch size are required")
        if classes < self.classes or labels.min() < 0 or labels.max() >= classes:
            raise ValueError("invalid cumulative class count or labels")
        old_classes = self.classes
        if self.phase >= 0 and self.plc and self.comp is not None and labels.min() < old_classes:
            raise ValueError("PLC assumes disjoint new classes between phases")
        self.main.expand(classes)
        for start in range(0, len(features), batch_size):
            x, _ = self.embeddings(features[start:start + batch_size])
            y = F.one_hot(labels[start:start + batch_size].long(), classes).to(self.device, self.dtype)
            self.main.update(x, y)
        self.main.finalize()
        if self.comp is not None:
            self.comp.expand(classes)
            for start in range(0, len(features), batch_size):
                xm, xc = self.embeddings(features[start:start + batch_size])
                y = F.one_hot(labels[start:start + batch_size].long(), classes).to(self.device, self.dtype)
                residue = y - self.main.predict(xm)
                if self.phase >= 0 and self.plc:
                    residue[:, :old_classes] = 0
                self.comp.update(xc, residue)
            self.comp.finalize()
        self.classes, self.phase = classes, self.phase + 1

    @torch.no_grad()
    def predict(self, features: Tensor, ratio: Optional[float] = None) -> Tensor:
        """Return combined class scores using Eq. (19), optionally overriding C."""
        xm, xc = self.embeddings(features)
        scores = self.main.predict(xm)
        if self.comp is not None:
            scores = scores + (self.ratio if ratio is None else ratio) * self.comp.predict(xc)
        return scores
