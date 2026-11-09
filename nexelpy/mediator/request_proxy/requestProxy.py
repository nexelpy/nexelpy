from starlette.requests import Request as R
from typing import Any, Optional
from starlette.datastructures import URL, QueryParams, Headers , Address
from .request_object import get_request

class RequestProxy:

    def _get_original_request(self) -> R:
        return get_request()
    
    def _pick(self, data, *keys):
        if not keys:
            return data
        if len(keys) == 1:
            return data.get(keys[0])
        return [data.get(k) for k in keys]

    async def app(self):
        """Return the running application (MainAppBuilder, a Starlette subclass)."""
        return self._get_original_request().scope.get("app")

    async def scope(self, *keys):
        return self._pick(self._get_original_request().scope, *keys)
    

    async def method(self) -> str:
        return self._get_original_request().method
    
    async def url(self) -> URL:
        return self._get_original_request().url
    
    async def headers(self,*keys) -> Headers:
        return self._pick(self._get_original_request().headers, *keys)
    
    async def client(self) -> Optional[Address]:
        return self._get_original_request().client
    
    async def state(self, *keys):
        state_dict = getattr(self._get_original_request().state, "_state", {})
        return self._pick(state_dict, *keys)

    def set_state(self, **kwargs):
        state = self._get_original_request().state
        for k, v in kwargs.items():
            setattr(state, k, v)
    
    async def args(self,*keys) -> QueryParams:
        return self._pick( dict(self._get_original_request().query_params), *keys)
    
    async def path_params(self,*keys) -> dict:
        return self._pick(self._get_original_request().path_params, *keys)

    async def cookies(self,*keys)-> dict:
        return self._pick(self._get_original_request().cookies, *keys)

    async def body(self) -> bytes:
        return await self._get_original_request().body()

    async def json(self, *keys):
        data = await self._get_original_request().json()
        return self._pick(data, *keys)

    async def form(self, *keys):
        form = await self._get_original_request().form()
        return self._pick(dict(form), *keys)

    def stream(self):
        """Return the raw async generator. Use: async for chunk in x.Request.stream(): ..."""
        return self._get_original_request().stream()
    
    async def session_clientSide(self, *keys):
        request = self._get_original_request()
        session_data = request.scope.get("state", {}).get("n-session", {})
        return self._pick(session_data, *keys)

    async def payload(self, method, *keys):
        method = method.upper()
        handlers = {
            "GET": self.args,
            "PATH": self.path_params,
            "JSON": self.json,
            "POST": self.form,
        }
        fn = handlers.get(method)
        if fn is None:
            raise ValueError(f"unsupported payload method: {method}")
        return await fn(*keys)
    

request = RequestProxy()