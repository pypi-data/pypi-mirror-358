"""
Asset-specific event types for the BriskSec Wrapper SDK.

This module provides specialized event types for different asset types.
"""

from typing import Any, Dict, Optional

from .events import Event


class AssetPortEvent(Event):
    """
    Represents an asset.port event.
    """

    def __init__(
        self,
        ip: str,
        port: str,
        protocol: str,
        service: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ):
        data = {
            "ip": ip,
            "port": port,
            "protocol": protocol,
        }

        if service:
            data["service"] = service

        super().__init__(topic="asset.port", data=data, attributes=attributes or {})


class AssetRepoEvent(Event):
    """
    Represents an asset.repo event.
    """

    def __init__(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        commit: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ):
        data = {
            "repo_url": repo_url,
        }

        if branch:
            data["branch"] = branch

        if commit:
            data["commit"] = commit

        super().__init__(topic="asset.repo", data=data, attributes=attributes or {})


class AssetDomainEvent(Event):
    """
    Represents an asset.domain event.
    """

    def __init__(
        self,
        domain: str,
        ip: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ):
        data = {
            "domain": domain,
        }

        if ip:
            data["ip"] = ip

        super().__init__(topic="asset.domain", data=data, attributes=attributes or {})


class AssetIPEvent(Event):
    """
    Represents an asset.ip event.
    """

    def __init__(
        self,
        ip: str,
        hostname: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ):
        data = {
            "ip": ip,
        }

        if hostname:
            data["hostname"] = hostname

        super().__init__(topic="asset.ip", data=data, attributes=attributes or {})


class AssetURLEvent(Event):
    """
    Represents an asset.url event.
    """

    def __init__(
        self,
        url: str,
        domain: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
    ):
        data = {
            "url": url,
        }

        if domain:
            data["domain"] = domain

        super().__init__(topic="asset.url", data=data, attributes=attributes or {})
