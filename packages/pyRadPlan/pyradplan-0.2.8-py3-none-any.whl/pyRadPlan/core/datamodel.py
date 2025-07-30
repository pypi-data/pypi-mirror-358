"""Basic Model for all pyRadPlan Datastructures."""

from typing import Any, Union
import numpy as np
from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
)
from pydantic.alias_generators import to_camel
from copy import deepcopy


class PyRadPlanBaseModel(BaseModel):
    """
    Base class for all pyRadPlan data structures.

    Especially useful for structures that should be matRad compatible.
    Extends Pydantic's BaseModel to use pydantic validation and serialization.

    Attributes
    ----------
    model_config : ConfigDict
        Configuration for the model, including alias generation, population by
        name, arbitrary types allowed, assignment validation, and attribute
        creation from dictionary.
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(alias=to_camel),
        populate_by_name=True,  # Allows both snake_case and camelCase attributes
        arbitrary_types_allowed=True,  # Allows arbitrary types in the model (will be casted)
        validate_assignment=True,  # Validate assignment of values to fields
        # (not only during construction)
        from_attributes=True,  # Allows to create a model from a dictionary
    )

    def __eq__(self, other: Any) -> bool:
        """
        Specialized __eq__ method to compare two pyRadPlanBaseModel instances.

        It first tries to compare the instances using the super().__eq__ method.
        If this fails, it compares the dictionaries. This is due to some issues
        comparing numpy arrays within the models.
        """
        try:
            return super().__eq__(other)
        except ValueError:
            if self.__dict__.keys() != other.__dict__.keys():
                return False
            stack = [(self.__dict__, other.__dict__)]
            while stack:
                dict_a, dict_b = stack.pop()
                if dict_a.keys() != dict_b.keys():
                    return False
                for key in dict_a:
                    if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                        stack.append((dict_a[key], dict_b[key]))
                    elif isinstance(dict_a[key], np.ndarray) and isinstance(
                        dict_b[key], np.ndarray
                    ):
                        if not np.array_equal(dict_a[key], dict_b[key]):
                            return False
                    elif dict_a[key] != dict_b[key]:
                        return False
            return True

    def __ne__(self, other: Any) -> bool:
        """
        Specialized __ne__ method to compare two PyRadPlanBaseModel instances.

        This method returns the negation of the __eq__ method.
        """
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        else:
            return True

    def to_matrad(self, context: Union[str, dict] = "mat-file") -> Any:
        """
        Perform matRad compatible serialization.

        Parameters
        ----------
        context : str, optional
            The context in which the datastructure should be serialized,
            by default 'mat-file'.

        Returns
        -------
        Any
            A datastructre compatible with matRad in the given context

        Notes
        -----
        Currently, the only supported context is 'mat-file'. In the future,
        this could be extended to support other contexts, such as direct
        calling via the matlab engine or oct2py.
        """
        self_copy = deepcopy(self)
        if isinstance(context, dict):
            if "matRad" not in context:
                context.update({"matRad": "mat-file"})
        else:
            context = {"matRad": context}

        if context["matRad"] != "mat-file":
            raise ValueError(f"Context {context} not supported")

        # Standard is a model_dump using above alias and context information
        return self_copy.model_dump(by_alias=True, context=context)
