# LU Decomposition using Doolittle's method

import numpy as np

def lu_doolittle(a):
    """
    Perform LU Decomposition of a square matrix using Doolittle's method.

    Parameters
    ----------
    a : numpy.ndarray
        The square matrix to decompose (shape: n x n).

    Returns
    -------
    L : numpy.ndarray
        Lower triangular matrix with unit diagonal (shape: n x n).
    U : numpy.ndarray
        Upper triangular matrix (shape: n x n).

    Raises
    ------
    ValueError
        If the matrix is singular or factorization is not possible.
    """
    n = a.shape[0]
    L = np.eye(n)
    U = np.zeros((n, n))
    if a[0, 0] == 0:
        raise ValueError("Factorization is not possible.")
    U[0, 0] = a[0, 0]
    for j in range(1, n):
        U[0, j] = a[0, j] / L[0, 0]
        L[j, 0] = a[j, 0] / U[0, 0]
    for i in range(1, n-1):
        s = sum(L[i, k] * U[k, i] for k in range(i))
        U[i, i] = (a[i, i] - s) / L[i, i]
        if U[i, i] == 0:
            raise ValueError("Factorization is not possible.")
        for j in range(i+1, n):
            r = sum(L[i, k] * U[k, j] for k in range(i))
            U[i, j] = (a[i, j] - r) / L[i, i]
            t = sum(L[j, k] * U[k, i] for k in range(i))
            L[j, i] = (a[j, i] - t) / U[i, i]
    w = sum(L[n-1, k] * U[k, n-1] for k in range(n-1))
    U[n-1, n-1] = (a[n-1, n-1] - w) / L[n-1, n-1]
    return L, U

def lu_crout(a):
    """
    Perform LU Decomposition of a square matrix using Crout's method.

    Parameters
    ----------
    a : numpy.ndarray
        The square matrix to decompose (shape: n x n).

    Returns
    -------
    L : numpy.ndarray
        Lower triangular matrix (shape: n x n).
    U : numpy.ndarray
        Upper triangular matrix with unit diagonal (shape: n x n).

    Raises
    ------
    ValueError
        If the matrix is singular or factorization is not possible.
    """
    n = a.shape[0]
    U = np.eye(n)
    L = np.zeros((n, n))
    if a[0, 0] == 0:
        raise ValueError("Factorization is not possible.")
    L[0, 0] = a[0, 0]
    for j in range(1, n):
        L[j, 0] = a[j, 0] / U[0, 0]
        U[0, j] = a[0, j] / L[0, 0]
    for i in range(1, n - 1):
        s = sum(L[i, k] * U[k, i] for k in range(i))
        L[i, i] = (a[i, i] - s) / U[i, i]
        if L[i, i] == 0:
            raise ValueError("Factorization is not possible.")
        for j in range(i + 1, n):
            t = sum(L[j, k] * U[k, i] for k in range(i))
            L[j, i] = (a[j, i] - t) / U[i, i]
            r = sum(L[i, k] * U[k, j] for k in range(i))
            U[i, j] = (a[i, j] - r) / L[i, i]
    w = sum(L[n - 1, k] * U[k, n - 1] for k in range(n - 1))
    L[n - 1, n - 1] = (a[n - 1, n - 1] - w) / U[n - 1, n - 1]
    return L, U

if __name__ == "__main__":
    # Example usage for library demonstration
    A = np.array([[4, 3], [6, 3]], dtype=float)
    print("Input matrix A:")
    print(A)

    print("\nDoolittle's method:")
    L, U = lu_doolittle(A)
    print("L =\n", L)
    print("U =\n", U)
    print("L @ U =\n", np.dot(L, U))

    print("\nCrout's method:")
    Lc, Uc = lu_crout(A)
    print("L =\n", Lc)
    print("U =\n", Uc)
    print("L @ U =\n", np.dot(Lc, Uc))