
import numpy as np
def secant_method(f, x0, x1, tol=1e-8, max_iter=100):
    """
    Find a root of the equation f(x) = 0 using the Secant method.

    Parameters
    ----------
    f : callable
        The function for which to find the root.
    x0 : float
        First initial approximation.
    x1 : float
        Second initial approximation.
    tol : float, optional
        The tolerance for stopping criterion (default is 1e-8).
    max_iter : int, optional
        The maximum number of iterations (default is 100).

    Returns
    -------
    root : float or None
        The root found or None if the method fails.
    history : list of tuples
        List of (iteration, x_k, f(x_k)) for each iteration.
    message : str
        Description of the result.
    """
    y0 = f(x0)
    y1 = f(x1)
    history = [(1, x0, y0), (2, x1, y1)]

    if y0 == 0:
        return x0, history, f"A root of the given equation is {x0}."
    if y1 == 0:
        return x1, history, f"A root of the given equation is {x1}."
    if y0 == y1:
        return None, history, "Secant method cannot locate any root for the given equation (f(x0) == f(x1))."

    for k in range(3, max_iter + 3):
        if y1 - y0 == 0:
            return None, history, "Division by zero encountered in Secant method."
        x = x1 - (y1 * (x1 - x0)) / (y1 - y0)
        y = f(x)
        history.append((k, x, y))
        if y == 0:
            return x, history, f"A root of the given equation is {x}."
        if abs(x - x1) <= tol:
            return x, history, f"An approximate root (with tolerance {tol}) of the given equation is {x}."
        x0, y0 = x1, y1
        x1, y1 = x, y

    return None, history, f"Maximum number of iterations ({max_iter}) reached. The method failed."

# Example demonstration
if __name__ == "__main__":
    # Define the function
    def f(x):
        return x - np.cos(x)

    print("\nThe given equation is: x - cos(x) = 0.")

    # Example initial guesses, tolerance, and max iterations
    x0 = 0.5
    x1 = 0.7
    tol = 1e-8
    max_iter = 20

    root, history, message = secant_method(f, x0, x1, tol, max_iter)

    print("\nThe Secant iterations are given as:\n")
    print("    k           x_k           f(x_k)")
    for k, xk, fxk in history:
        print(f"{k:4d}  {xk:14.10f}  {fxk:14.10f}")
    print("\n" + message)