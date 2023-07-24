"""Class to manage the connection with the server."""
import time

import requests


class RestapiConnection:
    """Internal auxiliary class that handles the base connection."""

    def __init__(self, host, port):
        """Initialize internal variables."""
        self._baseurl = f'http://{host}:{port}'
        self._auth_header = None

    def authenticate(self, username, password):
        """Authenticate the connection with the server."""
        request_url = self._baseurl + '/user_management/authenticate/'
        request_data = {
            'username': username,
            'password': password,
            'grant_type': 'password',
        }
        request_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_response = requests.post(
            request_url,
            data=request_data,
            headers=request_headers,
        )
        token_response = token_response.json()
        token_object = token_response['access_token']
        token_type = token_response['token_type']
        auth_header = {
            'accept': 'application/json',
            'Authorization': f'{token_type} {token_object}'
        }
        self._auth_header = auth_header
        return auth_header

    def auth_get(self, endpoint, params=None):
        """GET with authorized credentials."""
        full_url = self._baseurl + endpoint
        kwargs = {}
        if params is not None:
            kwargs['params'] = params
        return requests.get(full_url, **kwargs)

    def auth_post(self, endpoint, data_raw=None, data_json=None, params=None):
        """POST with authorized credentials."""
        full_url = self._baseurl + endpoint
        kwargs = {}
        if data_raw is not None:
            kwargs['data'] = data_raw
        if data_json is not None:
            kwargs['json'] = data_json
        if params is not None:
            kwargs['params'] = params
        return requests.post(full_url, **kwargs)


class FinalesClient:
    """Class to manage the connection with the server."""

    def __init__(self, host, port, execution_delay=0.1):
        """Initialize internal variables."""
        self._execution_delay = execution_delay
        self._connection = RestapiConnection(host, port)

    def authenticate(self, username, password):
        """Authenticate the connection with the server."""
        time.sleep(self.execution_delay)
        return self._connection.authenticate(username, password)

    def get_pending_requests(self, quantity, method):
        """Return the pending requests."""
        time.sleep(self.execution_delay)
        endpoint = '/pending_requests/'
        params = {'quantity': quantity, 'method': method}
        response = self._connection.auth_get(endpoint, params=params)
        return response.json()

    def post_request(self, data):
        """Post a request to the server."""
        time.sleep(self.execution_delay)
        endpoint = '/requests/'
        response = self._connection.auth_post(endpoint, data=data)
        return response.json()

    def post_result(self, data, request_id):
        """Post a result to the server."""
        time.sleep(self.execution_delay)
        endpoint = '/post_result/'
        params = {'request_id': request_id}
        response = self._connection.auth_post(endpoint,
                                              data=data,
                                              params=params)
        return response.json()
