# src/utils/http_client.py

import requests

class HttpClient:
    """
    Wrapper around the requests library for consistent HTTP operations.
    Provides support for GET, POST, headers, cookies, and error handling.
    """

    def __init__(self, timeout=10, verify_ssl=True):
        self.session = requests.Session()
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def get(self, url, params=None, headers=None, cookies=None):
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            return response
        except requests.RequestException as e:
            return self._error_response(str(e))

    def post(self, url, data=None, json=None, headers=None, cookies=None):
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                cookies=cookies,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            return response
        except requests.RequestException as e:
            return self._error_response(str(e))

    def _error_response(self, message):
        """Return a mock response object for errors."""
        class ErrorResponse:
            status_code = 0
            text = ""
            content = b""

            def __init__(self, msg):
                self.error = msg

        return ErrorResponse(message)

    def set_header(self, key, value):
        self.session.headers[key] = value

    def close(self):
        self.session.close()


# Example usage (for testing only)
if __name__ == "__main__":
    client = HttpClient()
    resp = client.get("https://httpbin.org/get", params={"test": "defensys"})
    print("Status:", resp.status_code)
    print("Body:", resp.text[:200])