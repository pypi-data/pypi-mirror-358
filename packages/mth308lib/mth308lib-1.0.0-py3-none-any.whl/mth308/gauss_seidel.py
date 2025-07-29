import numpy as np
def gauss_seidel(A, b, x0=None, max_iter=25, tol=1e-10):
    """
    Solve the linear system Ax = b using the Gauss-Seidel iterative method.

    Parameters
    ----------
    A : array_like, shape (n, n)
        Coefficient matrix.
    b : array_like, shape (n,)
        Right-hand side vector.
    x0 : array_like, shape (n,), optional
        Initial guess for the solution. If None, uses zeros.
    max_iter : int, optional
        Maximum number of iterations (default: 25).
    tol : float, optional
        Convergence tolerance (default: 1e-10).

    Returns
    -------
    X : ndarray, shape (n, k+1)
        Matrix containing the solution at each iteration (column-wise).
    converged : bool
        True if the method converged within max_iter, False otherwise.

    Raises
    ------
    ValueError
        If input dimensions do not match or A has zero diagonal elements.

    Example
    -------
    >>> A = [[4, 1, 1], [1, 3, 1], [1, 1, 5]]
    >>> b = [7, 8, 12]
    >>> X, converged = gauss_seidel(A, b, max_iter=10)
    >>> print(X)
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = A.shape[0]

    if A.shape != (n, n):
        raise ValueError("A must be a square matrix.")
    if b.shape[0] != n:
        raise ValueError("b must have length n.")
    if np.any(np.diag(A) == 0):
        raise ValueError("Zero found on diagonal of coefficient matrix.")

    if x0 is None:
        x = np.zeros(n)
    else:
        x = np.array(x0, dtype=float)
        if x.shape[0] != n:
            raise ValueError("x0 must have length n.")

    X = np.zeros((n, max_iter+1))
    X[:, 0] = x

    for k in range(max_iter):
        x_old = x.copy()
        for i in range(n):
            z = np.dot(A[i, i+1:], x[i+1:])
            u = np.dot(A[i, :i], x[:i])
            x[i] = (1 / A[i, i]) * (b[i] - u - z)
        X[:, k+1] = x
        if np.linalg.norm(x - x_old, ord=np.inf) < tol:
            return X[:, :k+2], True

    return X, False

# Example demonstration
if __name__ == "__main__":
    # Example system:
    # 4x + y + z = 7
    # x + 3y + z = 8
    # x + y + 5z = 12

    A = [
        [4, 1, 1],
        [1, 3, 1],
        [1, 1, 5]
    ]
    b = [7, 8, 12]
    max_iter = 10

    X, converged = gauss_seidel(A, b, max_iter=max_iter)
    if converged:
        print(f"\nConverged in {X.shape[1]-1} Gauss-Seidel iterations (column-wise):\n")
        np.set_printoptions(precision=6, suppress=True)
        print(X)
    else:
        print("Gauss-Seidel iteration did not converge within the maximum number of iterations.")