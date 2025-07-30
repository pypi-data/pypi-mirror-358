# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from .._models import BaseModel

__all__ = ["ContainerInfo"]


class ContainerInfo(BaseModel):
    api_url: str
    """URL of the container API."""

    container_ip: str
    """IP address of the container."""

    container_name: str
    """Name of the container."""

    created_at: datetime
    """Timestamp when the container was created (UTC)."""

    expires_at: datetime
    """Timestamp when the container will expire (UTC)."""

    sample_id: str
    """Sample ID of the container."""

    status: str
    """Status of the container."""
