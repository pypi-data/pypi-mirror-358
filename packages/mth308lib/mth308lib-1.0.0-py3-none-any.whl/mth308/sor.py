import numpy as np
def sor_solver(A, b, x0, w, max_iter):
    """
    Solve the linear system Ax = b using the Successive Over-Relaxation (SOR) method.

    Parameters
    ----------
    A : ndarray
        Coefficient matrix (n x n).
    b : ndarray
        Right-hand side vector (n,).
    x0 : ndarray
        Initial guess vector (n,).
    w : float
        SOR relaxation parameter (0 < w < 2).
    max_iter : int
        Maximum number of iterations.

    Returns
    -------
    X : ndarray
        Array of solution vectors at each iteration (n x (max_iter+1)).

    Raises
    ------
    ValueError
        If w is not in (0,2) or if any diagonal element of A is zero.

    Example
    -------
    >>> import numpy as np
    >>> from SOR import sor_solver
    >>> A = np.array([[4.0, 1.0, 1.0],
    ...               [1.0, 3.0, 1.0],
    ...               [1.0, 1.0, 5.0]])
    >>> b = np.array([7.0, 8.0, 11.0])
    >>> x0 = np.zeros(3)
    >>> w = 1.25
    >>> max_iter = 10
    >>> X = sor_solver(A, b, x0, w, max_iter)
    >>> print(X)
    """
    n = len(b)
    y = np.zeros(n)
    X = np.zeros((n, max_iter+1))
    x = x0.copy()
    X[:, 0] = x

    if not (0 < w < 2):
        raise ValueError("SOR parameter w must be in (0,2) for convergence.")

    if np.any(np.diag(A) == 0):
        raise ValueError("SOR iteration cannot be used. Diagonal elements of A must be nonzero.")

    for k in range(1, max_iter+1):
        for i in range(n):
            u = sum(A[i, j]*y[j] for j in range(i))
            z = sum(A[i, j]*x[j] for j in range(i+1, n))
            y[i] = (1-w)*x[i] + (w/A[i,i])*(b[i] - u - z)
        x = y.copy()
        X[:, k] = x

    return X

if __name__ == "__main__":
    # Example demonstration
    # System:
    # 4x + y + z = 7
    # x + 3y + z = 8
    # x + y + 5z = 11
    A = np.array([[4.0, 1.0, 1.0],
                  [1.0, 3.0, 1.0],
                  [1.0, 1.0, 5.0]])
    b = np.array([7.0, 8.0, 11.0])
    x0 = np.zeros(3)
    w = 1.25
    max_iter = 10

    try:
        X = sor_solver(A, b, x0, w, max_iter)
        print(f"\nSOR iterations (columnwise, each column is an iteration):\n")
        np.set_printoptions(precision=6, suppress=True)
        print(np.array2string(X, formatter={'float_kind':lambda x: "%10.6f" % x}))
    except ValueError as e:
        print(f"Error: {e}")