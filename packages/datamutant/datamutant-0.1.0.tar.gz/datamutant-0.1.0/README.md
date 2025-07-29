# DataMutant

A Python library for advanced data analysis algorithms with a modular architecture that supports multiple specialized tools.

## 🧬 What is DataMutant?

DataMutant is designed to be a comprehensive toolkit for data scientists and researchers, providing efficient implementations of advanced algorithms for data analysis, pattern recognition, and machine learning. Each algorithm is organized as a separate module with its own examples and documentation.

## 🚀 Features

* **Modular Architecture**: Each algorithm is self-contained with examples and detailed documentation
* **High Performance**: Optimized implementations using PyTorch
* **Comprehensive Testing**: Full test coverage for all algorithms
* **Type Safety**: Complete type hints and validation
* **Extensible Design**: Easy to add new algorithms

## 📦 Available Algorithms

### 1. Sublinear Monotonicity Score
- **Location**: `datamutant.monotonicity_score`
- **Purpose**: Measure how close sequences are to being monotonically increasing
- **Complexity**: O((1/ε) log n) - sublinear sampling algorithm
- **Documentation**: [View detailed docs](./datamutant/monotonicity_score/README.md)

## 📚 Installation

```bash
pip install datamutant
```

For development:
```bash
pip install datamutant[dev]
```

## 🔥 Quick Start

```python
import torch
from datamutant.monotonicity_score import sublinear_monotonicity_score

# Analyze sequence monotonicity
sequence = torch.tensor([1.0, 2.0, 3.0, 2.5, 4.0])
score = sublinear_monotonicity_score(sequence)
print(f"Monotonicity score: {score}")  # ~0.8
```

## 🏗️ Project Structure

```
datamutant/
├── datamutant/                          # Main package
│   ├── __init__.py                      # Package exports
│   └── monotonicity_score/              # Monotonicity algorithm
│       ├── __init__.py                  # Module exports
│       ├── sublinear.py                 # Core algorithm implementation
│       ├── models.py                    # Neural network models
│       ├── README.md                    # Algorithm documentation
│       └── examples/                    # Usage examples
│           ├── basic_usage.py
│           └── model_training.py
├── tests/                               # Comprehensive tests
│   └── monotonicity_score/
│       ├── test_core.py
│       └── test_models.py
├── setup.py                             # Package setup
├── pyproject.toml                       # Modern packaging
└── README.md                            # This file
```

## 📖 Algorithm Documentation

Each algorithm has its own detailed documentation:

- **Sublinear Monotonicity Score**: [./datamutant/monotonicity_score/README.md](./datamutant/monotonicity_score/README.md)

## 🎯 Examples

Each algorithm includes comprehensive examples in its own directory:

```bash
# Run monotonicity score examples
python -m datamutant.monotonicity_score.examples.basic_usage
python -m datamutant.monotonicity_score.examples.model_training
```

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run tests for specific algorithms:
```bash
pytest tests/monotonicity_score/
```

## 🤝 Contributing

1. Each new algorithm should be in its own module under `datamutant/`
2. Include comprehensive documentation in the algorithm's README.md
3. Provide examples in the `examples/` subdirectory
4. Add tests in the corresponding `tests/` directory
5. Update this main README with a short description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 