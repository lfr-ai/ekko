"""Shared Pydantic base models for the application DTO layer."""

from pydantic import BaseModel, ConfigDict

_BASE_MODEL_CONFIG = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
    validate_assignment=True,
    validate_by_alias=True,
    validate_by_name=True,
    from_attributes=True,
)


class _ConfiguredDTOModel(BaseModel):
    """Shared configured Pydantic base model for the application DTO layer."""

    model_config = _BASE_MODEL_CONFIG


class DTOModel(_ConfiguredDTOModel):
    """Shared base for mutable Pydantic models in the application DTO layer."""


class FrozenDTOModel(_ConfiguredDTOModel):
    """Shared base for immutable Pydantic models in the application DTO layer."""

    model_config = ConfigDict(**_BASE_MODEL_CONFIG, frozen=True)
