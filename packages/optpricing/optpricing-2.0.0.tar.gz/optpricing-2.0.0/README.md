# QuantFin

[![CI/CD](https://github.com/diljit22/quantfin/actions/workflows/ci.yml/badge.svg)](https://github.com/diljit22/quantfin/actions/workflows/ci.yml)
[![PyPI Version](https://badge.fury.io/py/quantfin.svg)](https://pypi.org/project/quantfin/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**A Python library for pricing and calibrating financial options.**

## Introduction

Welcome to **QuantFin**, a comprehensive Python toolkit for pricing and calibrating financial derivatives. This library was originally designed for me to learn about the more nuanced methods of quantitative finance and has since grown into a robust framework for analysis.

QuantFin is structured around four core pillars:

- **Atoms**: Fundamental data types (`Option`, `Stock`, `Rate`) that ensure consistency and clarity of inputs across the library.
- **Models**: A broad library ranging from classical Black-Scholes-Merton to advanced stochastic volatility (Heston, SABR) and jump/Lévy processes.
- **Techniques**: Multiple pricing engines—closed-form formulas, FFT, numerical integration, PDE solvers, lattice methods, and Monte Carlo (`numba`-accelerated with variance reduction methods baked in).
- **Workflows**: High-level orchestrators that automate end-to-end tasks like daily calibration and out-of-sample backtesting, all accessible via a CLI or an interactive dashboard.

---

## Quick Start

Get started in minutes using the command-line interface.

```bash
# 1. Install the library with all features, including the dashboard
pip install optPricing[app]

# 2. Download historical data for a ticker (used by some models)
quantfin data download --ticker SPY

# 3. Launch the interactive dashboard to visualize the results
quantfin dashboard

# 4. See a demo of the engine
quantfin demo
```

## Documentation & Links

For a detailed tutorial, full API reference, and more examples, please see the official documentation.

- **Getting Started**: [Installation Guide](installation.md) · [Walkthrough](getting_started.md)  
- **Documentation**: [API Reference](reference/atoms/index.md)
- **Interactive Dashboard**: [Launch the UI](dashboard.md)  
- **About Me**: [LinkedIn]([dashboard.md](https://www.linkedin.com/in/singhdiljit/))  

To explore all available commands, run:

```bash
quantfin --help
```

## Contributing & License

See [CONTRIBUTING](/CONTRIBUTING.md) and [LICENSE](LICENSE).
