"""Minimum DVH objective."""

from typing import Annotated
from pydantic import Field

from numba import njit
from numpy import logical_or, quantile, sort

from ._objective import Objective, ParameterMetadata


class MinDVH(Objective):
    """
    Minimum DVH objective.

    Attributes
    ----------
    d : float
        dose point
    v_min : float
        min. relative volume [%]
    """

    name = "Min DVH"

    d: Annotated[float, Field(default=30.0, ge=0.0), ParameterMetadata(kind="reference")]
    v_min: Annotated[
        float, Field(default=95.0, ge=0.0, le=100.0), ParameterMetadata(kind="relative_volume")
    ]

    def compute_objective(self, values):
        return _compute_objective(values, self.d, self.v_min)

    def compute_gradient(self, values):
        return _compute_gradient(values, self.d, self.v_min)


@njit
def _compute_objective(dose, d, v_min):
    deviation = dose - d
    dose_quantile = quantile(sort(dose)[::-1], v_min / 100.0)
    mask = logical_or(dose > d, dose < dose_quantile)
    deviation[mask] = 0

    return (deviation @ deviation) / len(dose)


@njit
def _compute_gradient(dose, d, v_min):
    deviation = dose - d
    dose_quantile = quantile(sort(dose)[::-1], v_min / 100.0)
    mask = logical_or(dose > d, dose < dose_quantile)
    deviation[mask] = 0
    return 2.0 * deviation / len(dose)
