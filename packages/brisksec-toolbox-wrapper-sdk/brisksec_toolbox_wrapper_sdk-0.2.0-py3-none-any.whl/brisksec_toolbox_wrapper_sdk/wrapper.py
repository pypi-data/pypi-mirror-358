"""
BriskSec Toolbox Wrapper SDK for Python.

This module provides utilities for parsing tool outputs and generating events.
The Go runtime handles all the complex wrapper logic, messaging, and HTTP servers.
This SDK focuses solely on output parsing and event generation.
"""

# Re-export the main classes for backwards compatibility
from .parser import OutputParser
from .types import Event, Finding

__all__ = ["OutputParser", "Event", "Finding"]
