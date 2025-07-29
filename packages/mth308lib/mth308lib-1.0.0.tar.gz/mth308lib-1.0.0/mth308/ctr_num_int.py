"""
numerical_integration.py

A small library for numerical integration using the trapezoidal rule.

Provides:
    - trapezoidal_rule: Compute the definite integral of a function using the trapezoidal rule.

Example:
    >>> from numerical_integration import trapezoidal_rule
    >>> result = trapezoidal_rule(lambda x: x**2, 0, 2, N=100)
    >>> print(result)
"""

def trapezoidal_rule(f, a, b, N=None, h=None):
    """
    Approximate the definite integral of f(x) from a to b using the trapezoidal rule.

    Parameters
    ----------
    f : callable
        The function f(x) to integrate. Should accept a float and return a float.
    a : float
        The lower limit of the integration.
    b : float
        The upper limit of the integration.
    N : int, optional
        Number of subdivisions of the interval [a, b].
    h : float, optional
        Step size. If specified, N is calculated as N = (b - a) / h.

    Returns
    -------
    float
        Approximation of the definite integral of f from a to b.

    Raises
    ------
    ValueError
        If neither N nor h is provided, or if N is not an integer.

    Example
    -------
    >>> trapezoidal_rule(lambda x: x**2, 0, 2, N=100)
    2.66672
    """
    # Determine N and h
    if N is None and h is None:
        raise ValueError("You must provide either N or h.")
    if N is None:
        N = int((b - a) / h)
    if h is None:
        h = (b - a) / N
    N = int(N)

    # Compute T_h
    T_h = 0.5 * (f(a) + f(b))
    for i in range(1, N):
        T_h += f(a + i*h)

    return h * T_h


if __name__ == "__main__":
    import math

    # Example 1: Integrate f(x) = x^2 on [0, 2]
    print("Example 1: Integrate f(x) = x^2 on [0, 2]")
    approx = trapezoidal_rule(lambda x: x**2, 0, 2, N=100)
    print(f"Approximation: {approx}")
    print(f"Exact value: {8/3}")
    print(f"Error: {abs(approx - 8/3)}\n")

    # Example 2: Integrate f(x) = sin(x) on [0, pi]
    print("Example 2: Integrate f(x) = sin(x) on [0, pi]")
    approx2 = trapezoidal_rule(math.sin, 0, math.pi, N=100)
    print(f"Approximation: {approx2}")
    print(f"Exact value: {2.0}")
    print(f"Error: {abs(approx2 - 2.0)}")
