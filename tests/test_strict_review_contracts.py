"""Independent mathematical and metric oracles for the strict academic review."""
import numpy as np
import pytest
import torch

from scripts.analyze_saved_classifiers import accuracy_by_group, paired_changes
from src.datasets.cifar100 import class_order
from src.methods import DualStreamAnalytic


def test_class_order_inverse_preserves_original_label_meaning():
    orders = [class_order(s) for s in range(3)]
    for order in orders:
        inverse = np.argsort(order)
        assert np.array_equal(inverse[order], np.arange(100))
    assert len({tuple(order) for order in orders}) == 3


def test_projection_seed_is_local_repeatable_and_independent():
    first = DualStreamAnalytic(5, 9, seed=1)
    torch.manual_seed(999)
    again = DualStreamAnalytic(5, 9, seed=1)
    other = DualStreamAnalytic(5, 9, seed=2)
    assert torch.equal(first.projection, again.projection)
    assert not torch.equal(first.projection, other.projection)


@pytest.mark.parametrize("solver", ["stats", "rls"])
def test_multiphase_chunk_semantics_and_zero_compensation(solver):
    x = torch.randn(36, 5, generator=torch.Generator().manual_seed(12), dtype=torch.float64)
    y = torch.tensor([0, 1] * 9 + [2, 3] * 9)
    whole = DualStreamAnalytic(5, 9, seed=3, solver=solver)
    split = DualStreamAnalytic(5, 9, seed=3, solver=solver)
    for model, chunk in [(whole, 18), (split, 4)]:
        model.fit_phase(x[:18], y[:18], 2, chunk)
        model.fit_phase(x[18:], y[18:], 4, chunk)
    torch.testing.assert_close(whole.predict(x), split.predict(x), rtol=1e-8, atol=1e-8)
    torch.testing.assert_close(whole.predict(x, ratio=0), whole.main.predict(whole.embeddings(x)[0]))


def test_accuracy_is_sample_weighted_and_paired_counts_explain_delta():
    labels = torch.tensor([0, 1, 2, 50])
    before = torch.tensor([0, 9, 2, 1])
    after = torch.tensor([8, 1, 2, 50])
    measured = accuracy_by_group(after, labels)
    assert measured["all_accuracy"] == 75
    assert measured["base_accuracy"] == pytest.approx(200 / 3)
    assert measured["novel_accuracy"] == 100
    flips = paired_changes(before, after, labels)
    assert flips["all"] == {"corrected": 2, "harmed": 1, "net_pp": 25, "count": 4}
    assert (3 * measured["base_accuracy"] + measured["novel_accuracy"]) / 4 == 75


def test_ridge_residual_obeys_regularized_normal_equations_not_nullspace():
    gen = torch.Generator().manual_seed(19)
    x = torch.randn(25, 7, dtype=torch.float64, generator=gen)
    y = torch.randn(25, 3, dtype=torch.float64, generator=gen)
    gamma = 0.4
    w = torch.linalg.solve(x.T @ x + gamma * torch.eye(7, dtype=x.dtype), x.T @ y)
    residual = y - x @ w
    torch.testing.assert_close(x.T @ residual, gamma * w, rtol=1e-10, atol=1e-10)
    assert (x.T @ residual).norm().item() > 1e-3
