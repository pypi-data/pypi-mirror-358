from typing import Union

from quartic_sdk.pipelines.config.opcua import OPCUAConfig

from asyncua import Client as AsyncClient


def get_client(config: OPCUAConfig):
    client = AsyncClient(config.host_url)

    if config.application_uri:
        client.application_uri = config.application_uri

    if config.username:
        client.set_user(config.username)
        client.set_password(config.password)

    return client


def get_security_string(config: OPCUAConfig):
    security_config = config.security_config
    if not security_config:
        return None
    return f"{security_config.security_policy},{security_config.security_mode},{security_config.certificate_path},{security_config.private_key_path}"
