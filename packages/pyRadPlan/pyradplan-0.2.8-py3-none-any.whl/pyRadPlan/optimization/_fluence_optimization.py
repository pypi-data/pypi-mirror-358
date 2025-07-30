import numpy as np

from pyRadPlan.ct import CT, validate_ct
from pyRadPlan.cst import StructureSet, validate_cst
from pyRadPlan.plan import Plan, validate_pln
from pyRadPlan.dij import Dij, validate_dij
from pyRadPlan.stf import SteeringInformation, validate_stf

from .problems import get_problem_from_pln


def fluence_optimization(
    ct: CT, cst: StructureSet, stf: SteeringInformation, dij: Dij, pln: Plan
) -> np.ndarray:
    """
    Trigger fluence optimization using the configuration stored in the pln object.

    Parameters
    ----------
    ct : CT
        CT object.
    cst : StructureSet
        StructureSet object.
    stf : SteeringInformation
        SteeringInformation object.
    dij : Dij
        Dij object.
    pln : Plan
        Plan object.

    Returns
    -------
    np.ndarray
        The optimized fluence map.
    """

    _ct = validate_ct(ct)
    _cst = validate_cst(cst)
    _stf = validate_stf(stf)
    _dij = validate_dij(dij)
    _pln = validate_pln(pln)

    planning_prob = get_problem_from_pln(_pln)

    x, _result_info = planning_prob.solve(_ct, _cst, _stf, _dij)

    return x
