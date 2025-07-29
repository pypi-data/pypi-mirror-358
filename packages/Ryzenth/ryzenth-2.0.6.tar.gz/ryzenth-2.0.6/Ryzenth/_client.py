#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2025 (c) Randy W @xtdevs, @xtsea
#
# from : https://github.com/TeamKillerX
# Channel : @RendyProjects
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import json
import logging
import random
import time
import typing as t
from os import getenv

import aiohttp
import httpx

from .__version__ import get_user_agent
from ._errors import ForbiddenError, InternalError, ToolNotFoundError, WhatFuckError
from ._shared import TOOL_DOMAIN_MAP
from .helper import AutoRetry
from .tl import LoggerService


class RyzenthApiClient:
    def __init__(
        self,
        *,
        tools_name: list[str],
        api_key: dict[str, list[dict]],
        rate_limit: int = 5,
        use_default_headers: bool = False,
        use_httpx: bool = False,
        settings: dict = None,
        logger: t.Optional[LoggerService] = None
    ) -> None:
        if not isinstance(api_key, dict) or not api_key:
            raise WhatFuckError("API Key must be a non-empty dict of tool_name → list of headers")
        if not tools_name:
            raise WhatFuckError("A non-empty list of tool names must be provided for 'tools_name'.")

        self._api_keys = api_key
        self._use_default_headers: bool = use_default_headers
        self._rate_limit = rate_limit
        self._request_counter = 0
        self._last_reset = time.monotonic()
        self._use_httpx = use_httpx
        self._settings = settings or {}
        self._logger = logger
        self._init_logging()

        self._tools: dict[str, str] = {
            name: TOOL_DOMAIN_MAP.get(name)
            for name in tools_name
        }
        self._session = (
            httpx.AsyncClient()
            if use_httpx else
            aiohttp.ClientSession()
        )

    def _init_logging(self):
        log_level = "WARNING"
        disable_httpx_log = False

        for entry in self._settings.get("logging", []):
            if "level" in entry:
                log_level = entry["level"].upper()
            if "httpx_log" in entry:
                disable_httpx_log = not entry["httpx_log"]

        logging.basicConfig(level=getattr(logging, log_level, logging.WARNING))
        if disable_httpx_log:
            logging.getLogger("httpx").setLevel(logging.CRITICAL)
            logging.getLogger("httpcore").setLevel(logging.CRITICAL)

    def get_base_url(self, tool: str) -> str:
        check_ok = self._tools.get(tool, None)
        if check_ok is None:
            raise ToolNotFoundError(f"Base URL for tool '{tool}' not found.")
        return check_ok

    def _get_headers_for_tool(self, tool: str) -> dict:
        base = {"User-Agent": get_user_agent()}
        if self._use_default_headers and tool in self._api_keys:
            base.update(random.choice(self._api_keys[tool]))
        return base

    async def _throttle(self):
        now = time.monotonic()
        if now - self._last_reset >= 1:
            self._last_reset = now
            self._request_counter = 0

        if self._request_counter >= self._rate_limit:
            await asyncio.sleep(1 - (now - self._last_reset))
            self._last_reset = time.monotonic()
            self._request_counter = 0

        self._request_counter += 1

    @classmethod
    def from_env(cls) -> "RyzenthApiClient":
        tools_raw = getenv("RYZENTH_TOOLS")
        api_key_raw = getenv("RYZENTH_API_KEY_JSON")
        rate_limit_raw = getenv("RYZENTH_RATE_LIMIT", "5")
        use_headers = getenv("RYZENTH_USE_HEADERS", "true")
        use_httpx = getenv("RYZENTH_USE_HTTPX", "false")

        if not tools_raw or not api_key_raw:
            raise WhatFuckError("Environment variables RYZENTH_TOOLS and RYZENTH_API_KEY_JSON are required.")

        tools = [t.strip() for t in tools_raw.split(",")]
        api_keys = json.loads(api_key_raw)
        rate_limit = int(rate_limit_raw)
        use_default_headers = use_headers.lower() == "true"
        httpx_flag = use_httpx.lower() == "true"

        return cls(
            tools_name=tools,
            api_key=api_keys,
            rate_limit=rate_limit,
            use_default_headers=use_default_headers,
            use_httpx=httpx_flag
        )

    async def _status_resp_error(self, resp, status_httpx=False):
        if status_httpx:
            if resp.status_code == 403:
                raise ForbiddenError("Access Forbidden: You may be blocked or banned.")
            elif resp.status_code == 401:
                raise ForbiddenError("Access Forbidden: Required API key or invalid params.")
            elif resp.status_code == 500:
                raise InternalError("Error requests status code 500")
        else:
            if resp.status == 403:
                raise ForbiddenError("Access Forbidden: You may be blocked or banned.")
            elif resp.status == 401:
                raise ForbiddenError("Access Forbidden: Required API key or invalid params.")
            elif resp.status == 500:
                raise InternalError("Error requests status code 500")

    @AutoRetry(max_retries=3, delay=1.5)
    async def get(
        self,
        tool: str,
        path: str,
        params: t.Optional[dict] = None,
        use_image_content: bool = False
    ) -> t.Union[dict, bytes]:
        await self._throttle()
        base_url = self.get_base_url(tool)
        url = f"{base_url}{path}"
        headers = self._get_headers_for_tool(tool)

        if self._use_httpx:
            resp = await self._session.get(url, params=params, headers=headers)
            await self._status_resp_error(resp, status_httpx=True)
            resp.raise_for_status()
            data = resp.content if use_image_content else resp.json()
        else:
            async with self._session.get(url, params=params, headers=headers) as resp:
                await self._status_resp_error(resp, status_httpx=False)
                resp.raise_for_status()
                data = await resp.read() if use_image_content else await resp.json()

        if self._logger:
            await self._logger.log(f"[GET {tool}] ✅ Success: {url}")
        return data

    @AutoRetry(max_retries=3, delay=1.5)
    async def post(
        self,
        tool: str,
        path: str,
        data: t.Optional[dict] = None,
        json: t.Optional[dict] = None,
        use_image_content: bool = False
    ) -> t.Union[dict, bytes]:
        await self._throttle()
        base_url = self.get_base_url(tool)
        url = f"{base_url}{path}"
        headers = self._get_headers_for_tool(tool)

        if self._use_httpx:
            resp = await self._session.post(url, data=data, json=json, headers=headers)
            await self._status_resp_error(resp, status_httpx=True)
            resp.raise_for_status()
            data = resp.content if use_image_content else resp.json()
        else:
            async with self._session.post(url, data=data, json=json, headers=headers) as resp:
                await self._status_resp_error(resp, status_httpx=False)
                resp.raise_for_status()
                data = await resp.read() if use_image_content else await resp.json()

        if self._logger:
            await self._logger.log(f"[POST {tool}] ✅ Success: {url}")
        return data

    async def close(self):
        return await self._session.aclose() if self._use_httpx else await self._session.close()
