# mth308lib

A Python library implementing core numerical methods for MTH308, including root-finding, linear systems, interpolation, and ODE solvers.

## Features

- **Root Finding:**  
  - Bisection method  
  - Regula Falsi  
  - Modified Regula Falsi  
  - Newton-Raphson  
  - Secant method  

- **Linear Systems:**  
  - Gaussian Elimination  
  - Gauss-Seidel  
  - Jacobi  
  - SOR (Successive Over-Relaxation)  
  - LU Decomposition (Doolittle & Crout)  
  - Power Method (dominant eigenvalue/vector)  

- **Interpolation:**  
  - Divided Difference Table  
  - Newton Divided Difference  

- **Numerical Integration:**  
  - Trapezoidal Rule  
  - Simpson's 1/3 Rule  

- **ODE Solvers:**  
  - Euler's Method  
  - Runge-Kutta 4th Order (RK4)  

## Installation

From the root directory, run:

```bash
pip install .
```

## Usage

Import any function directly from the package:

```python
from mth308 import (
    bisection_method, regula_falsi, modified_regula_falsi, newton_raphson, secant_method,
    gaussian_elimination, gauss_seidel, jacobi, sor_solver, lu_doolittle, lu_crout, power_method,
    divided_difference_table, newton_divided_diff,
    trapezoidal_rule, simpsons_one_third,
    euler_method, rk4
)

# Example: Find root of x^2 - 2 = 0 using bisection
root, iterations, converged = bisection_method(lambda x: x**2 - 2, 0, 2)
print("Root:", root)
```

## Testing

Run all tests with:

```bash
python -m unittest discover tests
```

## File Structure

```
mth308lib/
│
├── mth308/
│   ├── __init__.py
│   ├── bisection.py
│   ├── ctr_num_int.py
│   ├── divided_diff.py
│   ├── euler.py
│   ├── gauss_seidel.py
│   ├── gaussian_elim.py
│   ├── jacobi.py
│   ├── lu.py
│   ├── mrf.py
│   ├── newton_raphson.py
│   ├── power_method.py
│   ├── regula_falsi.py
│   ├── rk4.py
│   ├── secant.py
│   ├── simpsons.py
│   └── sor.py
│
├── tests/
│   └── test_all.py
│
├── setup.py
└── README.md
```

## License

IITK 