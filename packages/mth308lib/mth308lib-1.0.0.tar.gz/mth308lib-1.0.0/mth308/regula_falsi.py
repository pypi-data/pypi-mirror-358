import numpy as np
def regula_falsi(f, a, b, N=100, tol=1e-9, verbose=False):
    """
    Find a root of the equation f(x) = 0 using the Regula-Falsi (False Position) method.

    Parameters
    ----------
    f : callable
        The function for which the root is to be found.
    a : float
        Left endpoint of the initial interval.
    b : float
        Right endpoint of the initial interval.
    N : int, optional
        Maximum number of iterations (default is 100).
    tol : float, optional
        Tolerance for stopping criterion (default is 1e-9).
    verbose : bool, optional
        If True, prints iteration details.

    Returns
    -------
    root : float
        The estimated root.
    converged : bool
        True if the method converged, False otherwise.
    iterations : int
        Number of iterations performed.

    Raises
    ------
    ValueError
        If f(a) and f(b) do not have opposite signs.
    """
    y_0 = f(a)
    y_1 = f(b)
    if y_0 == 0:
        return a, True, 0
    if y_1 == 0:
        return b, True, 0
    if y_0 * y_1 > 0:
        raise ValueError("f(a) and f(b) must have opposite signs.")

    if verbose:
        print(f"{'k':>10}{'a_k':>15}{'b_k':>15}{'x_k':>15}{'f(x_k)':>15}")

    for k in range(1, N + 1):
        x = a - (y_0 * (b - a)) / (y_1 - y_0)
        y = f(x)
        if verbose:
            print(f"{k:10d}{a:15.9f}{b:15.9f}{x:15.9f}{y:15.9f}")
        if abs(y) < tol:
            return x, True, k
        if y_0 * y > 0:
            a = x
            y_0 = y
        else:
            b = x
            y_1 = y
    return x, False, N

# Example demonstration
if __name__ == "__main__":
    def f(x):
        return np.sqrt(x) - np.cos(x)

    print("\nThe given equation is: sqrt(x) - cos(x) = 0.\n")
    # Example interval [0.5, 1.0]
    a = 0.5
    b = 1.0
    N = 20

    try:
        root, converged, iterations = regula_falsi(f, a, b, N, verbose=True)
        if converged:
            print(f"\nA root of the given equation is approximately {root:.9f} (found in {iterations} iterations).")
        else:
            print(f"\nMaximum number of iterations reached. Approximate root: {root:.9f}")
    except ValueError as e:
        print(f"Error: {e}")
