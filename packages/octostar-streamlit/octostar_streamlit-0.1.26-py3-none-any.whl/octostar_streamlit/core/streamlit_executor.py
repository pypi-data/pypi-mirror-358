from typing import Callable

from pydantic import BaseModel
from octostar_streamlit.core.method_call import MethodCall


class StreamlitMethodExecutor:
    def __init__(self, method_call: MethodCall, fn: Callable, key=None, subscribe=None) -> None:
        self._method_call = method_call
        self._fn = fn
        self._key = key
        self._subscribe = subscribe

    def execute(self):
        key = self._key
        service = self._method_call.service
        method = self._method_call.method

        if isinstance(self._method_call.params, BaseModel):
            params = self._method_call.params.model_dump(by_alias=True)
        else:
            params = self._method_call.params

        return self._fn(service=service, method=method, params=params, key=key, subscribe=self._subscribe)
