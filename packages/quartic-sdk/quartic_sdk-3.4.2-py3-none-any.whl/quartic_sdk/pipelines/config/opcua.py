from typing import Optional, List

from pydantic import BaseModel

from quartic_sdk.pipelines.connector_app import BaseConfig

class OPCUASecurityConfig(BaseModel):
    security_policy: str
    security_mode: str
    certificate_path: str
    private_key_path: str


class OPCUAConfig(BaseModel, BaseConfig):
    host_url: str
    security_config: Optional[OPCUASecurityConfig] = None
    application_uri: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class OPCUASinkConfig(OPCUAConfig):
    pass


class OPCUASourceConfig(OPCUAConfig):
    node_ids: List[str]
