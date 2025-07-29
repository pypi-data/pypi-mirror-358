from .base_sink import KafkaSinkApp
from typing import Callable, Optional
from quartic_sdk.pipelines.connector_app import CONNECTOR_CLASS
from pydantic import BaseModel
from typing import Literal
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import pandas as pd
import time
from quartic_sdk.pipelines.connector_app import BaseConfig


class HttpConfig(BaseConfig):
    def __init__(self, **kwargs):
        self.endpoint: str = kwargs.get('endpoint', None)
        self.auth_type: str = kwargs.get('auth_type', None)
        self.access_token: str = kwargs.get('access_token')      # For Bearer auth
        self.refresh_token: str = kwargs.get('refresh_token')    # For Bearer auth
        self.refresh_endpoint: str = kwargs.get('refresh_endpoint')  # For Bearer auth
        self.username: str = kwargs.get('username')              # For Basic auth
        self.password: str = kwargs.get('password')              # For Basic auth
        self.group_messages: bool = kwargs.get('group_messages', False)
        self.headers: dict[str, str] = kwargs.get('headers', {'Content-Type': 'application/json'})
        self.timeout: int = kwargs.get('timeout', 10)

class HttpSink(KafkaSinkApp):
    """
    HTTP sink application.
    """ 
    WAIT_BEFORE_RETRY_SECONDS = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connector_class = CONNECTOR_CLASS.Http.value
        self.success_response_callback: Optional[Callable] = kwargs.get('success_response_callback', None)
        self.connector_config = kwargs.get('connector_config', None)
    
    def _create_session(self) -> requests.Session:
        """Create an HTTP session with basic authentication."""
        # TODO: Check session timeout?
        session = requests.Session()
        if self.connector_config.auth_type == 'Basic':
            session.auth = HTTPBasicAuth(self.connector_config.username, self.connector_config.password)
        elif self.connector_config.auth_type == 'Bearer':
            session.headers['Authorization'] = f'Bearer {self.connector_config.access_token}'
        session.headers.update(self.connector_config.headers)
        return session
    
    def _refresh_token(self) -> Optional[str]:
        """
        Refresh the access token using the refresh token
        Returns new access token if successful, None otherwise
        """
        if not self.connector_config.refresh_token:
            print("No refresh token available")
            return None

        try:
            refresh_url = f"{self.connector_config.endpoint}/api/token/refresh/"
            response = requests.post(
                refresh_url,
                json={"refresh": self.connector_config.refresh_token},
                headers={'Content-Type': 'application/json'},
                timeout=self.connector_config.timeout
            )
            response.raise_for_status()
            
            new_token = response.json().get('access')
            if new_token:
                self.connector_config.access_token = new_token
                return new_token
            
            print("No access token in refresh response")
            return None
            
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None
        
    def write_data(self, data: pd.DataFrame):
        if data.empty:
            return
        session = self._create_session()
        series = data['value']
        data = series.to_list()
        if self.connector_config.group_messages:
            while True:
                try:
                    self.send_post_request(session, data)
                except Exception as e:
                    if self.test_run:
                        raise e
                    time.sleep(self.WAIT_BEFORE_RETRY_SECONDS)
                    continue
                break
                
        else:
            for item in data:
                while True:
                    try:
                        self.send_post_request(session, item)
                    except Exception as e:
                        if self.test_run:
                            raise e
                        time.sleep(self.WAIT_BEFORE_RETRY_SECONDS)
                        continue
                    break
    
    def send_post_request(self, session, data):
        """Send a POST request with the given data"""
        try:
            response = session.post(self.connector_config.endpoint, 
                                    data=data, 
                                    timeout=self.connector_config.timeout)
            # Handle 401 by refreshing token and retrying once
            if response.status_code == 401:
                print("Received 401, attempting token refresh")
                new_token = self._refresh_token()
                
                if new_token:
                    # Update session with new token
                    session.headers['Authorization'] = f'Bearer {new_token}'
                    
                    # Retry the request
                    response = session.post(
                        self.connector_config.endpoint,
                        data=data,
                        timeout=self.connector_config.timeout
                    )
                else:
                    raise RequestException("Token refresh failed")
            response.raise_for_status()
            if self.success_response_callback:
                self.success_response_callback(response)
            print(f"Successfully written data: {data}.")
            print(f"Response: {response.text}")
        except RequestException as e:
            print(f"Failed to write data: {data}. Error: {e}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e
        finally:
            session.close()

    def test_config(self):
        try:
            self.write_data(pd.DataFrame({'value': ["test"]}))
            return "Connection successful"
        except Exception as e:
            return f"Failed to write data: {e}"
