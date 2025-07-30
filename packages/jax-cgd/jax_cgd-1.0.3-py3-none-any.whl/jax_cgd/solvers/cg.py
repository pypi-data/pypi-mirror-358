import jax
import jax.numpy as jnp
from functools import partial
from jax.scipy.sparse.linalg import cg
class CG:
    def __init__(self, tol=1e-7, atol=1e-20, max_iter=500):
        '''  Conjugate gradient method, implementation based on
            https://en.wikipedia.org/wiki/Conjugate_gradient_method.
            Only works for positive definite matrices A! '''

        self.tol = tol
        self.atol = atol
        self.max_iter = max_iter
        self.prev_sol = None

    def solve(self, limap, b):
        x0 = self.prev_sol
        solution, _ = cg(limap, b, tol=self.tol, atol=self.atol, M=None, maxiter=self.max_iter, x0=x0)
        self.prev_sol = solution
        return solution

