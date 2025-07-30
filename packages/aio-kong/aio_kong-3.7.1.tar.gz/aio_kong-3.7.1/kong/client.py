from __future__ import annotations

import os
import sys
from typing import Any, Callable, Dict, Optional

from aiohttp import ClientResponse, ClientSession

from . import __version__
from .acls import Acl, Acls
from .certificates import Certificate, Certificates
from .components import CrudComponent, KongError, KongResponseError
from .consumers import Consumer, Consumers
from .plugins import Plugin, Plugins
from .routes import Route, Routes
from .services import Service, Services
from .snis import Sni, Snis

__all__ = ["Kong", "KongError", "KongResponseError"]

DEFAULT_USER_AGENT = (
    f"python/{'.'.join(map(str, sys.version_info[:2]))} aio-kong/{__version__}"
)


def default_admin_url() -> str:
    """Return the default Kong admin URL."""
    return os.getenv("KONG_ADMIN_URL", os.getenv("KONG_URL", "http://127.0.0.1:8001"))


class Kong:
    """Kong client"""

    content_type: str = "application/json, text/*; q=0.5"

    def __init__(
        self,
        url: str | None = None,
        session: ClientSession | None = None,
        request_kwargs: dict | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self.url = url or default_admin_url()
        self.session = session
        self.user_agent = user_agent
        self.request_kwargs = request_kwargs or {}
        self.services = Services(self, Service)
        self.routes = Routes(self, Route)
        self.plugins = Plugins(self, Plugin)
        self.consumers = Consumers(self, Consumer)
        self.certificates = Certificates(self, Certificate)
        self.acls = Acls(self, Acl)
        self.snis = Snis(self, Sni)

    def __repr__(self) -> str:
        return self.url

    __str__ = __repr__

    @property
    def cli(self) -> Kong:
        return self

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def __aenter__(self) -> Kong:
        return self

    async def __aexit__(self, exc_type: type, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def execute(
        self,
        url: str,
        method: str = "",
        headers: dict[str, str] | None = None,
        callback: Optional[Callable[[ClientResponse], Any]] = None,
        wrap: Optional[Callable[[Any], Any]] = None,
        **kw: Any,
    ) -> Any:
        if not self.session:
            self.session = ClientSession()
        method = method or "GET"
        headers_ = self.default_headers()
        headers_.update(headers or ())
        kw.update(self.request_kwargs)
        response = await self.session.request(method, url, headers=headers_, **kw)
        if callback:
            return await callback(response)
        if response.status == 204:
            return True
        if response.status >= 400:
            try:
                data = await response.json()
            except Exception:
                data = await response.text()
            raise KongResponseError(response, data)
        response.raise_for_status()
        data = await response.json()
        return wrap(data) if wrap else data

    async def apply_json(self, config: dict, clear: bool = True) -> dict:
        if not isinstance(config, dict):
            raise KongError("Expected a dict got %s" % type(config).__name__)
        result = {}
        for name, data in config.items():
            if not isinstance(data, list):
                data = [data]
            o = getattr(self, name)
            if not isinstance(o, CrudComponent):
                raise KongError("Kong object %s not available" % name)
            result[name] = await o.apply_json(data, clear=clear)
        return result

    async def delete_all(self) -> None:
        await self.services.delete_all()
        await self.consumers.delete_all()
        await self.plugins.delete_all()
        await self.certificates.delete_all()

    def default_headers(self) -> Dict[str, str]:
        return {"user-agent": self.user_agent, "accept": self.content_type}
