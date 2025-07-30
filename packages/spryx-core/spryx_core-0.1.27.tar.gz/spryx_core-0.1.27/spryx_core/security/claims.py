from datetime import datetime
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, model_validator

UTC = ZoneInfo("UTC")


class _CoreModel(BaseModel):
    """Shared Pydantic config for core models."""

    model_config = {
        "extra": "forbid",
        "frozen": True,  # immutable instances
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


class TokenType(str, Enum):
    USER = "user"
    APP = "app"


class Meta(_CoreModel):
    token_type: TokenType
    sid: str | None = None


class PltContext(_CoreModel):
    role_id: str
    scopes: list[str]


class OrgContext(_CoreModel):
    id: str
    role_id: str
    status: Optional[str] = None
    scopes: list[str]


class AccessToken(_CoreModel):
    # Registered
    iss: str
    sub: str
    aud: str | list[str]
    iat: datetime
    exp: datetime
    nbf: datetime | None = None
    jti: str

    # Custom
    ver: int = Field(1, description="Schema version")
    meta: Meta
    plt_context: PltContext | None = None
    org_context: OrgContext | None = None

    @model_validator(mode="after")
    def _check_exp(self):
        """Validate that the token hasn't expired."""
        if self.exp < datetime.now(UTC):
            raise ValueError("token already expired")
        return self
