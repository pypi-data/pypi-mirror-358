from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    """
    The base model for all models

    This class should not be instantiated directly
    """

    model_config = ConfigDict(
        extra="allow", use_enum_values=True, validate_assignment=True
    )


class ResponseModel(Model, frozen=True):
    """
    The base model for all response models

    This class should not be instantiated directly
    """


class CreatePayloadModel(Model, extra="forbid"):
    """
    The base model for all create payload models

    This class should not be instantiated directly
    """

    def dump_json(self, **kwargs) -> dict[str, Any]:
        """
        Dumps the model in JSON format

        Parameters
        ----------
        kwargs : dict[str, Any]
            Additional keyword arguments to pass to the model dump

        Returns
        -------
        dict[str, Any]
            The payload
        """
        return self.model_dump(mode="json", exclude_unset=True, **kwargs)


class UpdatePayloadModel(Model, extra="forbid"):
    """
    The base model for all update payload models

    This class should not be instantiated directly
    """

    def dump_json(self, **kwargs) -> dict[str, Any]:
        """
        Dumps the model in JSON format

        Parameters
        ----------
        kwargs : dict[str, Any]
            Additional keyword arguments to pass to the model dump

        Returns
        -------
        dict[str, Any]
            The payload
        """
        return self.model_dump(mode="json", exclude_unset=True, **kwargs)
