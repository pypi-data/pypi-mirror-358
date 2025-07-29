import json
import os

import requests
from urllib.parse import urljoin
import traceback
import aiohttp
import logging

TOKEN_FILE = os.getenv("TOKEN_FILE_PATH","/tmp/.quartic")

def get_and_save_token(host,username,password,verify_ssl):
        """
        Get a new access token and refresh token from the authentication endpoint and save them.
        This method sends a POST request to the authentication endpoint with the provided username and password
        to obtain a new access token and refresh token. It then saves these tokens to a file.
        Args:
            host
            username
            password
            verify_ssl
        Returns:
            access_token
        Raises:
            PermissionError: If there is an error during the authentication process or if the response status
                            code indicates an issue.
        """
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = urljoin(host ,"/graphql/auth/tokens/")
        response = requests.post(
            url,
            json={
                "username": username,
                "password": password
            },
            headers=headers,
            verify=verify_ssl
        )
        if response.status_code != 200:
            raise PermissionError('Error while Login and generating token')
        return response.json().get('access'), response.json().get('refresh')


def save_token(token, user_identification_string):
    """
    Save a token to a file.

    This function creates the necessary directory structure and saves the provided token to a file.

    Args:
        token (str): The token to be saved.

    Returns:
        None

    Raises:
        None
    """
    os.makedirs(os.path.dirname(f'{TOKEN_FILE}/{user_identification_string}/token.txt'), exist_ok=True)
    # Save token
    with open(f'{TOKEN_FILE}/{user_identification_string}/token.txt', 'w') as token_file:
        token_file.write(token)

# Function to request a new token (You need to implement this)


def request_new_token(refresh_token, host,user_identification_string):
        """
    Request a new access token using a refresh token.

    This function sends a request to the specified host's refresh token endpoint to obtain a new access token.
    It includes the provided refresh token in the request data.

    Args:
        refresh_token (str): The refresh token used to obtain a new access token. If None, the request will fail.
        host (str): The base URL of the host where the refresh token request will be sent.

    Returns:
        str: The new access token obtained from the response.

    Raises:
        PermissionError: If the refresh token has expired or if any other error occurs during the token request.
    """
        try:
            headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}
            response = requests.post(
                url=urljoin(host, "/graphql/token/refresh/"),
                json={
                    "refresh": refresh_token,
                },
                headers=headers
            )
            # Check if the login was successful
            if response.status_code in {400, 401}:
                raise PermissionError(
                    'Refresh token has expired. Please recreate GraphqlClient')
            return response.json().get('access')
        except Exception as e:
            raise e

# Decorator function to handle token expiration and refresh


def authenticate_with_tokens(func):
    """
    Decorator to handle token expiration and refresh for API authentication.

    This decorator checks for the existence of a token file, reads the stored access token, and attempts
    to refresh the token if it has expired. It updates the token file with the new access token and retries
    the original API call with the refreshed token if necessary.

    Args:
        func (callable): The function to decorate.

    Returns:
        callable: The decorated function.

    Raises:
        Exception: If the token file does not exist or if any other error occurs during token management.
        PermissionError: If the access token is missing in the token file.
    """
    def wrapper(self, *args, **kwargs):
        try:

            if not self.access_token and not self.refresh_token:
                raise PermissionError("Access/Refresh token missing, Please recreate the client")

            # Call the decorated function
            response = func(self, *args, **kwargs)

            # Check the response status code
            if response.status_code == 401:
                # Access token is likely expired, attempt to refresh it
                self.access_token = request_new_token(
                    refresh_token=self.refresh_token,
                    host=self.configuration.host,
                    user_identification_string=self.configuration.username
                )  # Implement this method to refresh the access token
                if not self.access_token:
                    raise PermissionError("Failed to refresh access token.")


                # Retry the original API call with the new access token
                response = func(self, *args, **kwargs)

            return response
        except Exception as e:
            logging.debug(traceback.format_exc())
            raise e

    return wrapper

def async_authenticate_with_tokens(func):
    """
    Decorator to handle token expiration and refresh for API authentication.

    This decorator checks for the existence of a token file, reads the stored access token, and attempts
    to refresh the token if it has expired. It updates the token file with the new access token and retries
    the original API call with the refreshed token if necessary.

    Args:
        func (callable): The function to decorate.

    Returns:
        callable: The decorated function.

    Raises:
        Exception: If the token file does not exist or if any other error occurs during token management.
        PermissionError: If the access token is missing in the token file.
    """
    async def wrapper(self, *args, **kwargs):
        try:
            username = self.username
            host = self._get_graphql_url()

            if not self.access_token and not self.refresh_token:
                raise PermissionError("Access/Refresh token missing, Please recreate the client")

            try:
                # Call the decorated function
                response = await func(self, *args, **kwargs)

            except aiohttp.ClientResponseError as e:
                if e.status == 401:
                    # Access token is likely expired, attempt to refresh it
                    self.access_token = request_new_token(
                        refresh_token=self.refresh_token,
                        host=host,
                        user_identification_string=username
                    )  # Implement this method to refresh the access token
                    if not self.access_token:
                        raise PermissionError("Failed to refresh access token.")


                    # Retry the original API call with the new access token
                    response = await func(self, *args, **kwargs)
                else:
                    logging.debug(traceback.format_exc())
                    raise e
            return response
        except Exception as e:
            logging.debug(traceback.format_exc())
            raise e

    return wrapper
