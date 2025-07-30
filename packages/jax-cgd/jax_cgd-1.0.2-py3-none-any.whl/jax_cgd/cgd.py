import jax
import jax.numpy as jnp
from jax import grad, jit
from . import utils
from . import solvers
from functools import partial
from typing import Callable

class BCGD(object):
    def __init__(self, x_params_pytree: dict, y_params_pytree: dict, f_pytree_input: Callable, lr=1e-3, solver=None):
        """_summary_

        Args:
            x_params_pytree (_type_): Parameters of the model that minimizes f.
            y_params_pytree (_type_): Parameters of the model that maximizes f.
            f_pytree_input (_type_): Function that takes x and y parameters and returns the value of f.
            lr (_type_, optional): Learning rate. Defaults to 1e-3.
            solver (_type_, optional): Linear algebra solver to use to solve linear systems of equations. Defaults to None.
        """
        
        self.x_params_pytree = x_params_pytree
        self.y_params_pytree = y_params_pytree
        self.eta = lr
        
        if solver is None:
            self.solver = solvers.GMRES()
        else:
            self.solver = solver

        self.x_params, self.x_metadata = utils.pytree2array(x_params_pytree)
        self.y_params, self.y_metadata = utils.pytree2array(y_params_pytree)

        self.x_metadata = jax.device_get(self.x_metadata)
        self.y_metadata = jax.device_get(self.y_metadata)

        # Count number of parameters
        self.n_x = self.x_params.shape[0]
        self.n_y = self.y_params.shape[0]


        # Initialize timestep
        self.timestep = 0
        self.iter_num = 0

        self.f_pytree_input = f_pytree_input
        self.f = lambda x, y: f_pytree_input(utils.array2pytree(x, self.x_metadata), utils.array2pytree(y, self.y_metadata))

    def get_infos(self):
        """
        Get the current parameters of the model.

        Returns:
            x_params_arr, y_params_arr, x_params_pytree, y_params_pytree, timestep, iter_num
        """
        self.x_params_pytree = utils.array2pytree(self.x_params, self.x_metadata)
        self.y_params_pytree = utils.array2pytree(self.y_params, self.y_metadata)

        return self.x_params,self.y_params, self.x_params_pytree, self.y_params_pytree, self.timestep, self.iter_num

    def step(self):
        return 0
        

def generate_step_func(eta, solver, f):
    """
    Generate a step function for the BCGD optimizer.

    Args:
        eta: Learning rate.
        solver: Linear algebra solver to use to solve linear systems of equations.
        f: Objective function. Callable.

    Returns:
        A step function that performs a single optimization step.
    """
    return partial(step_func, eta=eta, solver=solver, f=f)



def step_func(x_params, y_params, timestep, eta, solver, f):
    """
    Perform a single optimization step for the ACGD optimizer.

    Args:
        x_params: Flattened array of x parameters.
        y_params: Flattened array of y parameters.
        timestep: Current timestep.
        eta: Learning rate.
        solver: Linear algebra solver for solving linear systems.
        f: Objective function. Callable.

    Returns:
        Updated x_params, y_params, timestep, iter_num
    """
    timestep += 1

    # Compute gradients
    dfdx_val = jax.grad(f, argnums=0)(x_params, y_params)
    dfdy_val = jax.grad(f, argnums=1)(x_params, y_params)


    # Compute the Hessian-vector product
    A1 = utils.Operater(f, y_params, x_params, eta, eta)
    b1 = eta ** 0.5 * (dfdx_val + utils.H_xy_vy(f, x_params, y_params, eta * dfdy_val))
    sol = solver.solve(A1.as_function(), b1)
    dx = -eta ** 0.5 * sol
    dy = eta * (dfdy_val + utils.H_yx_vx(f, x_params, y_params, dx))

    iter_num = A1.iter_num

    # Update parameters
    x_params += dx
    y_params += dy


    return x_params, y_params, timestep, iter_num

    
   
