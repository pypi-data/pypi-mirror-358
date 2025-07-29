"""
BriskSec Toolbox Wrapper SDK Parser Module.

This module provides the base class for implementing output parsers that convert
tool output to events and findings. This is the core functionality of the SDK.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .types import Event, Finding


class OutputParser:
    """Base class for tool output parsers.

    This class provides the base functionality for parsing tool output and converting
    it to events and findings. The Go runtime handles all message routing, HTTP servers,
    and pub/sub logic - this focuses purely on parsing.
    """

    def __init__(self) -> None:
        """Initialize the parser."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_output(
        self, output: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Union[Event, Finding]]]:
        """Parse tool output and convert it to events and findings.

        Args:
            output: The tool output to parse.
            metadata: Additional metadata to include in the events/findings.

        Returns:
            A dictionary containing lists of events and findings:
            {
                "events": [Event, ...],
                "findings": [Finding, ...]
            }
        """
        raise NotImplementedError("Subclasses must implement parse_output")

    def parse_to_events(
        self, output: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Union[Event, Finding]]:
        """Parse tool output and convert it to events only.

        Args:
            output: The tool output to parse.
            metadata: Additional metadata to include in the events.

        Returns:
            A list of events.
        """
        result = self.parse_output(output, metadata)
        return result.get("events", [])

    def parse_to_findings(
        self, output: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Union[Event, Finding]]:
        """Parse tool output and convert it to findings only.

        Args:
            output: The tool output to parse.
            metadata: Additional metadata to include in the findings.

        Returns:
            A list of findings.
        """
        result = self.parse_output(output, metadata)
        return result.get("findings", [])
