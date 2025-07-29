import numpy as np
"""
rk4_num_diff.py

A reusable library for solving ordinary differential equations (ODEs) using the 4th-order Runge-Kutta (RK4) method.

Functions:
----------
- rk4(f, x0, y0, h, n): Numerically solve dy/dx = f(x, y) using RK4.

Example usage is provided at the end of this file.
"""

def rk4(f, x0, y0, h, n):
    """
    Solve the ODE dy/dx = f(x, y) using the 4th-order Runge-Kutta method.

    Parameters
    ----------
    f : function
        Function of two variables f(x, y).
    x0 : float
        Initial value of x.
    y0 : float
        Initial value of y (i.e., y(x0) = y0).
    h : float
        Step size.
    n : int
        Number of steps.

    Returns
    -------
    x_vals : list of floats
        The x-values at each step.
    y_vals : list of floats
        The y-values (approximations of the solution) at each step.

    Example
    -------
    >>> def f(x, y): return x + y
    >>> x, y = rk4(f, 0, 1, 0.1, 10)
    >>> print(x)
    >>> print(y)
    """
    x_vals = [x0]
    y_vals = [y0]

    for i in range(n):
        k1 = h * f(x0, y0)
        k2 = h * f(x0 + h/2, y0 + k1/2)
        k3 = h * f(x0 + h/2, y0 + k2/2)
        k4 = h * f(x0 + h, y0 + k3)

        y0 = y0 + (1/6)*(k1 + 2*k2 + 2*k3 + k4)
        x0 = x0 + h

        x_vals.append(x0)
        y_vals.append(y0)

    return x_vals, y_vals

# Example demonstration
if __name__ == "__main__":
    # Example: Solve dy/dx = x + y, y(0) = 1, step size 0.1, for 10 steps
    def f(x, y):
        return x + y

    x0 = 0
    y0 = 1
    h = 0.1
    n = 10

    x_vals, y_vals = rk4(f, x0, y0, h, n)

    print("x values:", x_vals)
    print("y values:", y_vals)
