from typing import Union

import numpy as np

from pyRadPlan.stf import validate_stf, SteeringInformation
from pyRadPlan.ct import validate_ct, CT
from pyRadPlan.cst import validate_cst, StructureSet
from pyRadPlan.plan import validate_pln, Plan
from pyRadPlan.dij import Dij

from .engines import get_engine


def calc_dose_influence(
    ct: Union[CT, dict],
    cst: Union[StructureSet, dict],
    stf: Union[SteeringInformation, dict],
    pln: Union[Plan, dict],
) -> Dij:
    """
    Calculate the dose influence matrix.

    Parameters
    ----------
    ct : CT
        A CT object.
    cst : CST
        A CST object.
    stf : STF
        A STF object.

    Returns
    -------
    Dij
        A Dij object.
    """

    ct = validate_ct(ct)
    cst = validate_cst(cst, ct=ct)
    stf = validate_stf(stf)
    pln = validate_pln(pln)

    engine = get_engine(pln)

    dij = engine.calc_dose_influence(ct, cst, stf)
    return dij


def calc_dose_forward(
    ct: Union[CT, dict],
    cst: Union[StructureSet, dict],
    stf: Union[SteeringInformation, dict],
    pln: Union[Plan, dict],
    weights: np.ndarray = None,
) -> Dij:
    """
    Calculate the dose forward matrix.

    Parameters
    ----------
    ct : CT
        A CT object.
    cst : CST
        A CST object.
    stf : STF
        A STF object.
    weights : np.ndarray
        The weights for the beamlets.

    Returns
    -------
    PlanResult
        A PlanResult object.
    """
    ct = validate_ct(ct)
    cst = validate_cst(cst, ct=ct)
    stf = validate_stf(stf)
    pln = validate_pln(pln)

    engine = get_engine(pln)

    dij = engine.calc_dose_forward(ct, cst, stf, weights)
    return dij
