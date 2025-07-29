"""
Example of how to integrate the Python SDK with the Go runtime.

This script demonstrates how the Go runtime would call into Python code
and how the Python code would respond.
"""

import json
import logging
import sys
from typing import Any, Dict, List, Tuple

from brisksec import AssetPortEvent, BaseWrapper, Event, Finding


class ExampleWrapper(BaseWrapper):
    """
    Example wrapper implementation.
    """

    def __init__(self):
        """
        Initialize the example wrapper.
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename="example_wrapper.log",
        )
        logger = logging.getLogger("ExampleWrapper")

        super().__init__(logger)

    def handle_SCAN(
        self, parameters: Dict[str, Any]
    ) -> Tuple[List[Finding], List[Event]]:
        """
        Handle the SCAN operation.

        Args:
            parameters: The parameters for the operation.

        Returns:
            A tuple of (findings, events).
        """
        self.logger.info(f"Handling SCAN operation with parameters: {parameters}")

        # Get the target from the parameters
        target = parameters.get("target", "")
        if not target:
            self.logger.error("No target in parameters")
            return [], []

        # Get the stdout from the parameters (if any)
        stdout = parameters.get("stdout", "")

        # Create some findings
        findings = [
            Finding(
                id="example-finding-1",
                title="Example Finding 1",
                description="This is an example finding",
                severity="medium",
                resource=target,
                metadata={"target": target, "stdout_size": len(stdout)},
            ),
            Finding(
                id="example-finding-2",
                title="Example Finding 2",
                description="This is another example finding",
                severity="low",
                resource=target,
                metadata={"target": target, "stdout_size": len(stdout)},
            ),
        ]

        # Create some events
        events = [
            AssetPortEvent(ip=target, port="80", protocol="tcp", service="http"),
            AssetPortEvent(ip=target, port="443", protocol="tcp", service="https"),
        ]

        return findings, events

    def handle_default(
        self, parameters: Dict[str, Any]
    ) -> Tuple[List[Finding], List[Event]]:
        """
        Handle the default operation.

        Args:
            parameters: The parameters for the operation.

        Returns:
            A tuple of (findings, events).
        """
        self.logger.warning(f"Default handler called with parameters: {parameters}")
        return [], []


def simulate_go_runtime():
    """
    Simulate the Go runtime calling into Python.
    """
    # Create the wrapper
    wrapper = ExampleWrapper()

    # Start the wrapper
    wrapper.start()

    try:
        # Simulate the Go runtime sending a request
        request = {
            "operation": "SCAN",
            "parameters": {
                "target": "192.168.1.1",
                "stdout": "Example output from a tool",
            },
        }

        # Send the request to stdin
        sys.stdin = open("request.json", "w+")
        json.dump(request, sys.stdin)
        sys.stdin.write("\n")
        sys.stdin.flush()
        sys.stdin.seek(0)

        # Capture stdout
        sys.stdout = open("response.json", "w+")

        # Wait for the response
        import time

        time.sleep(1)

        # Read the response
        sys.stdout.seek(0)
        response = json.load(sys.stdout)

        # Print the response
        print("Response:")
        print(json.dumps(response, indent=2))

    finally:
        # Stop the wrapper
        wrapper.stop()

        # Reset stdin and stdout
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    # If run directly, simulate the Go runtime
    simulate_go_runtime()

    # If imported, just create and start the wrapper
    # This is how it would be used in a real scenario
    wrapper = ExampleWrapper()
    wrapper.start()
