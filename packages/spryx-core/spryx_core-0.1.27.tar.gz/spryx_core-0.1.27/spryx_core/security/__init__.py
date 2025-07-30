"""
Security utilities for Spryx projects.

This module provides security-related functionality like permission handling,
token claims, and related utilities.
"""

from spryx_core.security.claims import AccessToken

__all__ = [
    "AccessToken",
]
