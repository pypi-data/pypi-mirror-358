import numpy as np
def newton_raphson(f, df, x0, max_iter=100, tol=1e-7, verbose=False):
    """
    Find a root of the equation f(x) = 0 using the Newton-Raphson method.

    Parameters
    ----------
    f : callable
        The function for which the root is sought.
    df : callable
        The derivative of the function f.
    x0 : float
        Initial guess for the root.
    max_iter : int, optional
        Maximum number of iterations (default is 100).
    tol : float, optional
        Tolerance for convergence (default is 1e-7).
    verbose : bool, optional
        If True, prints iteration details.

    Returns
    -------
    root : float or None
        The estimated root, or None if the method fails.
    info : dict
        Dictionary containing convergence information.
    """
    x = x0
    for k in range(1, max_iter + 1):
        fx = f(x)
        dfx = df(x)
        if verbose:
            print(f"{k:8d} {x:14.10f} {fx:14.10f}")
        if dfx == 0:
            if verbose:
                print("Derivative is zero. Method fails.")
            return None, {'converged': False, 'iterations': k, 'reason': 'Zero derivative'}
        x_new = x - fx / dfx
        if abs(x_new - x) <= tol:
            return x_new, {'converged': True, 'iterations': k, 'reason': 'Converged'}
        x = x_new
    if verbose:
        print(f"Maximum number of iterations ({max_iter}) reached. Method fails.")
    return None, {'converged': False, 'iterations': max_iter, 'reason': 'Max iterations'}

# Example demonstration
if __name__ == "__main__":
    # Define the function and its derivative
    f = lambda x: x - np.cos(x)
    df = lambda x: 1 + np.sin(x)

    print("\nThe given equation is: x - cos(x) = 0.")

    # Example initial guess, max iterations, and tolerance
    x0 = 0.5
    max_iter = 20
    tol = 1e-8

    print("\nNewton-Raphson iterations (demonstration):\n")
    print(f"{'k':>8} {'x_k':>14} {'f(x_k)':>14}")
    root, info = newton_raphson(f, df, x0, max_iter, tol, verbose=True)

    if info['converged']:
        print(f"\nRoot found: {root:.10f} (in {info['iterations']} iterations)")
    else:
        print(f"\nMethod failed: {info['reason']} after {info['iterations']} iterations.")

    # Usage in other scripts:
    # from NR import newton_raphson
    # root, info = newton_raphson(f, df, x0)