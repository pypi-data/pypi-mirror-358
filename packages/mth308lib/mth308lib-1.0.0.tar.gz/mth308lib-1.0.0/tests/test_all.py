import unittest
import numpy as np
from mth308 import (
    bisection_method, trapezoidal_rule, divided_difference_table, newton_divided_diff,
    euler_method, gauss_seidel, gaussian_elimination, jacobi, lu_doolittle, lu_crout,
    modified_regula_falsi, newton_raphson, power_method, regula_falsi, rk4,
    secant_method, simpsons_one_third, sor_solver
)

class TestMth308Lib(unittest.TestCase):
    def test_bisection_method(self):
        f = lambda x: x**2 - 2
        root, iterations, converged = bisection_method(f, 0, 2, N=50, eps=1e-8)
        self.assertTrue(converged)
        self.assertAlmostEqual(root, np.sqrt(2), places=7)

    def test_trapezoidal_rule(self):
        result = trapezoidal_rule(lambda x: x**2, 0, 2, N=100)
        self.assertAlmostEqual(result, 8/3, places=2)

    def test_divided_difference_table(self):
        x = [1, 2, 4]
        y = [1, 4, 16]
        table = divided_difference_table(x, y)
        self.assertAlmostEqual(table[2,2], 1.0, places=7)

    def test_newton_divided_diff(self):
        x = [1, 2, 4]
        y = [1, 4, 16]
        table = newton_divided_diff(x, y)
        self.assertAlmostEqual(table[2,2], 1.0, places=7)

    def test_euler_method(self):
        f = lambda t, y: y
        t, w = euler_method(f, 0, 1, 1, N=10)
        self.assertEqual(len(t), 11)
        self.assertEqual(len(w), 11)

    def test_gauss_seidel(self):
        A = [[4, 1, 1], [1, 3, 1], [1, 1, 5]]
        b = [7, 8, 12]
        X, converged = gauss_seidel(A, b, max_iter=10)
        self.assertEqual(X.shape[0], 3)
        self.assertTrue(X.shape[1] >= 2)

    def test_gaussian_elimination(self):
        a = [[2, 3], [5, 4]]
        b = [8, 13]
        x = gaussian_elimination(a, b)
        self.assertIsNotNone(x)
        self.assertAlmostEqual(x[0,0]*2 + x[1,0]*3, 8, places=6)

    def test_jacobi(self):
        A = np.array([[10.0, 2.0, 1.0], [1.0, 5.0, 1.0], [2.0, 3.0, 10.0]])
        b = np.array([9.0, -1.0, 27.0])
        x0 = np.zeros(3)
        X = jacobi(A, b, x0, max_iter=5)
        self.assertEqual(X.shape[0], 3)

    def test_lu_doolittle(self):
        A = np.array([[4, 3], [6, 3]], dtype=float)
        L, U = lu_doolittle(A)
        self.assertTrue(np.allclose(np.dot(L, U), A))

    def test_lu_crout(self):
        A = np.array([[4, 3], [6, 3]], dtype=float)
        L, U = lu_crout(A)
        self.assertTrue(np.allclose(np.dot(L, U), A))

    def test_modified_regula_falsi(self):
        f = lambda x: x**2 - 2
        root = modified_regula_falsi(f, 0, 2, tol=1e-8)
        self.assertAlmostEqual(root, np.sqrt(2), places=7)

    def test_newton_raphson(self):
        f = lambda x: x**2 - 2
        df = lambda x: 2*x
        root, info = newton_raphson(f, df, 1.5, max_iter=20, tol=1e-8)
        self.assertTrue(info['converged'])
        self.assertAlmostEqual(root, np.sqrt(2), places=7)

    def test_power_method(self):
        A = np.array([[2, 0], [0, 1]])
        x0 = np.array([1, 1])
        eigenvalue, eigenvector, _, _ = power_method(A, x0, tol=1e-6, max_iter=100)
        self.assertAlmostEqual(eigenvalue, 2, places=5)

    def test_regula_falsi(self):
        f = lambda x: x**2 - 2
        root, converged, iterations = regula_falsi(f, 0, 2, N=50, tol=1e-8)
        self.assertTrue(converged)
        self.assertAlmostEqual(root, np.sqrt(2), places=7)

    def test_rk4(self):
        f = lambda x, y: x + y
        x_vals, y_vals = rk4(f, 0, 1, 0.1, 10)
        self.assertEqual(len(x_vals), 11)
        self.assertEqual(len(y_vals), 11)

    def test_secant_method(self):
        f = lambda x: x**2 - 2
        root, history, message = secant_method(f, 0, 2, tol=1e-8, max_iter=20)
        self.assertIsNotNone(root)
        self.assertAlmostEqual(root, np.sqrt(2), places=7)

    def test_simpsons_one_third(self):
        result = simpsons_one_third(lambda x: x**2, 0, 2, N=100)
        self.assertAlmostEqual(result, 8/3, places=2)

    def test_sor_solver(self):
        A = np.array([[4.0, 1.0, 1.0], [1.0, 3.0, 1.0], [1.0, 1.0, 5.0]])
        b = np.array([7.0, 8.0, 11.0])
        x0 = np.zeros(3)
        w = 1.25
        max_iter = 5
        X = sor_solver(A, b, x0, w, max_iter)
        self.assertEqual(X.shape[0], 3)
        self.assertEqual(X.shape[1], max_iter+1)

if __name__ == '__main__':
    unittest.main()
