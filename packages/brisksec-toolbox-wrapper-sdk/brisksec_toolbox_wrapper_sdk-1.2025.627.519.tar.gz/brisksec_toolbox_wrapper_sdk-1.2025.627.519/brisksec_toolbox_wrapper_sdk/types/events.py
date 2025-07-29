"""
This file is auto-generated from Go types. Do not edit manually.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Event represents a follow-up event that can be published to a Pub/Sub topic"""

    topic: str

    data: Dict[str, Any]

    attributes: Optional[Dict[str, str]] = None
