from __future__ import annotations

import re

CDN_URL_RE = re.compile(r'^(https://[^/]+/[^/]+)/[^/]+/S\d+/Trailer/(\w+\.m3u8?)$')
FUCKING_MKV = re.compile(r'^(https://[^/]+/[^/]+)\.S\d+/mkv/Trailer/(\w+\.m3u8?)$')
