import hashlib
import json
import os
import platform
import random
import time
from typing import Dict, Optional

import requests
from .constants import SDK_VERSION, DEFAULT_REQUEST_TIMEOUT


def request_url(endpoint: str, path: str) -> str:
    return f"{endpoint}{path}"


def make_headers(client_key: str, client_secret: str) -> Dict[str, str]:
    ts = str(int(time.time()))
    nonce = f"{int(time.time() * 1000)}{random.randint(10000, 19999)}"
    need_sign_str = f"{ts}|{client_secret}|{nonce}"
    sign = hashlib.md5(need_sign_str.encode()).hexdigest().upper()
    extra_info = json.dumps({
        "sdk": "true",
        "language": "python",
        "version": SDK_VERSION,
        "os": platform.system().lower(),
        "arch": platform.machine().lower(),
    })
    return {
        "x-stardots-timestamp": ts,
        "x-stardots-nonce": nonce,
        "x-stardots-key": client_key,
        "x-stardots-sign": sign,
        "x-stardots-extra": extra_info,
    }


def send_request(
    method: str,
    url: str,
    json_payload: Optional[dict] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_REQUEST_TIMEOUT,
    files: Optional[dict] = None,
) -> requests.Response:
    session = requests.Session()
    req_headers = headers or {}
    if files:
        # For multipart, do not set Content-Type, requests will handle it
        pass
    else:
        req_headers.setdefault("Content-Type", "application/json; charset=utf-8")
    resp = session.request(
        method=method,
        url=url,
        headers=req_headers,
        json=None if files else json_payload,
        data=None if not files else json_payload,
        files=files,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp 