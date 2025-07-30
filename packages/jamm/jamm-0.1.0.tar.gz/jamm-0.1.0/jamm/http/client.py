import requests
from requests.exceptions import RequestException


class HTTPClient:
    """HTTP client with Protocol Buffer support."""

    def __init__(self, auth_handler, environment):
        self.auth = auth_handler
        self.environment = environment
        self.session = requests.Session()

        # Add default headers
        self.session.headers.update(
            {"User-Agent": f"jamm-sdk-python/{environment.version}"}
        )

        # Configure SSL verification based on environment
        self.session.verify = environment.verify_ssl

    def request(self, method, endpoint, data=None, params=None, headers=None):
        """Make an HTTP request to the API."""
        url = f"https://{self.environment.api_host}{endpoint}"

        # Get auth headers from auth handler
        auth_headers = self.auth.get_auth_headers()

        # Merge headers
        request_headers = {**self.session.headers}
        if auth_headers:
            request_headers.update(auth_headers)
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=data,
                timeout=(30, 90),  # (connect timeout, read timeout)
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            # Handle request exceptions
            raise
