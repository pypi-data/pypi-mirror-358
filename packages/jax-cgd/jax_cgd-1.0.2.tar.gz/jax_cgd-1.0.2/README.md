# JAX-CGD

JAX implementation of Competitive Gradient Descent algorithms for minimax optimization problems.

## Features

- **ACGD (Adaptive Competitive Gradient Descent)**: An adaptive variant of competitive gradient descent with momentum
- **BCGD (Basic Competitive Gradient Descent)**: Standard competitive gradient descent algorithm
- **Flexible Solvers**: Support for different linear algebra solvers (CG, GMRES)
- **JAX Integration**: Built on JAX for automatic differentiation and JIT compilation

## Installation

```bash
pip install jax-cgd
```

## Algorithms

### ACGD (Adaptive Competitive Gradient Descent)
- Includes momentum and adaptive learning rates
- Better convergence properties for complex minimax problems
- Configurable exponential decay rate (beta) and numerical stability (eps)

### BCGD (Basic Competitive Gradient Descent)
- Standard competitive gradient descent
- Simpler implementation for basic minimax optimization

## Requirements

- Python >= 3.10
- JAX >= 0.5.1
- NumPy
- Flax >= 1.10.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
