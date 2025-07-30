# 🧪 Scikit-Sampling

[![GitHub](https://img.shields.io/static/v1?label=Code&message=GitHub&color=blue&style=flat-square)](https://github.com/leomaurodesenv/scikit-sampling)
[![MIT license](https://img.shields.io/static/v1?label=License&message=MIT&color=blue&style=flat-square)](LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/leomaurodesenv/scikit-sampling/continuous-integration.yml?label=Build&style=flat-square)](https://github.com/leomaurodesenv/scikit-sampling/actions/workflows/continuous-integration.yml)


Scikit-Sampling (or `sksampling`) is a Python library for dataset sampling techniques. It provides a unified API for common sampling strategies, making it easy to integrate into your data science and machine learning workflows.

## Installation

You can install `sksampling` using pip:

```bash
pip install scikit-sampling
```

## Features

`sksampling` offers a range of sampling methods, including:

- `sample_size`: Computes the ideal sample size based confidence level and interval.

## Usage

`sksampling` follows the `scikit-learn` API, making it intuitive to use.

```python
from sksampling import sample_size

# Example usage
population_size: int = 100_000
confidence_level: float = 0.95
confidence_interval: float = 0.02
sample_size(population_size, confidence_level, confidence_interval) # approx 2345
```
