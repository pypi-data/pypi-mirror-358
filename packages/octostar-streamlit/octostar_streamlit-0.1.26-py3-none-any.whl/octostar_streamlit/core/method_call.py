from typing import Any

from pydantic import BaseModel


class MethodCall(BaseModel):
    service: str
    method: str
    # params: BaseModel
    params: Any
