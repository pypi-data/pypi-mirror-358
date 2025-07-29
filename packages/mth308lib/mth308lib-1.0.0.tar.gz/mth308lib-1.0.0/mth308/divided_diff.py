import numpy as np
def divided_difference_table(x, y):
    """
    Compute the full divided difference table for Newton's interpolation.

    Parameters
    ----------
    x : array_like
        1D array of x data points [x0, x1, ..., xn].
    y : array_like
        1D array of corresponding y values f(x) = [f(x0), f(x1), ..., f(xn)].

    Returns
    -------
    table : 2D numpy.ndarray
        The divided difference table. The first column is y, and the upper triangle
        contains the divided differences.

    Example
    -------
    >>> x = [1, 2, 4]
    >>> y = [1, 4, 16]
    >>> table = divided_difference_table(x, y)
    >>> print(table)
    [[ 1.  0.  0.]
     [ 4.  3.  0.]
     [16.  6.  1.]]
    """
    n = len(x)
    table = np.zeros((n, n))
    table[:, 0] = y

    for i in range(1, n):
        for j in range(1, i+1):
            numerator = table[i][j-1] - table[i-1][j-1]
            denominator = x[i] - x[i-j]
            table[i][j] = numerator / denominator

    return table

# Example demonstration
if __name__ == "__main__":
    x = [1, 2, 4]
    y = [1, 4, 16]
    table = divided_difference_table(x, y)
    print("Divided Difference Table:")
    print(table)
def newton_divided_diff(x, y):
    """
    Compute the divided difference coefficients for Newton's interpolating polynomial.

    Parameters:
    -----------
    x : array_like
        1D array of x data points [x0, x1, ..., xn].
    y : array_like
        1D array of corresponding y values f(x) = [f(x0), f(x1), ..., f(xn)].

    Returns:
    --------
    table : 2D numpy array
        The full divided difference table.
        The first column is [f(x0), f(x1), ..., f(xn)],
        The first row of each column contains the Newton coefficients:
        [F0,0, F1,1, ..., Fn,n]
    
    Example:
    --------
    >>> x = [1, 2, 4]
    >>> y = [1, 4, 16]
    >>> newton_divided_diff(x, y)
    """

    n = len(x)
    table = np.zeros((n, n))
    table[:, 0] = y  # Fill first column with y values

    # Step-1: Fill divided difference table
    for i in range(1, n):
        for j in range(1, i+1):
            numerator = table[i][j-1] - table[i-1][j-1]
            denominator = x[i] - x[i-j]
            table[i][j] = numerator / denominator

    return table
