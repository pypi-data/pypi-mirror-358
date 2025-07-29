import math
def bisection_method(f, a, b, N=100, eps=1e-7, verbose=False):
    """
    Find a root of the equation f(x) = 0 in the interval [a, b] using the bisection method.

    Parameters:
        f (callable): The function for which to find the root.
        a (float): Left endpoint of the interval.
        b (float): Right endpoint of the interval.
        N (int): Maximum number of iterations (default: 100).
        eps (float): Tolerance for stopping criterion (default: 1e-7).
        verbose (bool): If True, prints iteration details.

    Returns:
        root (float): The approximate root found.
        iterations (int): Number of iterations performed.
        converged (bool): Whether the method converged within the given tolerance.
    """
    y_0 = f(a)
    y_1 = f(b)
    if y_0 == 0:
        if verbose:
            print(f"\nA root of the given equation is {a:.9f}.")
        return a, 0, True
    if y_1 == 0:
        if verbose:
            print(f"\nA root of the given equation is {b:.9f}.")
        return b, 0, True
    if y_0 * y_1 > 0:
        raise ValueError(f"Bisection method cannot locate any root in the interval [{a}, {b}]. f(a) and f(b) must have opposite signs.")

    k = 1
    if verbose:
        print("\nThe Bisection iterations are given as:\n")
        print("    k          a_k         b_k         x_k        f(x_k)")
    while k <= N:
        x = (a + b) / 2
        y = f(x)
        if verbose:
            print(f"{k:4d}  {a:12.9f}  {b:12.9f}  {x:12.9f}  {y:12.9f}")
        if y == 0 or (b - a) <= eps:
            return x, k, True
        if y_0 * y > 0:
            a = x
            y_0 = y
        else:
            b = x
        k += 1
    return x, N, False

def f(x):
    """Example function: sqrt(x) - cos(x)"""
    return math.sqrt(x) - math.cos(x)

if __name__ == "__main__":
    print("\nThe given equation is: sqrt(x) - cos(x) = 0.")
    # Example demonstration
    try:
        a = float(input('\nEnter the left end point of the interval: '))
        b = float(input('Enter the right end point of the interval: '))
        N = int(input('Enter the maximum number of iterations: '))
        eps = float(input('Enter the measure of accuracy (tolerance): '))
        root, iterations, converged = bisection_method(f, a, b, N, eps, verbose=True)
        if converged:
            print(f"\nAn approximate root (with tolerance {eps}) of the given equation is {root:.9f}.")
        else:
            print(f"\nMaximum number of iterations reached.\nAn approximate root of the given equation is {root:.9f}.")
    except Exception as e:
        print(f"\nError: {e}")

    # Example usage as a library function (without user input)
    # root, iterations, converged = bisection_method(f, 0.5, 1.0, N=50, eps=1e-6, verbose=True)
    # print(f"\nRoot found: {root}, Iterations: {iterations}, Converged: {converged}")