
## Paramax for Python 3.9 (a fork)
============
Parameterizations and constraints for JAX PyTrees
-----------------------------------------------------------------------

Paramax allows applying custom constraints or behaviors to PyTree components,
using unwrappable placeholders. This can be used for
- Enforcing positivity (e.g., scale parameters)
- Structured matrices (triangular, symmetric, etc.)
- Applying tricks like weight normalization
- Marking components as non-trainable

Some benefits of the unwrappable pattern:
- It allows parameterizations to be computed once for a model (e.g. at the top of the
  loss function).
- It is flexible, e.g. allowing custom parameterizations to be applied to PyTrees
  from external libraries
- It is concise

If you found the package useful, please consider giving it a star on github, and if you
create ``AbstractUnwrappable``s that may be of interest to others, a pull request would
be much appreciated!

## Documentation

Original documentation available [here](https://danielward27.github.io/paramax/).

## Installation (Requires python>=3.9)
```bash
pip install paramax 
```

## Example
```python
>>> import paramax
>>> import jax.numpy as jnp
>>> scale = paramax.Parameterize(jnp.exp, jnp.log(jnp.ones(3)))  # Enforce positivity
>>> paramax.unwrap(("abc", 1, scale))
('abc', 1, Array([1., 1., 1.], dtype=float32))
```

## Alternative parameterization patterns
Using properties to access parameterized model components is common but has drawbacks:
- Parameterizations are tied to class definition, limiting flexibility e.g. this
  cannot be used on PyTrees from external libraries
- It can become verbose with many parameters
- It often leads to repeatedly computing the parameterization

## Related
- We make use of the [Equinox](https://arxiv.org/abs/2111.00254) package, to register
the PyTrees used in the package
- This package spawned out of a need for a simple method to apply parameter constraints
    in the distributions package [flowjax](https://github.com/danielward27/flowjax)
