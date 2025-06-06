# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Types used by neuralgcm.experimental API."""
from __future__ import annotations

import dataclasses
import datetime
import functools
from typing import Any, Callable, Generic, TypeVar

import jax
import jax.numpy as jnp
from neuralgcm.experimental import coordax as cx
from neuralgcm.experimental.core import scales
import numpy as np
import pandas as pd
import tree_math


units = scales.units
#
# Generic types.
#
Array = np.ndarray | jax.Array
Dtype = jax.typing.DTypeLike | Any
Numeric = float | int | Array
PRNGKeyArray = jax.Array
ShapeDtypeStruct = jax.ShapeDtypeStruct
ShapeFloatStruct = functools.partial(ShapeDtypeStruct, dtype=jnp.float32)
Timestep = np.timedelta64 | float
TimedeltaLike = str | np.timedelta64 | pd.Timestamp | datetime.timedelta
Quantity = scales.Quantity

#
# Generic API input/output types.
#
Pytree = Any
PyTreeState = TypeVar('PyTreeState')


#
# Simulation function signatures.
#
StepFn = Callable[[PyTreeState], PyTreeState]
PostProcessFn = Callable[..., Pytree]


Query = dict[str, dict[str, cx.Coordinate | cx.Field]]
Observation = dict[str, dict[str, cx.Field]]


@tree_math.struct
class ModelState(Generic[PyTreeState]):
  """Simulation state decomposed into prognostic, diagnostic and randomness.

  Attributes:
    prognostics: Prognostic variables describing the simulation state.
    diagnostics: Optional diagnostic values holding diagnostic information.
    randomness: Optional randomness state describing stochasticity of the model.
  """

  prognostics: PyTreeState
  diagnostics: Pytree = dataclasses.field(default_factory=dict)
  randomness: Pytree = dataclasses.field(default_factory=dict)


@jax.tree_util.register_pytree_node_class
@dataclasses.dataclass
class Randomness:
  """State describing the random process."""

  prng_key: jax.Array
  prng_step: int = 0
  core: Pytree = None

  def tree_flatten(self):
    """Flattens Randomness JAX pytree."""
    leaves = (self.prng_key, self.prng_step, self.core)
    aux_data = ()
    return leaves, aux_data

  @classmethod
  def tree_unflatten(cls, aux_data, leaves):
    """Unflattens Randomness from aux_data and leaves."""
    return cls(*leaves, *aux_data)


#
# API function signatures.
#
PostProcessFn = Callable[..., Any]


#
# Auxiliary types for intermediate computations.
#
@dataclasses.dataclass(eq=True, order=True, frozen=True)
class KeyWithCosLatFactor:
  """Class describing a key by `name` and an integer `factor_order`."""

  name: str
  factor_order: int
