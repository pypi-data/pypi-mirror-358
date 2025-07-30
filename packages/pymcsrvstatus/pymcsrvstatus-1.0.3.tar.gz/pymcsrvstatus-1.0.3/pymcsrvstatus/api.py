# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from sys import version as pyversion
from typing import Dict, Optional

import aiohttp

from pymcsrvstatus.httpurl import HttpUrl
from pymcsrvstatus.models import ServerStatus
from pymcsrvstatus.version import __version__

_URL = HttpUrl("https://api.mcsrvstat.us")
_API_VERSION = "3"


def _headers(extra_user_agent: Optional[str]) -> Dict[str, str]:
    return {"User-Agent": f"pymcsrvstatus/{__version__}{f' {extra_user_agent}' if extra_user_agent else ''} (Python {pyversion})".replace("\n", "")}


async def fetch(address: str, extra_user_agent: Optional[str] = None) -> ServerStatus:
    url = str(_URL / _API_VERSION / address)
    async with aiohttp.ClientSession(headers=_headers(extra_user_agent)) as session, session.get(url) as response:
        return ServerStatus(**await response.json())


async def check_if_online(address: str, extra_user_agent: Optional[str] = None) -> bool:
    url = str(_URL / "simple" / address)
    async with aiohttp.ClientSession(headers=_headers(extra_user_agent)) as session, session.get(url) as response:
        if response.status == 200:
            return True
        return False


def get_icon_url(address: str) -> HttpUrl:
    return _URL / "icon" / address
