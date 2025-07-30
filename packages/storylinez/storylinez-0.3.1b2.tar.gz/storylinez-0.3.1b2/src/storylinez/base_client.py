import requests
import time
from typing import Dict, Any

class BaseClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str, default_org_id: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.default_org_id = default_org_id

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json",
        }

    def _make_request(
        self,
        method: str,
        url: str,
        params: Dict = None,
        json_data: Dict = None,
        json: Dict = None,
        data: Any = None,
        files: Dict = None,
        headers: Dict = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict:
        """
        Make an HTTP request with support for JSON payloads.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): The URL to send the request to.
            params (Dict, optional): Query parameters.
            json_data (Dict, optional): JSON data to send in the request body. Takes precedence over 'json' if both are provided.
            json (Dict, optional): Alternative keyword for JSON data. Used if 'json_data' is not provided.
            data (Any, optional): Data to send in the request body (for non-JSON payloads).
            files (Dict, optional): Files to upload.
            headers (Dict, optional): Additional headers.
            max_retries (int, optional): Maximum number of retries for network errors.
            retry_delay (float, optional): Initial delay between retries in seconds.

        Returns:
            Dict: The JSON response from the API.

        Raises:
            Exception: If the request fails after retries or returns an error status.
        """
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        # Prefer json_data if both are provided
        json_payload = json_data if json_data is not None else json

        retries = 0
        while True:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_payload,
                    data=data,
                    files=files,
                    headers=request_headers
                )
                
                if response.status_code >= 400:
                    error_message = f"API request failed with status {response.status_code}"
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_message = f"{error_message}: {error_data['error']}"
                    except:
                        if response.text:
                            error_message = f"{error_message}: {response.text}"
                    raise Exception(error_message)
                return response.json()
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout, 
                    requests.exceptions.RequestException) as e:
                retries += 1
                if retries > max_retries:
                    raise Exception(f"Maximum retry attempts reached after network errors: {str(e)}")
                
                # Exponential backoff
                wait_time = retry_delay * (2 ** (retries - 1))
                time.sleep(wait_time)
                continue
