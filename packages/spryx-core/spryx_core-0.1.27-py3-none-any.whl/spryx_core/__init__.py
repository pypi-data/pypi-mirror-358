"""
spryx-core: Core utilities and types for Spryx projects.

This package provides common utilities and type definitions used across Spryx projects,
including ID generation, time handling, sentinel values, security utilities, and more.
"""

from spryx_core.constants import NOT_GIVEN
from spryx_core.enums import Environment, SortOrder
from spryx_core.errors import SpryxError, SpryxErrorDict
from spryx_core.id import EntityId, cast_entity_id, generate_entity_id, is_valid_ulid
from spryx_core.pagination import Page
from spryx_core.security.claims import AccessToken
from spryx_core.sentinels import NotGiven
from spryx_core.time import (
    end_of_day,
    now_utc,
    parse_iso,
    start_of_day,
    timestamp_from_iso,
    to_iso,
    utc_from_timestamp,
)
from spryx_core.types import NotGivenOr, default_or_given, is_given

__all__ = [
    "AccessToken",
    # Constants
    "NOT_GIVEN",
    # Enums
    "Environment",
    "SortOrder",
    # Errors
    "SpryxError",
    "SpryxErrorDict",
    # ID
    "EntityId",
    "cast_entity_id",
    "generate_entity_id",
    "is_valid_ulid",
    # Pagination
    "Page",
    # Sentinels
    "NotGiven",
    # Time
    "end_of_day",
    "now_utc",
    "parse_iso",
    "start_of_day",
    "timestamp_from_iso",
    "to_iso",
    "utc_from_timestamp",
    # Types
    "NotGivenOr",
    "default_or_given",
    "is_given",
]
