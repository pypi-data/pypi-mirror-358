"""
BriskSec Toolbox Wrapper SDK for Python.

This package provides a simple SDK for parsing tool outputs and generating events.
The Go runtime handles all the complex wrapper logic, messaging, and HTTP servers.
"""

# Core parser class
from .parser import OutputParser

# Types (auto-generated from Go types via tools/typegen)
from .types import (
    AssetDomainEvent,
    AssetIPEvent,
    AssetPortEvent,
    AssetRepoEvent,
    AssetURLEvent,
    Event,
    Finding,
)

__all__ = [
    # Core functionality
    "OutputParser",
    # Types
    "Finding",
    "Event",
    "AssetPortEvent",
    "AssetRepoEvent",
    "AssetDomainEvent",
    "AssetIPEvent",
    "AssetURLEvent",
]
