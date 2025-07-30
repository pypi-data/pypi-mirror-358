from __future__ import annotations

"""
:class:`AbstractUnwrappable` objects and utilities.

These are placeholder values for specifying custom behaviour for nodes in a pytree,
applied using :func:`unwrap`.
"""

from abc import abstractmethod
from collections.abc import Callable
from typing import Any, Generic, TypeVar, Union

import equinox as eqx
import jax
import jax.numpy as jnp
from jax import lax
from jax.nn import softplus
from jax.tree_util import tree_leaves
from jaxtyping import Array, PyTree

from paramax_py39.utils import inv_softplus

T = TypeVar("T")


class AbstractUnwrappable(eqx.Module, Generic[T]):
    """An abstract class representing an unwrappable object.

    Unwrappables replace PyTree nodes, applying custom behavior upon unwrapping.
    """

    @abstractmethod
    def unwrap(self) -> T:
        """Returns the unwrapped pytree, assuming no wrapped subnodes exist."""
        ...


def unwrap(tree: PyTree):
    """Map across a PyTree and unwrap all :class:`AbstractUnwrappable` nodes."""

    def _unwrap(tree, *, include_self: bool):
        def _map_fn(leaf):
            if isinstance(leaf, AbstractUnwrappable):
                # Unwrap subnodes, then itself
                return _unwrap(leaf, include_self=False).unwrap()
            return leaf

        def is_leaf(x):
            is_unwrappable = isinstance(x, AbstractUnwrappable)
            included = include_self or x is not tree
            return is_unwrappable and included

        return jax.tree_util.tree_map(
            f=_map_fn,
            tree=tree,
            is_leaf=is_leaf,
        )

    return _unwrap(tree, include_self=True)


class Parameterize(AbstractUnwrappable[T]):
    """Unwrap an object by calling fn with args and kwargs."""

    fn: Callable[..., T]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __init__(self, fn: Callable[..., T], *args: Any, **kwargs: Any):
        self.fn = fn
        self.args = tuple(args)
        self.kwargs = kwargs

    def unwrap(self) -> T:
        return self.fn(*self.args, **self.kwargs)


def non_trainable(tree: PyTree):
    """Freezes parameters by wrapping inexact array leaves with :class:`NonTrainable`."""

    def _map_fn(leaf):
        return NonTrainable(leaf) if eqx.is_inexact_array(leaf) else leaf

    return jax.tree_util.tree_map(
        f=_map_fn,
        tree=tree,
        is_leaf=lambda x: isinstance(x, NonTrainable),
    )


class NonTrainable(AbstractUnwrappable[T]):
    """Applies stop gradient to all arraylike leaves before unwrapping."""

    tree: T

    def unwrap(self) -> T:
        differentiable, static = eqx.partition(self.tree, eqx.is_array_like)
        return eqx.combine(lax.stop_gradient(differentiable), static)


class WeightNormalization(AbstractUnwrappable[Array]):
    """Applies weight normalization (https://arxiv.org/abs/1602.07868)."""

    weight: Union[Array, AbstractUnwrappable[Array]]
    scale: Union[Array, AbstractUnwrappable[Array]]

    def __init__(self, weight: Union[Array, AbstractUnwrappable[Array]]):
        self.weight = weight
        scale_init = 1 / jnp.linalg.norm(unwrap(weight), axis=-1, keepdims=True)
        self.scale = Parameterize(softplus, inv_softplus(scale_init))

    def unwrap(self) -> Array:
        weight_norms = jnp.linalg.norm(self.weight, axis=-1, keepdims=True)
        return self.scale * self.weight / weight_norms


def contains_unwrappables(pytree: PyTree) -> bool:
    """Check if a pytree contains any AbstractUnwrappable nodes."""

    def _is_unwrappable(leaf):
        return isinstance(leaf, AbstractUnwrappable)

    leaves = tree_leaves(pytree, is_leaf=_is_unwrappable)
    return any(_is_unwrappable(leaf) for leaf in leaves)
