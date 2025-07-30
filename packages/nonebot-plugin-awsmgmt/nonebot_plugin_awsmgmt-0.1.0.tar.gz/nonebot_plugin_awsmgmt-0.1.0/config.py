from pydantic import BaseModel
from typing import Optional

class Config(BaseModel):
    """
    AWS Management Plugin Configuration
    """
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_default_target_tag: Optional[str] = "ManagedBy:nonebot-plugin-awsmgmt"

    class Config:
        extra = "ignore"