# Komodo Mlipir Algorithm (KMA)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](./test_documentation.md)
[![Code Style](https://img.shields.io/badge/code%20style-PEP8-orange)](https://www.python.org/dev/peps/pep-0008/)

Implementasi Python dari **Komodo Mlipir Algorithm (KMA)** - algoritma metaheuristik yang terinspirasi dari perilaku komodo dalam mencari makanan. Algoritma ini dikembangkan oleh **Prof. Dr. Suyanto, S.T., M.Sc. (2021)** dan diimplementasikan dalam Python oleh **Pejalan Sunyi (2025)**.

## 📋 Daftar Isi

- [Deskripsi](#-deskripsi)
- [Fitur](#-fitur)
- [Instalasi](#-instalasi)
- [Quick Start](#-quick-start)
- [Penggunaan Detail](#-penggunaan-detail)
- [Parameter](#-parameter)
- [Contoh Implementasi](#-contoh-implementasi)
- [Benchmarking](#-benchmarking)
- [Testing](#-testing)
- [Struktur Proyek](#-struktur-proyek)
- [Contributing](#-contributing)
- [Citation](#-citation)
- [License](#-license)

## 📖 Deskripsi

Komodo Mlipir Algorithm (KMA) adalah algoritma optimasi metaheuristik yang mensimulasikan perilaku komodo dalam mencari makanan. Algoritma ini membagi populasi menjadi tiga kategori:

1. **Jantan Besar (Big Males)**: Individu dominan dengan fitness terbaik
2. **Betina (Female)**: Individu yang melakukan reproduksi (mating atau parthenogenesis)
3. **Jantan Kecil (Small Males)**: Individu yang mengikuti jantan besar (mlipir behavior)

### Keunggulan KMA:
- 🎯 Efektif untuk optimasi fungsi kompleks
- 🔄 Adaptive population schema untuk efisiensi
- 🧬 Dual reproduction strategy (sexual & asexual)
- 📊 Konvergensi yang baik untuk berbagai jenis problem

## ✨ Fitur

- ✅ **Clean Code** dengan standar PEP8
- ✅ **Type Hints** untuk better IDE support
- ✅ **Comprehensive Testing** dengan pytest
- ✅ **Adaptive Population** untuk efisiensi komputasi
- ✅ **Multiple Reproduction Strategies**
- ✅ **Customizable Parameters**
- ✅ **History Tracking** untuk analisis konvergensi
- ✅ **Verbose Mode** untuk monitoring
- ✅ **Reproducible Results** dengan random seed

## 🚀 Instalasi

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Install dari Source

```bash
# Clone repository
git clone https://github.com/yourusername/komodo-mlipir-algorithm.git
cd komodo-mlipir-algorithm

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```txt
numpy>=1.20.0
matplotlib>=3.3.0  # Optional, untuk visualisasi
```

### Development Dependencies

```txt
pytest>=6.0.0
pytest-cov>=2.12.0
pytest-mock>=3.6.0
```

## 🎯 Quick Start

```python
from optimizer.KomodoMlipirAlgorithm import KomodoMlipirAlgorithm

# Define objective function (maximize)
def sphere_function(x):
    return -sum(xi**2 for xi in x)

# Initialize KMA
kma = KomodoMlipirAlgorithm(
    population_size=30,
    fitness_function=sphere_function,
    search_space=[(-5, 5), (-5, 5)],
    max_iterations=100
)

# Run optimization
kma.fit(verbose=True)

# Get results
results = kma.get_results()
print(f"Best solution: {results['best_solution']}")
print(f"Best fitness: {results['best_fitness']}")
```

## 📚 Penggunaan Detail

### 1. Basic Usage

```python
from optimizer import KMA  # Using alias

# Define your optimization problem
def objective_function(x):
    # Maximize this function
    return -(x[0]**2 + x[1]**2)  # Example: minimize x^2 + y^2

# Setup algorithm
optimizer = KMA(
    population_size=50,
    male_proportion=0.4,
    mlipir_rate=0.5,
    fitness_function=objective_function,
    search_space=[(-10, 10), (-10, 10)],
    max_iterations=200,
    random_state=42
)

# Run optimization
optimizer.fit(verbose=False)

# Get results
solution = optimizer.get_results()
```

### 2. Advanced Usage dengan Adaptive Schema

```python
# Enable adaptive population sizing
optimizer = KMA(
    population_size=30,
    fitness_function=your_function,
    search_space=your_bounds,
    max_iterations=500,
    parthenogenesis_radius=0.15,
    stop_criteria=0.001,
    stop=True  # Enable early stopping
)

# Run with adaptive schema
optimizer.fit(
    adaptive_schema=True,
    min_population=20,
    max_population=100,
    verbose=True
)
```

### 3. Constrained Optimization

```python
def constrained_objective(x):
    # Objective function with penalty
    objective = x[0] + x[1]
    
    # Constraint: x^2 + y^2 <= 1
    constraint_violation = max(0, x[0]**2 + x[1]**2 - 1)
    penalty = 1000 * constraint_violation
    
    return objective - penalty

optimizer = KMA(
    fitness_function=constrained_objective,
    search_space=[(-2, 2), (-2, 2)]
)
```

### 4. Multi-dimensional Optimization

```python
# 10-dimensional optimization
dimensions = 10

def rosenbrock(x):
    # Rosenbrock function (minimize)
    result = 0
    for i in range(len(x)-1):
        result += 100*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2
    return -result  # Negative because KMA maximizes

optimizer = KMA(
    population_size=100,
    fitness_function=rosenbrock,
    search_space=[(-5, 5)] * dimensions,
    max_iterations=1000
)
```

## ⚙️ Parameter

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `population_size` | int | 5 | Jumlah individu dalam populasi (minimum 5) |
| `male_proportion` | float | 0.5 | Proporsi jantan besar (0.1 - 1.0) |
| `mlipir_rate` | float | 0.5 | Tingkat mlipir untuk jantan kecil (0 - 1) |
| `fitness_function` | Callable | None | Fungsi objektif yang akan dimaksimalkan |
| `search_space` | List[Tuple] | None | Batasan untuk setiap dimensi [(min, max), ...] |
| `max_iterations` | int | 1000 | Jumlah iterasi maksimum |
| `random_state` | int | 42 | Seed untuk reproduktibilitas |
| `parthenogenesis_radius` | float | 0.1 | Radius untuk reproduksi aseksual |
| `stop_criteria` | float | 0.01 | Kriteria konvergensi (std deviation) |
| `stop` | bool | False | Enable early stopping berdasarkan konvergensi |

### Fit Method Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `adaptive_schema` | bool | False | Aktifkan skema adaptif populasi |
| `min_population` | int | 20 | Ukuran populasi minimum (untuk adaptive) |
| `max_population` | int | 100 | Ukuran populasi maksimum (untuk adaptive) |
| `verbose` | bool | True | Tampilkan progress selama optimasi |

## 💡 Contoh Implementasi

### 1. Optimasi Fungsi Sphere

```python
import numpy as np
from optimizer import KMA
import matplotlib.pyplot as plt

# Sphere function
def sphere(x):
    return -np.sum(x**2)

# Setup
kma = KMA(
    population_size=30,
    fitness_function=sphere,
    search_space=[(-5, 5), (-5, 5)],
    max_iterations=100
)

# Optimize
kma.fit(verbose=False)
results = kma.get_results()

# Plot convergence
plt.plot(results['history']['best_fitness'])
plt.xlabel('Iteration')
plt.ylabel('Best Fitness')
plt.title('KMA Convergence on Sphere Function')
plt.show()

print(f"Optimal solution: {results['best_solution']}")
print(f"Optimal value: {results['best_fitness']}")
```

### 2. Optimasi Fungsi Rastrigin

```python
# Rastrigin function (multimodal)
def rastrigin(x):
    n = len(x)
    return -(10*n + sum(xi**2 - 10*np.cos(2*np.pi*xi) for xi in x))

kma = KMA(
    population_size=100,
    male_proportion=0.3,
    mlipir_rate=0.7,
    fitness_function=rastrigin,
    search_space=[(-5.12, 5.12)] * 5,
    max_iterations=500,
    parthenogenesis_radius=0.2
)

kma.fit(adaptive_schema=True)
```

### 3. Optimasi Portfolio

```python
# Portfolio optimization example
def portfolio_objective(weights):
    # Expected returns
    returns = np.array([0.12, 0.10, 0.15, 0.08])
    # Covariance matrix
    cov_matrix = np.array([
        [0.10, 0.02, 0.04, 0.01],
        [0.02, 0.08, 0.03, 0.02],
        [0.04, 0.03, 0.12, 0.05],
        [0.01, 0.02, 0.05, 0.06]
    ])
    
    # Normalize weights
    weights = weights / np.sum(weights)
    
    # Calculate portfolio return and risk
    portfolio_return = np.dot(weights, returns)
    portfolio_risk = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
    
    # Sharpe ratio (maximize)
    sharpe_ratio = (portfolio_return - 0.02) / portfolio_risk
    
    return sharpe_ratio

# Optimize portfolio
kma = KMA(
    population_size=50,
    fitness_function=portfolio_objective,
    search_space=[(0, 1)] * 4,  # 4 assets
    max_iterations=200
)

kma.fit()
optimal_weights = kma.get_results()['best_solution']
optimal_weights = optimal_weights / np.sum(optimal_weights)
print(f"Optimal portfolio weights: {optimal_weights}")
```

## 📊 Benchmarking

Jalankan benchmark functions dengan:

```python
from fungsi_benchmark import run_benchmarks

# Run standard benchmarks
results = run_benchmarks(
    functions=['sphere', 'rosenbrock', 'rastrigin', 'ackley'],
    dimensions=[2, 5, 10],
    n_runs=30
)

# Display results
for func, dims_results in results.items():
    for dim, stats in dims_results.items():
        print(f"{func} ({dim}D): Mean = {stats['mean']:.6f}, Std = {stats['std']:.6f}")
```

## 🧪 Testing

### Run All Tests

```bash
# Basic test run
pytest unit_test.py -v

# With coverage report
pytest unit_test.py --cov=optimizer --cov-report=html

# Using test runner
python run_tests.py --coverage
```

### Run Specific Tests

```bash
# Run only initialization tests
pytest unit_test.py::TestKomodoMlipirAlgorithmInitialization -v

# Run without slow tests
pytest unit_test.py -m "not slow"

# Run with specific pattern
pytest unit_test.py -k "test_sphere" -v
```

## 📁 Struktur Proyek

```
komodo_mlipir_algorithm/
│
├── optimizer/                    # Package utama
│   ├── __init__.py
│   └── KomodoMlipirAlgorithm.py # Implementasi KMA
│
├── fungsi_benchmark.py          # Benchmark functions
├── coba_kma.ipynb              # Jupyter notebook examples
├── unit_test.py                # Unit tests
├── run_tests.py                # Test runner script
├── test_documentation.md       # Testing documentation
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## 🤝 Contributing

Kontribusi sangat diterima! Silakan ikuti langkah berikut:

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP8 style guide
- Add unit tests for new features
- Update documentation
- Ensure all tests pass before PR

## 📝 Citation

Jika Anda menggunakan Komodo Mlipir Algorithm dalam penelitian, silakan cite:

```bibtex
@article{suyanto2021komodo,
  title={Komodo Mlipir Algorithm: A Novel Metaheuristic Inspired by Komodo Dragons},
  author={Suyanto, S.T., M.Sc., Prof. Dr.},
  journal={Journal of Computational Intelligence},
  year={2021},
  publisher={Publisher Name}
}

@software{kma_python2025,
  title={Python Implementation of Komodo Mlipir Algorithm},
  author={Pejalan Sunyi},
  year={2025},
  url={https://github.com/khalifardy/komodo_mlipir_algorithm}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by Pejalan Sunyi**

*For questions and support, please open an issue in the GitHub repository.*