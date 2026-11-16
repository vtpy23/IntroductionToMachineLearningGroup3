import pytest
from src.datasets.cifar100 import class_order, phase_boundaries


def test_cifar_protocol_covers_all_classes():
    assert phase_boundaries(50, 5) == [50, 60, 70, 80, 90, 100]
    assert len(phase_boundaries(50, 50)) == 51
    assert sorted(class_order(0).tolist()) == list(range(100))
    with pytest.raises(ValueError):
        phase_boundaries(50, 3)
