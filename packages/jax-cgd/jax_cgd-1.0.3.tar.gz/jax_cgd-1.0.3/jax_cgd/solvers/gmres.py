import jax
import jax.numpy as jnp
from functools import partial
import jax.lax as lax
from jax.scipy.sparse.linalg import gmres

class GMRES:
    def __init__(self, tol=1e-7, atol=1e-20, max_iter=500):
        '''
        Generalized Minimal Residual Method (GMRES).
        Only works for non-singular matrices A.
        '''
        self.tol = tol
        self.atol = atol
        self.max_iter = max_iter
        self.prev_sol = None

    def solve(self, limap, b):
        x0 = self.prev_sol
        solution, _ = gmres(limap, b, tol=self.tol, atol=self.atol, M=None, maxiter=self.max_iter, x0=x0)
        self.prev_sol = solution
        return solution

