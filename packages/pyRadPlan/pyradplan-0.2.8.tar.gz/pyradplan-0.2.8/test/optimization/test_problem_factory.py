import pytest

from pyRadPlan.plan import PhotonPlan
from pyRadPlan.optimization.problems import (
    get_available_problems,
    get_problem,
    get_problem_from_pln,
    PlanningProblem,
)


def test_get_available_problems():
    problems = get_available_problems()
    assert isinstance(problems, dict)
    assert len(problems) > 0
    assert all([isinstance(k, str) for k in problems.keys()])
    assert all([issubclass(v, PlanningProblem) for v in problems.values()])


def test_get_available_problems_with_pln_default():
    pln = PhotonPlan()
    problems = get_available_problems(pln)
    assert isinstance(problems, dict)
    assert len(problems) > 0
    assert all([isinstance(k, str) for k in problems.keys()])


def test_get_problem():
    problems = get_available_problems()
    for problem_name, problem_class in problems.items():
        problem = get_problem(problem_name)
        assert isinstance(problem, problem_class)
        assert isinstance(problem, PlanningProblem)
        assert problem.short_name == problem_name
        assert problem.name == problem_class.name
        assert problem.short_name == problem_class.short_name


def test_get_problem_from_pln_specific():
    pln = PhotonPlan(prop_opt={"problem": "nonlin_fluence", "bypass_objective_jacobian": False})
    problem = get_problem_from_pln(pln)
    assert isinstance(problem, PlanningProblem)
    assert problem.short_name == "nonlin_fluence"
    assert not problem.bypass_objective_jacobian


def test_get_problem_from_pln_invalid_warning():
    pln = PhotonPlan(prop_opt={"problem": "invalid_problem"})
    with pytest.warns(UserWarning):
        get_problem_from_pln(pln)


def test_get_problem_invalid():
    with pytest.raises(KeyError):
        get_problem("invalid_problem")
    with pytest.raises(ValueError):
        get_problem(123)
    with pytest.raises(NotImplementedError):
        get_problem({"problem": "scipy"})  # valid problem, but dict not implemented yet
