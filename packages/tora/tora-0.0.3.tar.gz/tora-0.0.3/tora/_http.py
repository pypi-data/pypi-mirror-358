import http.client
import json as _json
from typing import Any
from urllib.parse import urlparse


class HTTPStatusError(Exception):
    """Custom exception for HTTP errors."""

    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


class HttpResponse:
    """A wrapper for http.client.HTTPResponse."""

    def __init__(self, raw_response, data, url):
        self._raw_response = raw_response
        self.status_code = raw_response.status
        self.text = data.decode("utf-8")
        self._url = url
        self._json = None

    def json(self):
        """Returns the JSON-decoded content of the response."""
        if self._json is None:
            self._json = _json.loads(self.text)
        return self._json

    def raise_for_status(self):
        """Raises HTTPStatusError for 4xx and 5xx responses."""
        if 400 <= self.status_code < 600:
            raise HTTPStatusError(
                f"Client error '{self.status_code} {self._raw_response.reason}' for url '{self._url}'",
                response=self,
            )


class HttpClient:
    """
    A simple HTTP client that wraps http.client, with an interface
    similar to requests or httpx.
    """

    def __init__(self, base_url: str, headers: dict | None = None):
        parsed_url = urlparse(base_url)
        self.scheme = parsed_url.scheme
        self.netloc = parsed_url.netloc
        self.base_path = parsed_url.path.rstrip("/")

        if self.scheme == "https":
            self.conn_class = http.client.HTTPSConnection
        else:
            self.conn_class = http.client.HTTPConnection

        self.headers = headers or {}
        self.conn = None

    def _get_conn(self, timeout=None):
        if self.conn:
            return self.conn
        return self.conn_class(self.netloc, timeout=timeout)

    def _request(
        self,
        method: str,
        path: str,
        body=None,
        headers: dict | None = None,
        timeout: int | None = None,
    ):
        conn = self._get_conn(timeout=timeout)

        full_path = self.base_path + path

        final_headers = self.headers.copy()
        if headers:
            final_headers.update(headers)

        try:
            conn.request(method, full_path, body, headers=final_headers)
            response = conn.getresponse()
            data = response.read()
        except Exception:
            if self.conn is None:
                conn.close()
            raise

        if self.conn is None:
            conn.close()

        url = f"{self.scheme}://{self.netloc}{full_path}"
        return HttpResponse(response, data, url)

    def get(self, path: str, headers: dict | None = None):
        """Sends a GET request."""
        return self._request("GET", path, headers=headers)

    def post(
        self,
        path: str,
        json: Any = None,
        data=None,
        headers: dict | None = None,
        timeout: int | None = None,
    ):
        """Sends a POST request."""
        body = None
        request_headers = {}
        if headers:
            request_headers.update(headers)

        if json is not None:
            body = _json.dumps(json).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        elif data is not None:
            body = data

        return self._request(
            "POST", path, body=body, headers=request_headers, timeout=timeout
        )

    def close(self):
        """Closes the connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.conn = self._get_conn()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
