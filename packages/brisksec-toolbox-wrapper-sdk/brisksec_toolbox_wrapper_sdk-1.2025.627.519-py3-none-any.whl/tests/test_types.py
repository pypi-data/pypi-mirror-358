"""
Tests for the types module.
"""

import unittest

from brisksec_toolbox_wrapper_sdk.types import (
    AssetDomainEvent,
    AssetIPEvent,
    AssetPortEvent,
    AssetRepoEvent,
    AssetURLEvent,
    Event,
    Finding,
)


class TestFinding(unittest.TestCase):
    """
    Tests for the Finding class.
    """

    def test_finding_to_dict(self):
        """
        Test the to_dict method of the Finding class.
        """
        finding = Finding(
            id="test-id",
            title="Test Finding",
            description="This is a test finding",
            severity="high",
            resource="test-resource",
            remediation="Fix the issue",
            references=["https://example.com"],
            metadata={"key": "value"},
        )

        expected = {
            "id": "test-id",
            "title": "Test Finding",
            "description": "This is a test finding",
            "severity": "high",
            "resource": "test-resource",
            "remediation": "Fix the issue",
            "references": ["https://example.com"],
            "metadata": {"key": "value"},
        }

        self.assertEqual(finding.model_dump(exclude_none=True), expected)

    def test_finding_to_dict_minimal(self):
        """
        Test the to_dict method of the Finding class with minimal fields.
        """
        finding = Finding(
            id="test-id",
            title="Test Finding",
            description="This is a test finding",
            severity="high",
            resource="test-resource",
        )

        expected = {
            "id": "test-id",
            "title": "Test Finding",
            "description": "This is a test finding",
            "severity": "high",
            "resource": "test-resource",
        }

        self.assertEqual(finding.model_dump(exclude_none=True), expected)


class TestEvent(unittest.TestCase):
    """
    Tests for the Event class.
    """

    def test_event_to_dict(self):
        """
        Test the to_dict method of the Event class.
        """
        event = Event(
            topic="test-topic", data={"key": "value"}, attributes={"attr": "value"}
        )

        expected = {
            "topic": "test-topic",
            "data": {"key": "value"},
            "attributes": {"attr": "value"},
        }

        self.assertEqual(event.model_dump(exclude_none=True), expected)


class TestAssetEvents(unittest.TestCase):
    """
    Tests for the asset event classes.
    """

    def test_asset_port_event(self):
        """
        Test the AssetPortEvent class.
        """
        event = AssetPortEvent(
            ip="192.168.1.1",
            port="80",
            protocol="tcp",
            service="http",
            attributes={"attr": "value"},
        )

        expected = {
            "topic": "asset.port",
            "data": {
                "ip": "192.168.1.1",
                "port": "80",
                "protocol": "tcp",
                "service": "http",
            },
            "attributes": {"attr": "value"},
        }

        self.assertEqual(event.model_dump(exclude_none=True), expected)

    def test_asset_repo_event(self):
        """
        Test the AssetRepoEvent class.
        """
        event = AssetRepoEvent(
            repo_url="https://github.com/example/repo",
            branch="main",
            commit="abc123",
            attributes={"attr": "value"},
        )

        expected = {
            "topic": "asset.repo",
            "data": {
                "repo_url": "https://github.com/example/repo",
                "branch": "main",
                "commit": "abc123",
            },
            "attributes": {"attr": "value"},
        }

        self.assertEqual(event.model_dump(exclude_none=True), expected)

    def test_asset_domain_event(self):
        """
        Test the AssetDomainEvent class.
        """
        event = AssetDomainEvent(
            domain="example.com", ip="192.168.1.1", attributes={"attr": "value"}
        )

        expected = {
            "topic": "asset.domain",
            "data": {"domain": "example.com", "ip": "192.168.1.1"},
            "attributes": {"attr": "value"},
        }

        self.assertEqual(event.model_dump(exclude_none=True), expected)

    def test_asset_ip_event(self):
        """
        Test the AssetIPEvent class.
        """
        event = AssetIPEvent(
            ip="192.168.1.1", hostname="example.com", attributes={"attr": "value"}
        )

        expected = {
            "topic": "asset.ip",
            "data": {"ip": "192.168.1.1", "hostname": "example.com"},
            "attributes": {"attr": "value"},
        }

        self.assertEqual(event.model_dump(exclude_none=True), expected)

    def test_asset_url_event(self):
        """
        Test the AssetURLEvent class.
        """
        event = AssetURLEvent(
            url="https://example.com/path",
            domain="example.com",
            attributes={"attr": "value"},
        )

        expected = {
            "topic": "asset.url",
            "data": {"url": "https://example.com/path", "domain": "example.com"},
            "attributes": {"attr": "value"},
        }

        self.assertEqual(event.model_dump(exclude_none=True), expected)


if __name__ == "__main__":
    unittest.main()
