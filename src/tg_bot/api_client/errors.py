from __future__ import annotations

import httpx


class ApiClientError(Exception):
    def __init__(self, response: httpx.Response):
        self.response = response
        super().__init__(f"API error: {response.status_code} {response.text}")

    @property
    def status_code(self) -> int:
        return self.response.status_code
