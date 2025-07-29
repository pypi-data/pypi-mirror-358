"""
simpsons.py

A reusable library for numerical integration using Simpson's 1/3 Rule.

Provides:
    - simpsons_one_third: Compute the definite integral of a function using Simpson's 1/3 Rule.

Example:
    >>> from simpsons import simpsons_one_third
    >>> result = simpsons_one_third(lambda x: x**2, 0, 2, N=100)
    >>> print(result)
"""

def simpsons_one_third(f, a, b, N=None, h=None):
    """
    Approximate the definite integral of f(x) from a to b using Simpson's 1/3 Rule.

    Either N (number of sub-intervals, must be even) or h (step size) must be provided.

    Parameters
    ----------
    f : callable
        The function f(x) to integrate.
    a : float
        The lower limit of integration.
    b : float
        The upper limit of integration.
    N : int, optional
        Even number of sub-intervals. N must be even.
    h : float, optional
        Step size. If specified, N is computed as N = (b - a) / h.

    Returns
    -------
    float
        Approximation of the definite integral of f from a to b.

    Raises
    ------
    ValueError
        If neither N nor h is provided or if N is not even.

    Example
    -------
    >>> simpsons_one_third(lambda x: x**2, 0, 2, N=100)
    2.6666666666666665
    """
    # Determine N and h
    if N is None and h is None:
        raise ValueError("You must provide either N or h.")
    if N is None:
        N = int((b - a) / h)
    if h is None:
        h = (b - a) / N
    N = int(N)
    if N % 2 != 0:
        raise ValueError("N must be even for Simpson's 1/3 Rule.")

    # Step-1: Compute h
    h = (b - a) / N

    # Step-2: Initialize T_h
    T_h = f(a) + f(b)

    # Step-3: Even index sum (i = 1 to N-1 using 2i)
    for i in range(1, N//2):
        T_h += 2 * f(a + 2*i*h)

    # Step-4: Odd index sum (i = 1 to N using 2i-1)
    for i in range(1, N//2 + 1):
        T_h += 4 * f(a + (2*i - 1) * h)

    # Step-5: Multiply by h/3
    T_h *= h/3

    return T_h

# Example demonstration
if __name__ == "__main__":
    import math

    def example_function(x):
        """Example function: f(x) = x^2"""
        return x ** 2

    a, b = 0, 2
    exact = 8 / 3

    print("Demonstration of simpsons_one_third:")
    print(f"Integrating f(x) = x^2 from {a} to {b}")
    approx = simpsons_one_third(example_function, a, b, N=100)
    print(f"Simpson's Rule Approximation: {approx}")
    print(f"Exact Value: {exact}")
    print(f"Error: {abs(approx - exact)}")
