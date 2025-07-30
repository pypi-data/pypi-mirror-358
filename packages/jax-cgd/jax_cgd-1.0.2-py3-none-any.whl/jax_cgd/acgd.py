import jax
import jax.numpy as jnp
from jax import grad, jit
from . import utils
from . import solvers
from functools import partial
from typing import Callable


class ACGD:
    def __init__ (self, x_params_pytree: dict, y_params_pytree: dict, f_pytree_input: Callable, lr: float=1e-3, beta: float=0.9, eps: float=1e-3, solver=None):
        """
            _summary_
                x_params_pytree (_type_): Parameters of the model that minimizes f.
                y_params_pytree (_type_): Parameters of the model that maximizes f.
                f_pytree_input (_type_): Function that takes x and y parameters and returns the value of f.
                lr (_type_, optional): Learning rate. Defaults to 1e-3.
                beta (float, optional): Exponential decay rate for the second moment estimates. Defaults to 0.9.
                eps (_type_, optional): Small constant for numerical stability. Defaults to 1e-3.
                solver (_type_, optional): Linear algebra solver to use to solve linear systems of equations. Defaults to None.
            """

        # Store arguments in class
        self.x_params_pytree = x_params_pytree
        self.y_params_pytree = y_params_pytree
        self.eta = lr
        self.beta = beta
        self.eps = eps

        if solver is None:
            self.solver = solvers.GMRES()
        else:
            self.solver = solver

        self.x_params, self.x_metadata = utils.pytree2array(x_params_pytree)
        self.y_params, self.y_metadata = utils.params2array(y_params_pytree)

        self.x_metadata = jax.device_get(self.x_metadata)
        self.y_metadata = jax.device_get(self.y_metadata)

        # Count number of parameters
        self.n_x = self.x_params.shape[0]
        self.n_y = self.y_params.shape[0]

        self.vx = jnp.zeros(self.n_x)
        self.vy = jnp.zeros(self.n_y)

        # Initialize timestep

        self.timestep = 0
        self.iter_num = 0
        # self.prev_sol = None

        self.f_pytree_input = f_pytree_input
        self.f = lambda x, y: f_pytree_input(utils.array2pytree(x, self.x_metadata), utils.array2pytree(y, self.y_metadata))
        # Generate the step function
        self.step_func = generate_step_func(self.eta, self.beta, self.eps, self.solver, self.f)
        self.step_func = jit(self.step_func)

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
        """
        Perform a single optimization step by calling the external step_func.
        """
        self.x_params, self.y_params, self.vx, self.vy, self.timestep, self.iter_num = self.step_func(
            self.x_params, self.y_params, self.vx, self.vy, self.timestep
        )
        

def generate_step_func(eta, beta, eps, solver, f):
    """
    Generate a step function for the ACGD optimizer.

    Args:
        x_meta_data: Metadata for reconstructing x_params_pytree.
        y_meta_data: Metadata for reconstructing y_params_pytree.
        eta: Learning rate.
        beta: Exponential decay rate for second moment estimates.
        eps: Small constant for numerical stability.
        solver: Linear algebra solver for solving linear systems.
        f: Objective function. Callable.

    Returns:
        A function that performs a single optimization step.
    """
    return partial(step_func, eta=eta, beta=beta, eps=eps, solver=solver, f=f)


def step_func(x_params, y_params, vx, vy, timestep, eta, beta, eps, solver, f):
    """
    Perform a single optimization step for the ACGD optimizer.

    Args:
        x_params: Flattened array of x parameters.
        y_params: Flattened array of y parameters.
        vx: Second moment estimate for x parameters.
        vy: Second moment estimate for y parameters.
        timestep: Current timestep.
        eta: Learning rate.
        beta: Exponential decay rate for second moment estimates.
        eps: Small constant for numerical stability.
        solver: Linear algebra solver for solving linear systems.
        f: Objective function. Callable.

    Returns:
        Updated x_params, y_params, vx, vy, timestep, iter_num
    """
    timestep += 1

    # Compute gradients
    dfdx_val = jax.grad(f, argnums=0)(x_params, y_params)
    dfdy_val = jax.grad(f, argnums=1)(x_params, y_params)

    # Update second moment estimates
    vx = beta * vx + (1 - beta) * dfdx_val ** 2
    vy = beta * vy + (1 - beta) * dfdy_val ** 2

    # Compute bias-corrected learning rates
    bias_correction = 1 - beta**timestep
    eta_x = eta * jnp.sqrt(bias_correction) / (jnp.linalg.norm(vx) + eps)
    eta_y = eta * jnp.sqrt(bias_correction) / (jnp.linalg.norm(vy) + eps)

    # Compute the Hessian-vector product
    A1 = utils.Operater(f, y_params, x_params, eta_y, eta_x)
    b1 = eta_x ** 0.5 * (dfdx_val + utils.H_xy_vy(f, x_params, y_params, eta_y * dfdy_val))
    sol = solver.solve(A1.as_function(), b1)
    dx = -eta_x ** 0.5 * sol
    dy = eta_y * (dfdy_val + utils.H_yx_vx(f, x_params, y_params, dx))

    iter_num = A1.iter_num

    # Update parameters
    x_params += dx
    y_params += dy


    return x_params, y_params, vx, vy, timestep, iter_num

    
   