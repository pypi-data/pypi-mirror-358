import numpy as np
def power_method(A, x0, tol=1e-6, max_iter=1000):
    """
    Computes the dominant eigenvalue and corresponding eigenvector of a square matrix using the Power Method.

    Parameters
    ----------
    A : np.ndarray
        The input square matrix (n x n).
    x0 : np.ndarray
        Initial guess for the eigenvector (n, ) or (n, 1).
    tol : float, optional
        Tolerance for convergence (default is 1e-6).
    max_iter : int, optional
        Maximum number of iterations (default is 1000).

    Returns
    -------
    eigenvalue : float
        Approximation of the dominant eigenvalue.
    eigenvector : np.ndarray
        Approximation of the corresponding eigenvector (n, 1).
    eigenvalue_iters : list of float
        List of eigenvalue approximations at each iteration.
    eigenvector_iters : np.ndarray
        Array of eigenvector approximations at each iteration (n, num_iters+1).
    """
    n = A.shape[0]
    x = np.array(x0, dtype=float).reshape((n, 1))
    p = np.argmax(np.abs(x))
    z = x.copy()
    Mu = []

    for k in range(max_iter):
        y = A @ x
        mu = y[p, 0]
        Mu.append(mu)
        p = np.argmax(np.abs(y))
        if y[p, 0] == 0:
            break
        ERR = np.linalg.norm(x - y / y[p, 0], ord=np.inf)
        x = y / y[p, 0]
        z = np.hstack((z, x))
        if ERR < tol:
            break

    return Mu[-1], x, Mu, z

# Example demonstration
if __name__ == "__main__":
    # Example: 3x3 matrix
    print("Power Method Example\n")
    n = int(input("Enter the dimension of the square matrix: "))
    print(f"Enter the entries of the matrix row-wise ({n} rows, {n} columns):")
    A = []
    for i in range(n):
        row = list(map(float, input().strip().split()))
        A.append(row)
    A = np.array(A)

    x0 = np.array(list(map(float, input("Enter an initial guess (as a column vector): ").split())))
    tol = float(input("Enter the tolerance: "))
    max_iter = int(input("Enter the maximum number of iterations: "))

    print("\nThe given matrix is:")
    print(A)

    eigenvalue, eigenvector, eigenvalue_iters, eigenvector_iters = power_method(A, x0, tol, max_iter)

    print("\nThe iterations for eigen vector are given as:\n")
    print(np.array2string(eigenvector_iters, formatter={'float_kind': lambda x: '%10.6f' % x}))

    print("\nThe iterations for eigen value are given as:\n")
    print(np.array2string(np.array(eigenvalue_iters), formatter={'float_kind': lambda x: '%10.6f' % x}))

    print(f"\nAn approximation of the dominant eigen value is: {eigenvalue:.6f}")
    print("\nAn eigen vector corresponding to the dominant eigen value is:\n", eigenvector.flatten())