"""Mathematical contracts, not implementation-mirroring smoke assertions."""
import pytest
import torch

from src.methods import AnalyticRidge, DualStreamAnalytic


@pytest.mark.parametrize("solver", ["rls", "stats"])
def test_expanding_recursive_ridge_matches_joint_solution(solver):
    gen = torch.Generator().manual_seed(45)
    x = torch.randn(41, 13, dtype=torch.float64, generator=gen)
    labels = torch.cat([torch.randint(0, 2, (17,), generator=gen),
                        torch.randint(2, 5, (24,), generator=gen)])
    y = torch.nn.functional.one_hot(labels, 5).double()
    state = AnalyticRidge(13, gamma=0.7, solver=solver)
    state.update(x[:17], y[:17, :2]); state.finalize()
    state.update(x[17:30], y[17:30]); state.update(x[30:], y[30:]); state.finalize()
    joint = torch.linalg.solve(x.T @ x + 0.7 * torch.eye(13, dtype=x.dtype), x.T @ y)
    torch.testing.assert_close(state.weight, joint, rtol=1e-10, atol=1e-10)


def test_compensation_targets_use_final_main_weights_and_plc():
    gen = torch.Generator().manual_seed(42)
    x = torch.randn(31, 6, dtype=torch.float64, generator=gen)
    labels = torch.tensor([0, 1] * 7 + [0] + [2, 3] * 8)
    a = DualStreamAnalytic(6, 11, gamma=0.3, seed=9)
    a.fit_phase(x[:15], labels[:15], 2, 4)
    xm0, xc0 = a.embeddings(x[:15])
    y0 = torch.nn.functional.one_hot(labels[:15], 2).double()
    target0 = y0 - a.main.predict(xm0)
    a.fit_phase(x[15:], labels[15:], 4, 3)
    xm1, xc1 = a.embeddings(x[15:])
    target1 = torch.nn.functional.one_hot(labels[15:], 4).double() - a.main.predict(xm1)
    target1[:, :2] = 0
    features = torch.cat([xc0, xc1])
    targets = torch.cat([torch.nn.functional.pad(target0, (0, 2)), target1])
    expected = torch.linalg.solve(features.T @ features + 0.3 * torch.eye(11, dtype=features.dtype), features.T @ targets)
    torch.testing.assert_close(a.comp.weight, expected, rtol=1e-10, atol=1e-10)


def test_chunk_size_does_not_change_phase_semantics():
    x = torch.randn(40, 7, generator=torch.Generator().manual_seed(8), dtype=torch.float64)
    y = torch.arange(40) % 4
    models = [DualStreamAnalytic(7, 15, seed=1, solver=s) for s in ["stats", "rls"]]
    for model, chunk in zip(models, [40, 3]):
        model.fit_phase(x, y, 4, chunk)
    torch.testing.assert_close(models[0].predict(x), models[1].predict(x), rtol=1e-8, atol=1e-8)


def test_disjoint_class_assumption_is_enforced():
    model = DualStreamAnalytic(3, 5)
    model.fit_phase(torch.randn(4, 3), torch.tensor([0, 1, 0, 1]), 2)
    with pytest.raises(ValueError, match="disjoint"):
        model.fit_phase(torch.randn(2, 3), torch.tensor([0, 2]), 3)
