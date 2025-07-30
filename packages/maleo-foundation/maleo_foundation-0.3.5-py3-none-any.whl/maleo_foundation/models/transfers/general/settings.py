from pydantic_settings import BaseSettings
from pydantic import Field
from maleo_foundation.enums import BaseEnums

class Settings(BaseSettings):
    ENVIRONMENT: BaseEnums.EnvironmentType = Field(..., description="Environment")
    SERVICE_KEY: str = Field(..., description="Service's key")
    GOOGLE_CREDENTIALS_PATH: str = Field(
        "/credentials/maleo-google-service-account.json",
        description="Internal credential's file path"
    )
    STATIC_CONFIGURATIONS_PATH: str = Field(
        "configs/static.yaml",
        description="Maleo's static configurations path"
    )
    RUNTIME_CONFIGURATIONS_PATH: str = Field(
        "configs/runtime.yaml",
        description="Service's runtime configurations path"
    )