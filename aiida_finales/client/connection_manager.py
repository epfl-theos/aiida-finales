"""Class to manage the connection with the server."""
import time

import requests


class ConnectionManager:
    """Class to manage the connection with the server."""

    def __init__(self, username, password, ipurl, port):
        """Initialize internal variables."""
        self._baseurl = f'http://{ipurl}:{port}'
        self._username = username
        self._password = password
        self._auth_header = None

    def authenticate(self):
        """Authenticate the connection with the server."""
        time.sleep(5)
        request_url = self._baseurl + '/token'
        token_response = requests.post(
            request_url,
            data={
                'username': self._username,
                'password': self._password,
                'grant_type': 'password',
            },
            headers={'content-type': 'application/x-www-form-urlencoded'},
        )
        token_response = token_response.json()
        token = token_response['access_token']
        auth_header = {'Authorization': f'Bearer {token}'}
        self._auth_header = auth_header
        return auth_header

    def get_pending_requests(self, params):
        """Return the pending requests for measurements."""
        time.sleep(0.1)
        request_url = self._baseurl + '/api/broker/get/pending'
        request_response = requests.get(request_url,
                                        params=params,
                                        headers=self._auth_header)
        return request_response.json()

    def post_measurment(self, request_id, json_data):
        """Post a measurement result to the server."""
        time.sleep(0.1)
        request_url = self._baseurl + '/api/broker/post/measurement'
        request_response = requests.post(
            request_url,
            data=json_data,
            params={'request_id': request_id},
            headers=self._auth_header,
        )
        return request_response.json()

    def post_request(self, json_data):
        """Post a measurement request to the server."""
        time.sleep(0.1)
        request_url = self._baseurl + '/api/broker/request/measurement'
        request_response = requests.post(request_url,
                                         data=json_data,
                                         headers=self._auth_header)
        return request_response.json()

    def get_chemicals(self):
        """Get a list with all the chemicals."""
        time.sleep(0.1)
        request_url = self._baseurl + '/api/broker/get/all_chemicals'
        request_response = requests.get(request_url, headers=self._auth_header)
        return request_response.json()
