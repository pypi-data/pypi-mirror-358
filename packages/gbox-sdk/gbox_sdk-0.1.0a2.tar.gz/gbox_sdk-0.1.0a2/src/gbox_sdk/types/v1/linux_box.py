# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LinuxBox", "Config", "ConfigOs", "ConfigResolution", "ConfigBrowser"]


class ConfigOs(BaseModel):
    version: str
    """OS version string (e.g. 'ubuntu-20.04')"""


class ConfigResolution(BaseModel):
    height: float
    """Height of the box"""

    width: float
    """Width of the box"""


class ConfigBrowser(BaseModel):
    type: Literal["chromium", "firefox", "webkit"]
    """Supported browser types for Linux boxes"""

    version: str
    """Browser version string (e.g. '12')"""


class Config(BaseModel):
    cpu: float
    """CPU cores allocated to the box"""

    envs: Dict[str, str]
    """Environment variables for the box.

    These variables will be available in all operations including command execution,
    code running, and other box behaviors
    """

    labels: Dict[str, str]
    """Key-value pairs of labels for the box.

    Labels are used to add custom metadata to help identify, categorize, and manage
    boxes. Common use cases include project names, environments, teams,
    applications, or any other organizational tags that help you organize and filter
    your boxes.
    """

    memory: float
    """Memory allocated to the box in MiB"""

    os: ConfigOs
    """Linux operating system configuration"""

    resolution: ConfigResolution
    """Box display resolution configuration"""

    storage: float
    """Storage allocated to the box in GiB."""

    browser: Optional[ConfigBrowser] = None
    """Linux browser configuration settings"""

    working_dir: Optional[str] = FieldInfo(alias="workingDir", default=None)
    """Working directory path for the box.

    This directory serves as the default starting point for all operations including
    command execution, code running, and file system operations. When you execute
    commands or run code, they will start from this directory unless explicitly
    specified otherwise.
    """


class LinuxBox(BaseModel):
    id: str
    """Unique identifier for the box"""

    config: Config
    """Complete configuration for Linux box instance"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp of the box"""

    expires_at: datetime = FieldInfo(alias="expiresAt")
    """Expiration timestamp of the box"""

    status: Literal["pending", "running", "error", "terminated"]
    """The current status of a box instance"""

    type: Literal["linux"]
    """Box type is Linux"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Last update timestamp of the box"""
