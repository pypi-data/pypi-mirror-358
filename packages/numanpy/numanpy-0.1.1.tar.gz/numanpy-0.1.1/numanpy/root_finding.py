def bisect(f, a, b, eps=1e-6, N=100, verbose=False):
    """
    Bisection method for finding a root of the scalar function f in the interval [a, b].

    Parameters:
    f (callable): The scalar function for which to find the root.
    a (float): The start of the interval.
    b (float): The end of the interval.
    eps (float): The tolerance for convergence.
    N (int): The maximum number of iterations.
    verbose (bool): If True, returns iterates and prints convergence information; else, returns only the root.

    Returns:
    float: The approximate root of the scalar function f.
    """
    if f(a) * f(b) >= 0:
        raise ValueError("f(a) and f(b) must have different signs.")
    cs = []

    for _ in range(N):
        cs.append((a + b) / 2)
        c = cs[-1]
        if abs(f(c)) < eps or (b - a) / 2 < eps:
            if verbose:
                print(f"Converged to {c} after {_ + 1} iterations.")
                return cs
            else:
                return c
        if f(c) * f(a) < 0:
            b = c
        else:
            a = c

    raise RuntimeError("Maximum number of iterations reached without convergence.")


def iterate(f, x0, eps=1e-6, N=100):
    """
    Fixed-point iteration method for finding a root of the scalar function f.

    Parameters:
    f (callable): The scalar function for which to find the root.
    x0 (float or ndarray): The initial guess for the root.
    eps (float): The tolerance for convergence.
    N (int): The maximum number of iterations.

    Returns:
    float: The approximate root of the scalar function f.
    """
    x = x0
    for _ in range(N):
        x_ = f(x)
        if abs(x_ - x) < eps:
            return x_
        x = x_

    raise RuntimeError("Maximum number of iterations reached without convergence.")


def newton(f, df, x0, eps=1e-6, N=100, verbose=False):
    """
    Newton's method for finding a root of the scalar function f.

    Parameters:
    f (callable): The scalar function for which to find the root.
    df (callable): The derivative of the scalar function f.
    x0 (float or ndarray): The initial guess for the root.
    eps (float): The tolerance for convergence.
    N (int): The maximum number of iterations.
    verbose (bool): If True, returns iterates and prints convergence information; else, returns only the root.

    Returns:
    float: The approximate root of the scalar function f.
    """
    x = [x0]
    for _ in range(N):
        fx = f(x[-1])
        dfx = df(x[-1])
        if dfx == 0:
            raise ValueError("Derivative is zero. No solution found.")
        
        x.append(x[-1] - fx / dfx)
        if abs(x[-1] - x[-2]) < eps:
            if verbose:
                print(f"Converged to {x[-1]} after {_ + 1} iterations.")
                return x
            else:
                return x[-1]

    raise RuntimeError("Maximum number of iterations reached without convergence.")