from __future__ import annotations

import logging
from typing import Any

import httpx

from tg_bot.api_client.errors import ApiClientError

logger = logging.getLogger(__name__)


class BaseApiClient:
    def __init__(self, *, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._client = httpx.AsyncClient(base_url=self.base_url)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        logger.debug(f"GET запрос: {url}, params={params}")
        try:
            response = await self._client.get(path, params=params, headers=headers)
            logger.debug(f"Ответ GET {url}: status={response.status_code}")
            if response.status_code >= 400:
                logger.error(f"Ошибка GET {url}: status={response.status_code}, body={response.text[:200]}")
                raise ApiClientError(response)
            return response
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети при GET {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при GET {url}: {e}")
            raise

    async def _post(self, path: str, json: dict[str, Any] | None = None) -> httpx.Response:
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        logger.debug(f"POST запрос: {url}, json={json}")
        try:
            response = await self._client.post(path, json=json, headers=headers)
            logger.debug(f"Ответ POST {url}: status={response.status_code}")
            if response.status_code >= 400:
                logger.error(f"Ошибка POST {url}: status={response.status_code}, body={response.text[:200]}")
                raise ApiClientError(response)
            logger.debug(f"Успешный POST {url}: body={response.text[:200]}")
            return response
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети при POST {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при POST {url}: {e}")
            raise

    async def close(self) -> None:
        await self._client.aclose()
