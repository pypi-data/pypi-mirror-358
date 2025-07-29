import numpy as np
def gaussian_elimination(a, b, verbose=False):
    """
    Solves the linear system Ax = b using Gaussian elimination.

    Parameters:
        a (np.ndarray): Coefficient matrix of shape (n, n).
        b (np.ndarray): Right-hand side vector of shape (n,) or (n, 1).
        verbose (bool): If True, prints intermediate steps.

    Returns:
        x (np.ndarray): Solution vector of shape (n, 1) if a unique solution exists.
        None: If no unique solution exists.
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float).reshape(-1, 1)
    n = a.shape[0]
    A = np.hstack((a, b))
    x = np.zeros((n, 1))
    m = np.eye(n)
    p = 0  # Track pivot row

    if verbose:
        print("The augmented matrix corresponding to the system is given by:")
        print(A)
        print("Gaussian elimination steps:")

    for i in range(n-1):
        if verbose:
            print(f"Step- {i+1}\n")
        p = 0
        for l in range(i, n):
            if p == 0 and A[l, i] != 0:
                p = l
        if p != 0:
            if p != i:
                # Row swap
                A[[i, p], :] = A[[p, i], :]
            for k in range(i+1, n):
                m[k, i] = A[k, i] / A[i, i]
                A[k, :] = A[k, :] - m[k, i] * A[i, :]
            if verbose:
                print(A)
    # Solution existence check and back substitution
    if p != 0:
        if A[n-1, n-1] == 0:
            if A[n-1, n] == 0:
                if verbose:
                    print("No unique solution exists.")
                return None
            else:
                if verbose:
                    print("No solution exists.")
                return None
        else:
            # Backward substitution
            x[n-1] = A[n-1, n] / A[n-1, n-1]
            for i in range(n-2, -1, -1):
                s = 0
                for j in range(i+1, n):
                    s += A[i, j] * x[j]
                x[i] = (A[i, n] - s) / A[i, i]
            if verbose:
                print("Solution of the system is given by:")
                print(x)
            return x
    if p == 0:
        if verbose:
            print("No unique solution exists.")
        return None

# Example demonstration
if __name__ == "__main__":
    # Example: Solve the system
    # 2x + 3y = 8
    # 5x + 4y = 13
    a = [[2, 3],
         [5, 4]]
    b = [8, 13]
    print("Solving the system:\n2x + 3y = 8\n5x + 4y = 13\n")
    x = gaussian_elimination(a, b, verbose=True)
    if x is not None:
        print("Computed solution:")
        print(x)
    else:
        print("No unique solution exists.")