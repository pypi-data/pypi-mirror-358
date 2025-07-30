import math
import scipy.stats as st


def _get_z_score(confidence_level: float) -> float:
    """
    Retrieves the Z-score for a given confidence level.

    Args:
        confidence_level: The confidence level as a float (e.g., 0.95 for 95%).

    Returns:
        The Z-score for the given confidence level.
    """
    return st.norm.ppf(1 - (1 - confidence_level) / 2)


def sample_size(
    population_size: int,
    confidence_level: float = 0.95,
    confidence_interval: float = 0.02,
) -> int:
    """
    Calculates the sample size for a finite population using Cochran's formula.

    Args:
        population_size: The total size of the population.
        confidence_level: The desired confidence level (e.g., 0.95 for 95%).
        confidence_interval: The desired confidence interval (margin of error).
                             Default is 0.02 (2%).

    Returns:
        The calculated sample size as an integer.
    """

    # For sample size calculation, we assume the worst-case variance, where p=0.5
    p = 0.5
    z_score = _get_z_score(confidence_level)
    # Calculate sample size for an infinite population
    n_0 = (z_score**2 * p * (1 - p)) / (confidence_interval**2)
    # Adjust sample size for the finite population
    n = n_0 / (1 + (n_0 - 1) / population_size)

    return int(math.ceil(n))
