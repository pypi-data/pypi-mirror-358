import pytest
from sksampling import _get_z_score, sample_size


def test_sample_size_basic():
    """
    Tests the sample_size function with a few known sets of inputs and
    expected outputs.
    """
    error_margin = 1
    # Test case from original print statement
    assert sample_size(100_000, 0.95, 0.02) == pytest.approx(2345, abs=error_margin)
    # Test with a smaller population
    assert sample_size(500, 0.95, 0.05) == pytest.approx(218, abs=error_margin)
    # Test with higher confidence and smaller interval
    assert sample_size(10_000, 0.99, 0.01) == pytest.approx(6239, abs=error_margin)
    # Test with a very large population, approaching the infinite case
    assert sample_size(1_000_000, 0.95, 0.05) == pytest.approx(385, abs=error_margin)


def test_z_score():
    """
    Tests the _get_z_score helper function with common confidence levels.
    """
    error_margin = 1e-2
    # Z-score for 90% confidence level should be approximately 1.645
    assert _get_z_score(0.90) == pytest.approx(1.645, abs=error_margin)
    # Z-score for 95% confidence level should be approximately 1.96
    assert _get_z_score(0.95) == pytest.approx(1.96, abs=error_margin)
    # Z-score for 99% confidence level should be approximately 2.58
    assert _get_z_score(0.99) == pytest.approx(2.58, abs=error_margin)
