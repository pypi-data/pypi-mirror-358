import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ClientConfig(BaseModel):
    """Configuration for the Jamm API client."""

    model_config = ConfigDict(validate_assignment=True)

    # Authentication settings
    client_id: str = Field(default_factory=lambda: os.environ.get("JAMM_CLIENT_ID", ""))
    client_secret: str = Field(
        default_factory=lambda: os.environ.get("JAMM_CLIENT_SECRET", "")
    )

    # Environment settings
    environment: str = Field(
        default_factory=lambda: os.environ.get("JAMM_ENVIRONMENT", "production")
    )

    # These will be set by the Environment class
    api_base_url: Optional[str] = None
    oauth_base_url: Optional[str] = None
    verify_ssl: bool = True

    # HTTP settings
    timeout: int = 30
    read_timeout: int = 90
    max_retries: int = 3
    backoff_factor: float = 0.5
