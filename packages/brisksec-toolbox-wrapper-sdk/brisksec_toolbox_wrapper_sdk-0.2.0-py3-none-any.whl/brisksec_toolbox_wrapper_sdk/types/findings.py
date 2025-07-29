"""
This file is auto-generated from Go types. Do not edit manually.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Finding(BaseModel):
    """Finding represents a standardized security finding"""

    id: str

    title: str

    description: str

    severity: str  # "critical", "high", "medium", "low", "info"

    resource: str

    remediation: Optional[str] = None

    references: Optional[List[str]] = None

    metadata: Optional[Dict[str, str]] = None
