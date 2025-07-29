import numpy as np
import matplotlib.pyplot as plt

def euler_method(f, a, b, y0, N=None, h=None):
    """
    Solve an ODE using Euler's method on the interval [a,b].
    
    Either N (number of sub-intervals) or h (step size) must be provided.
    
    Parameters
    ----------
    f : callable
        The derivative function f(t, y), returns the rate of change.
    a : float
        The starting point of the interval.
    b : float
        The end point of the interval.
    y0 : float
        Initial condition y(a) = y0.
    N : int, optional
        Number of sub-intervals.
    h : float, optional
        Step size.
    
    Returns
    -------
    t : ndarray
        Time points.
    w : ndarray
        Approximated solution at each time point.
    """
    # Compute N and h
    if N is None and h is None:
        raise ValueError("You must provide either N or h.")
    if N is None:
        N = int((b - a) / h)
    if h is None:
        h = (b - a) / N
    N = int(N)
    h = (b - a) / N

    # Initialize arrays
    t = np.zeros(N + 1)
    w = np.zeros(N + 1)

    # Initial conditions
    t[0] = a
    w[0] = y0

    # Euler's iterative formula
    for i in range(1, N + 1):
        w[i] = w[i-1] + h * f(t[i-1], w[i-1])
        t[i] = a + i*h

    return t, w

# Test the function
if __name__ == "__main__":
    # Example ODE: y' = y + t with y(0) = 1 on [0,1]
    f = lambda t, y: y + t
    t, w = euler_method(f, a=0, b=1, y0=1, N=10)

    print("t:", t)
    print("w:", w)

    # Plot the result
    plt.plot(t, w, 'o-', label='Euler Approximation')
    plt.xlabel('t')
    plt.ylabel('w(t)')
    plt.title('Euler Method Approximation')
    plt.grid(True)
    plt.legend()
    plt.show()
