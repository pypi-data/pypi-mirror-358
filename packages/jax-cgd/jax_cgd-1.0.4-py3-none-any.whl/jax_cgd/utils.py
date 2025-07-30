import jax
import jax.numpy as jnp
from jax import grad, jacrev, jacfwd, jvp
import jax.lax as lax
import jax.numpy as jnp
import numpy as np
from jax.tree_util import tree_flatten, tree_unflatten


def pytree2array(pytree):
    """
    Combine jax.numpy arrays in the pytree into a single 1D array.
    
    Process:
      1. Use tree_util.tree_flatten to get all leaf nodes (leaves) and structure information (treedef).
      2. Flatten each leaf to 1D using jnp.ravel and record the original shape (lost structure information) into leavesdata.
      3. Use jnp.concatenate to combine all flattened leaves into a single 1D array (arr).
    
    Returns:
      arr: Combined 1D jax.numpy array
      metadata: (leavesdata, treedef)
          leavesdata: List, each element records the original shape of the corresponding leaf
          treedef: Metadata describing the structure of the pytree
    """
    # Step 1: Flatten the pytree
    leaves, treedef = tree_flatten(pytree)
    
    flat_leaves = []
    leavesdata = []
    for leaf in leaves:
        # Record the original shape of each leaf
        leavesdata.append(leaf.shape)
        # Flatten the leaf to a 1D array
        flat_leaves.append(jnp.ravel(leaf))
    
    # Combine all flattened arrays into a single 1D array
    arr = jnp.concatenate(flat_leaves)
    metadata = (leavesdata, treedef)
    return arr, metadata

def array2pytree(arr, metadata):
    """
    Restore the original pytree from the given 1D array and metadata.
    
    Args:
      arr: 1D jax.numpy array obtained from pytree2array
      metadata: (leavesdata, treedef)
          leavesdata: Original shape information of each leaf
          treedef: Structure information of the pytree
          
    Returns:
      Restored pytree with leaf nodes as jax.numpy arrays.
    """
    leavesdata, treedef = metadata
    leaves = []
    offset = 0
    for shape in leavesdata:
        # Calculate the number of elements in the current leaf node
        size = 1
        for s in shape:
            size *= s
        # Extract the corresponding part from arr and reshape it to the original shape
        leaf_flat = arr[offset: offset + size]
        leaf = jnp.reshape(leaf_flat, shape)
        leaves.append(leaf)
        offset += size
        
    # Use tree_util.tree_unflatten to restore the pytree
    pytree = tree_unflatten(treedef, leaves)
    return pytree


def H_xy_vy(h, x, y, vy):
    """
    Compute the Hessian-Vector Product: H_xy * vy.

    Args:
        h: Callable, scalar function h(x, y).
        x: 1D array, parameters with respect to x.
        y: 1D array, parameters with respect to y.
        vy: 1D array, vector to multiply with the Hessian H_xy (same shape as y).

    Returns:
        1D array, result of H_xy * vy (same shape as x).
    """
    # Define the function g(x, y) = ∂h / ∂x
    grad_x = lambda x_, y_: jax.grad(h, argnums=0)(x_, y_)

    # Compute the Hessian-vector product: (∂²h / ∂x ∂y^T) * vy
    _, hvp = jax.jvp(lambda y_: grad_x(x, y_), (y,), (vy,))
    return hvp

def H_yx_vx(h, x, y, vx):
    """
    Compute the Hessian-Vector Product: H_yx * vx.

    Args:
        h: Callable, scalar function h(x, y).
        x: 1D array, parameters with respect to x.
        y: 1D array, parameters with respect to y.
        vx: 1D array, vector to multiply with the Hessian H_yx (same shape as x).

    Returns:
        1D array, result of H_yx * vx (same shape as y).
    """
    # Define the function g(y, x) = ∂h / ∂y
    grad_y = lambda x_, y_: jax.grad(h, argnums=1)(x_, y_)

    # Compute the Hessian-vector product: (∂²h / ∂y ∂x^T) * vx
    _, hvp = jax.jvp(lambda x_: grad_y(x_, y), (x,), (vx,))
    return hvp

class Operater:
    def __init__(self, f, y_params_arr, x_params_arr, eta_y, eta_x):


        self.f = f
        self.y_params_arr = y_params_arr
        self.x_params_arr = x_params_arr
        self.eta_y = eta_y
        self.eta_x = eta_x
        self.shape = self.shape = (len(x_params_arr), len(x_params_arr))
        self.iter_num = 0

    def __matmul__(self, v: jnp.array) -> jnp.array:
        """
        Performs a matrix-free matrix-vector product in JAX.

        Args:
            v: Input vector for the matrix-vector product (1D array). The same shape as x_params_arr.

        Returns:
            result: The result of the matrix-vector product (1D array).
        """
        # Scale the input vector by sqrt(eta_x) A^{1/2}_{x,t} v
        self.iter_num += 1
        v0 = self.eta_x ** 0.5 * v

        # Compute the first Hessian-vector product: A_{y,t} * (D^2_{yx}f * v0)
        grad_fn1 = H_yx_vx(self.f, self.x_params_arr, self.y_params_arr, v0)
        v1 = self.eta_y * grad_fn1

        # Compute the second Hessian-vector product: A^{1/2}_{x,t} * (D^2_{xy}f * v1)
        grad_fn2 = H_xy_vy(self.f, self.x_params_arr, self.y_params_arr, v1)
        v2 = self.eta_x ** 0.5 * grad_fn2

        # Add the identity contribution: I * v + v2
        result = v + v2

        return result
    
    def as_function(self):
        return jax.jit(lambda v: self @ v)



