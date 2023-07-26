"""Class to manage the connection with the server."""
import time

from pydantic import BaseModel
import requests
import yaml  # consider strictyaml for automatic schema validation


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
        if token_response.status_code == 401:
            raise ValueError('Wrong username / password.')
        elif token_response.status_code != 200:
            raise RuntimeError()('Problem with authentication.')

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
        kwargs = {'headers': self._auth_header}
        if params is not None:
            kwargs['params'] = params
        return requests.get(full_url, **kwargs)

    def auth_post(self, endpoint, data_raw=None, data_json=None, params=None):
        """POST with authorized credentials."""
        full_url = self._baseurl + endpoint
        kwargs = {'headers': self._auth_header}
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
        time.sleep(self._execution_delay)
        return self._connection.authenticate(username, password)

    def get_pending_requests(self, quantity=None, method=None):
        """Return the pending requests."""
        time.sleep(self._execution_delay)
        endpoint = '/pending_requests/'
        params = {'quantity': quantity, 'method': method}
        response = self._connection.auth_get(endpoint, params=params)
        return response.json()

    def get_specific_request(self, request_uuid):
        """Retrieve a specific request."""
        time.sleep(self._execution_delay)
        endpoint = f'/requests/{request_uuid}'
        response = self._connection.auth_get(endpoint)
        return response.json()

    def post_request(self, data):
        """Post a request to the server."""
        time.sleep(self._execution_delay)
        endpoint = '/requests/'
        response = self._connection.auth_post(endpoint, data_json=data)
        return response.json()

    def post_result(self, data, request_id):
        """Post a result to the server."""
        time.sleep(self._execution_delay)
        endpoint = '/results/'
        response = self._connection.auth_post(endpoint, data_json=data)
        return response


class FinalesClientConfig(BaseModel):
    """Configuration data for a FINALES client."""

    username: str
    host: str
    port: int
    execution_delay: float = 0.1

    @classmethod
    def load_from_yaml_file(cls, filepath):
        """Load the configuration from a yaml file."""
        with open(filepath) as fileobj:
            try:
                client_config = yaml.load(fileobj, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                raise yaml.YAMLError(
                    'Error while trying to read the yaml from client-config-file'
                ) from exc

        return FinalesClientConfig(**client_config)

    def create_client(self):
        """Use the data to create a client."""
        return FinalesClient(host=self.host,
                             port=self.port,
                             execution_delay=self.execution_delay)
