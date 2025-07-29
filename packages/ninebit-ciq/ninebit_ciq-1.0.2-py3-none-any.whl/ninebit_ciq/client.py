import requests
import time
import logging
from .logger import setup_logger


class NineBitCIQClient:
    """
    Client for interacting with the NineBit CIQ backend.

    Parameters:
        base_url (str): Base URL of the CIQ API.
        api_key (str): API key for authentication (sent in 'X-API-Key' header).
        log_level (int): Logging level (default logging.ERROR).
    """

    def __init__(self, base_url: str, api_key: str, log_level=logging.ERROR):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key, "Content-Type": "application/json"})
        self.logger = setup_logger(log_level)

    def get_design_time_workflow(self):
        """Fetch design time workflow JSON from the backend."""
        try:
            url = f"{self.base_url}/workflow-service/dt/workflows"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching design time workflow: {e}")
            raise

    def trigger_workflow(self, workflow_data: dict):
        """Trigger a workflow with given data, return workflow ID."""
        try:
            url = f"{self.base_url}/workflow-service/trigger_workflow"
            response = self.session.post(url, json=workflow_data, timeout=10)
            response.raise_for_status()
            return response.json().get("wf_id")
        except requests.RequestException as e:
            self.logger.error(f"Error triggering workflow: {e}")
            raise

    def get_workflow_status(self, wf_id: str):
        """Check status and result of a workflow by its workflow ID."""
        try:
            url = f"{self.base_url}/workflow-service/rt/workflows/{wf_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error getting workflow status: {e}")
            raise

    def wait_for_completion(self, wf_id: str, interval: int = 5, timeout: int = 300):
        """
        Polls workflow status until it completes or times out.

        Args:
            wf_id (str): Workflow ID to track.
            interval (int): Seconds between polls (default: 5).
            timeout (int): Max seconds to wait (default: 300).

        Returns:
            dict: Final status payload.

        Raises:
            TimeoutError: If workflow doesn't finish within the timeout.
            RuntimeError: If workflow failed.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_workflow_status(wf_id)
            state = status.get("state") or status.get("status")
            self.logger.info(f"Workflow {wf_id} state: {state}")

            if state in ("completed", "success"):
                return status
            if state in ("failed", "error"):
                raise RuntimeError(f"Workflow {wf_id} failed: {status}")

            time.sleep(interval)

        raise TimeoutError(f"Workflow {wf_id} did not complete in {timeout} seconds.")
