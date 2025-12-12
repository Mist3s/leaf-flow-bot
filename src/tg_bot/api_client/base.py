from __future__ import annotations

from typing import Any

import httpx

from tg_bot.api_client.errors import ApiClientError


class BaseApiClient:
    def __init__(self, *, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self._client.get(path, params=params, headers=headers)
        if response.status_code >= 400:
            raise ApiClientError(response)
        return response

    async def close(self) -> None:
        await self._client.aclose()
