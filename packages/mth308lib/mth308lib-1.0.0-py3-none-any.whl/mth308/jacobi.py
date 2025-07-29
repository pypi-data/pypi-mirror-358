import numpy as np
def jacobi(A, b, x0=None, max_iter=100):
    """
    Solve the linear system Ax = b using the Gauss-Jacobi iterative method.

    Parameters
    ----------
    A : numpy.ndarray
        Coefficient matrix (n x n).
    b : numpy.ndarray
        Right-hand side vector (n,).
    x0 : numpy.ndarray, optional
        Initial guess vector (n,). If None, uses zeros.
    max_iter : int, optional
        Maximum number of iterations (default: 100).

    Returns
    -------
    X : numpy.ndarray
        Array of solution vectors at each iteration (n x (max_iter+1)).

    Raises
    ------
    ValueError
        If any diagonal element of A is zero.

    Example
    -------
    >>> import numpy as np
    >>> from jaccobi import jacobi
    >>> A = np.array([[10.0, 2.0, 1.0], [1.0, 5.0, 1.0], [2.0, 3.0, 10.0]])
    >>> b = np.array([9.0, -1.0, 27.0])
    >>> x0 = np.zeros(3)
    >>> X = jacobi(A, b, x0, max_iter=10)
    >>> print(X)
    """
    n = A.shape[0]
    if np.any(np.diag(A) == 0):
        raise ValueError("Gauss-Jacobi iteration cannot be used. Zero diagonal element found. May need to swap equations.")

    if x0 is None:
        x = np.zeros(n)
    else:
        x = x0.copy()
    y = np.zeros(n)
    X = np.zeros((n, max_iter + 1))
    X[:, 0] = x

    for k in range(max_iter):
        for i in range(n):
            z = 0
            for j in range(n):
                if j != i:
                    z += A[i, j] * x[j]
            y[i] = (1 / A[i, i]) * (b[i] - z)
        x = y.copy()
        X[:, k + 1] = x

    return X

# Example demonstration
if __name__ == "__main__":
    # Example system:
    # 10x + 2y + 1z = 9
    # 1x + 5y + 1z = -1
    # 2x + 3y + 10z = 27

    A = np.array([
        [10.0, 2.0, 1.0],
        [1.0, 5.0, 1.0],
        [2.0, 3.0, 10.0]
    ])
    b = np.array([9.0, -1.0, 27.0])
    x0 = np.zeros(3)
    max_iter = 10

    X = jacobi(A, b, x0, max_iter)
    np.set_printoptions(precision=6, suppress=True)
    print(f"\n{max_iter} Gauss-Jacobi iterations (columnwise):\n")
    print(X)