"""Try to bypass Cloudflare protection."""

from __future__ import annotations

import httpx

headers = {
    # "User-Agent": "HTTPie/3.2.4",
    # "Accept": "*/*",
    # "Accept-Encoding": "gzip, deflate",
    # "Connection": "keep-alive",
}

url = "https://untappd.com/user/backoftheferry"

with httpx.Client(http2=False, headers=headers, timeout=10) as client:
    resp = client.get(url)
    print(f"{resp.http_version=}")
    print(resp.status_code)
    print(resp.headers)
    print(resp.text[:500])  # print first 500 chars of html
