from typing import Dict, Union
from pydantic import Field
from octostar_streamlit.core.params_base_model import ParamsBaseModel

class OsDropzoneParams(ParamsBaseModel):
    label: str
    prefer_saved_set: bool = Field(default=True, serialization_alias='preferSavedSet')

class OsContextMenuParams(ParamsBaseModel):
    item: Dict
    label: Union[str, None] = None
    height: Union[str, None] = None
    padding: Union[str, None] = None
