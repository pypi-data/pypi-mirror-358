import requests
import time
import logging
from .logger import setup_logger
from typing import Union, IO
import mimetypes

CIQ_HOST = "https://datahub.ninebit.in"


class NineBitCIQClient:
    """
    Client for interacting with the NineBit CIQ backend.

    Parameters:
        base_url (str): Base URL of the CIQ API.
        api_key (str): API key for authentication (sent in 'X-API-Key' header).
        log_level (int): Logging level (default logging.ERROR).
    """

    def __init__(self, api_key: str, base_url: str = CIQ_HOST, log_level=logging.ERROR):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False  # TODO: SSL
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
            return response.json().get("content")
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

    def ingest_file(self, file: Union[str, IO[bytes]], bucket_name: str, object_name: str, content_type: str = None):
        """
        Reads and uploads a PDF or DOCX file to the backend for processing.

        Args:
            file (Union[str, IO[bytes]]):
                - Local file path as a string, or
                - File-like object (e.g., BytesIO) with file content.

        Returns:
            dict: Response from the backend.

        Raises:
            ValueError: If the input is invalid or unsupported.
            IOError: If the file cannot be read.
        """
        # Determine file name (only used for content type inference)
        if isinstance(file, str):
            filename = file
        elif hasattr(file, "name"):
            filename = file.name
        else:
            filename = "unknown"

        # Infer content type if not explicitly provided
        if content_type is None:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        # Step 1: Get the pre-signed URL from the backend
        try:
            response = self.session.post(
                f"{self.base_url}/workflow-service/generate-presigned-url",
                json={"bucket_name": bucket_name, "object_name": object_name, "content_type": content_type},
            )
            response.raise_for_status()
            presigned_url = response.json()["url"]
            self.logger.info(f"Presigned_url: {presigned_url}")
        except Exception as e:
            self.logger.error(f"Failed to get pre-signed URL: {e}")
            return False

        # Step 2: Upload the file to MinIO via the pre-signed URL
        try:
            if isinstance(file, str):
                with open(file, "rb") as f:
                    data = f.read()
            else:
                file.seek(0)
                data = file.read()

            upload_response = requests.put(
                presigned_url, data=data, verify=False, headers={"Content-Type": content_type}  # TODO: SSL
            )

            if upload_response.status_code == 200:
                self.logger.info("File uploaded successfully.")
                return True
            else:
                self.logger.error(f"Upload failed: {upload_response.status_code} - {upload_response.text}")
                return False

        except Exception as e:
            self.logger.error(f"File upload error: {e}")
            return False
