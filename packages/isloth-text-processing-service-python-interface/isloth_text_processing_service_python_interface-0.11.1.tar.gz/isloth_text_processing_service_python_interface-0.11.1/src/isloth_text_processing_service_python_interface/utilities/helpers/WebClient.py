"""
web_client.py
-------------
Provides an HTTP client for service-to-service communication with support for
GET, POST, PATCH, DELETE, file upload, and structured error handling.
"""

from typing import Optional, Any, Dict
import requests


class WebClient:
    """
    WebClient for making HTTP requests to internal/external services.

    Attributes
    ----------
    service_name : str
        Name of the target service for error reporting.
    base_url : str
        Base URL for all HTTP requests.
    """

    def __init__(self, service_name: str, base_url: str):
        self._service_name = service_name
        self._base_url = base_url
        self._default_headers = {'Content-Type': 'application/json'}
        self._session = requests.Session()
        self._session.headers.update(self._default_headers)

    def _get_headers(self, auth_token: Optional[str] = None) -> Dict[str, str]:
        """
        Constructs headers including Authorization if provided.

        Parameters
        ----------
        auth_token : Optional[str]
            Bearer token to include.

        Returns
        -------
        Dict[str, str]
            HTTP headers with or without Authorization.
        """
        headers = self._default_headers.copy()
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        return headers

    def get(self, uri: str, auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a GET request to the given URI.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        try:
            return self._session.get(f"{self._base_url}{uri}", headers=self._get_headers(auth_token))
        except Exception as e:
            raise self._handle_error("GET", uri, e)

    def post(self, uri: str, data: dict, auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a POST request with JSON data.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        data : dict
            JSON body to send.
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        try:
            return self._session.post(
                f"{self._base_url}{uri}",
                json=data,
                headers=self._get_headers(auth_token)
            )
        except Exception as e:
            raise self._handle_error("POST", uri, e)

    def post_with_files(self, uri: str, data: dict, files: Dict[str, Any], auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a POST request with form-data including files.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        data : dict
            Form fields.
        files : Dict[str, Any]
            Files to upload.
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        headers = self._get_headers(auth_token)
        headers.pop("Content-Type", None)  # Let requests auto-set boundary
        try:
            return self._session.post(
                f"{self._base_url}{uri}",
                data=data,
                files=files,
                headers=headers
            )
        except Exception as e:
            raise self._handle_error("POST FILE", uri, e)

    def patch(self, uri: str, data: dict, auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a PATCH request with JSON body.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        data : dict
            JSON payload.
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        try:
            return self._session.patch(
                f"{self._base_url}{uri}",
                json=data,
                headers=self._get_headers(auth_token)
            )
        except Exception as e:
            raise self._handle_error("PATCH", uri, e)

    def patch_with_files(self, uri: str, data: dict, files: Dict[str, Any], auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a PATCH request with form-data including files.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        data : dict
            Form fields.
        files : Dict[str, Any]
            Files to upload.
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        headers = self._get_headers(auth_token)
        headers.pop("Content-Type", None)
        try:
            return self._session.patch(
                f"{self._base_url}{uri}",
                data=data,
                files=files,
                headers=headers
            )
        except Exception as e:
            raise self._handle_error("PATCH FILE", uri, e)

    def delete(self, uri: str, auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a DELETE request.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        try:
            return self._session.delete(
                f"{self._base_url}{uri}",
                headers=self._get_headers(auth_token)
            )
        except Exception as e:
            raise self._handle_error("DELETE", uri, e)

    def get_with_params(self, uri: str, params: dict, auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a GET request with query parameters.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        params : dict
            Query string parameters.
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        try:
            return self._session.get(
                f"{self._base_url}{uri}",
                headers=self._get_headers(auth_token),
                params=params
            )
        except Exception as e:
            raise self._handle_error("GET PARAMS", uri, e)

    def get_with_cookies(self, uri: str, cookies: str, auth_token: Optional[str] = None) -> requests.Response:
        """
        Sends a GET request with custom cookies.

        Parameters
        ----------
        uri : str
            API path (relative to base URL).
        cookies : str
            Raw cookie string (e.g., 'a=A; b=B').
        auth_token : Optional[str]
            Optional bearer token.

        Returns
        -------
        requests.Response
            The raw HTTP response object.
        """
        headers = self._get_headers(auth_token)
        headers['Cookie'] = cookies
        try:
            return self._session.get(
                f"{self._base_url}{uri}",
                headers=headers
            )
        except Exception as e:
            raise self._handle_error("GET COOKIE", uri, e)

    def _handle_error(self, method: str, uri: str, error: Exception) -> RuntimeError:
        """
        Generic exception handler for failed requests.

        Parameters
        ----------
        method : str
            HTTP method used.
        uri : str
            Target URI.
        error : Exception
            Original raised exception.

        Returns
        -------
        RuntimeError
            Error with contextual message.
        """
        return RuntimeError(f"{method} request to {self._service_name}{uri} failed: {error}")
