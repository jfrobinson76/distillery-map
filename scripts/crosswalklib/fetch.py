"""
The only way a matcher touches the network.

    f = fetch.Fetcher(cache_dir, allow=args.fetch, cap=400, log=cache_dir / "requests.log")
    body = f.get(url)                       # bytes from cache, or fetched and cached, or None
    f.bulk(url, dest, max_bytes=2_000_000_000)   # one-off download with a size check first

Guarantees, none of them optional:
- TLS is verified with the platform default context. There is no parameter to turn that off.
  A host with a broken chain is logged `tls` and returns None.
- Every request is written to the log BEFORE it is sent, so a run that dies mid-flight still
  leaves its count. The log is the audit trail the research note cites.
- The cap counts every attempt, including 429s and errors. At the cap `get` returns None and
  says so once. A 429 stops the run for that host: nothing is retried.
- At most one request per `delay` seconds (default 1.0), globally, not per host.
- Nothing is fetched unless `allow` is True; with `allow=False` the cache is the only source.
"""
from __future__ import annotations

import hashlib
import http.cookiejar
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Stillbound-Research/1.0 (data@stillbound.ai)"


class Fetcher:
    def __init__(self, cache_dir: Path, allow: bool, cap: int = 400, delay: float = 1.0,
                 log: Path | None = None, timeout: int = 30, spent: int = 0):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.allow, self.cap, self.delay, self.timeout = allow, cap, delay, timeout
        self.log = Path(log) if log else self.cache_dir / "requests.log"
        self.made = spent + self._count_logged()
        self.last = 0.0
        self.blocked: set[str] = set()
        self.said_cap = False
        self.outcomes: dict[str, int] = {}
        self._ctx = ssl.create_default_context()  # verified; deliberately not configurable
        self._jar = http.cookiejar.CookieJar()   # for sites that hand out a session before a POST
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=self._ctx), urllib.request.HTTPCookieProcessor(self._jar))

    # ------------------------------------------------------------------ cache ----
    def _key(self, url: str) -> Path:
        return self.cache_dir / (hashlib.sha1(url.encode()).hexdigest()[:20] + ".bin")

    def cached(self, url: str) -> bytes | None:
        p = self._key(url)
        return p.read_bytes() if p.exists() else None

    def _count_logged(self) -> int:
        if not self.log.exists():
            return 0
        return sum(1 for line in self.log.read_text().splitlines() if line.startswith("REQ "))

    def _log(self, kind: str, url: str, extra: str = "") -> None:
        with self.log.open("a") as fh:
            fh.write(f"{kind} {time.strftime('%Y-%m-%dT%H:%M:%S')} {url} {extra}\n".rstrip() + "\n")

    def _note(self, outcome: str) -> None:
        self.outcomes[outcome] = self.outcomes.get(outcome, 0) + 1

    # -------------------------------------------------------------------- get ----
    def get(self, url: str, headers: dict | None = None, force: bool = False) -> bytes | None:
        """Bytes for `url`: from cache unless `force`; else fetched (if allowed, under the cap)."""
        if not force:
            c = self.cached(url)
            if c is not None:
                self._note("cache")
                return c
        if not self.allow:
            self._note("not-allowed")
            return None
        host = urllib.parse.urlsplit(url).netloc
        if host in self.blocked:
            self._note("host-blocked")
            return None
        if self.made >= self.cap:
            if not self.said_cap:
                print(f"fetch: request cap {self.cap} reached; nothing more is fetched this run", file=sys.stderr)
                self.said_cap = True
            self._note("cap")
            return None
        wait = self.delay - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.made += 1
        self._log("REQ", url)  # before the request, so a dead run still counts it
        self.last = time.monotonic()
        req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
        try:
            with self._opener.open(req, timeout=self.timeout) as r:
                body = r.read()
            self._key(url).write_bytes(body)
            self._log("OK", url, str(len(body)))
            self._note("ok")
            return body
        except urllib.error.HTTPError as e:
            self._log("HTTP", url, str(e.code))
            self._note(f"http-{e.code}")
            if e.code == 429:
                self.blocked.add(host)
                print(f"fetch: 429 from {host}; no more requests to it this run", file=sys.stderr)
            return None
        except ssl.SSLError as e:
            self._log("TLS", url, str(e.reason if hasattr(e, "reason") else e))
            self._note("tls")
            return None
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as e:
            self._log("ERR", url, type(e).__name__)
            self._note("error")
            return None

    def post(self, url: str, data: dict, headers: dict | None = None, timeout: int | None = None) -> bytes | None:
        """A form POST, never cached, under the same cap, log, pacing and TLS rules as get().
        Cookies set by earlier get()/post() calls on this Fetcher are sent (some registers hand
        out a session token on a page before they let you download)."""
        if not self.allow:
            self._note("not-allowed")
            return None
        host = urllib.parse.urlsplit(url).netloc
        if host in self.blocked or self.made >= self.cap:
            self._note("host-blocked" if host in self.blocked else "cap")
            return None
        wait = self.delay - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.made += 1
        self._log("REQ", url, "POST " + ",".join(f"{k}={str(v)[:24]}" for k, v in data.items() if "token" not in k.lower()))
        self.last = time.monotonic()
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                     headers={"User-Agent": UA, **(headers or {})})
        try:
            with self._opener.open(req, timeout=timeout or self.timeout) as r:
                body = r.read()
            self._log("OK", url, str(len(body)))
            self._note("ok")
            return body
        except urllib.error.HTTPError as e:
            self._log("HTTP", url, str(e.code))
            self._note(f"http-{e.code}")
            if e.code == 429:
                self.blocked.add(host)
            return None
        except ssl.SSLError as e:
            self._log("TLS", url, str(getattr(e, "reason", e)))
            self._note("tls")
            return None
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as e:
            self._log("ERR", url, type(e).__name__)
            self._note("error")
            return None

    def text(self, url: str, encoding: str = "utf-8", **kw) -> str | None:
        b = self.get(url, **kw)
        return b.decode(encoding, "replace") if b is not None else None

    def json(self, url: str, **kw):
        t = self.text(url, **kw)
        return json.loads(t) if t else None

    # ------------------------------------------------------------------- bulk ----
    def bulk(self, url: str, dest: Path, max_bytes: int) -> bool:
        """One-off download to `dest`, sized first with HEAD; refuses over `max_bytes`."""
        dest = Path(dest)
        if dest.exists():
            self._note("bulk-cached")
            return True
        if not self.allow:
            self._note("not-allowed")
            return False
        if self.made >= self.cap:
            self._note("cap")
            return False
        self.made += 1
        self._log("REQ", url, "HEAD")
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as r:
                size = int(r.headers.get("Content-Length") or 0)
        except Exception as e:  # noqa: BLE001 - a HEAD that fails is logged and we stop
            self._log("ERR", url, f"HEAD {type(e).__name__}")
            return False
        if size > max_bytes:
            self._log("REFUSED", url, f"{size} > {max_bytes}")
            print(f"fetch: {url} is {size} bytes, over the {max_bytes} cap; not downloaded", file=sys.stderr)
            return False
        self.made += 1
        self._log("REQ", url, f"GET {size}")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=max(self.timeout, 600), context=self._ctx) as r, \
                    dest.open("wb") as out:
                while chunk := r.read(1 << 20):
                    out.write(chunk)
            self._log("OK", url, str(dest.stat().st_size))
            return True
        except Exception as e:  # noqa: BLE001
            self._log("ERR", url, type(e).__name__)
            dest.unlink(missing_ok=True)
            return False

    def summary(self) -> str:
        return f"requests this run {self.made} of cap {self.cap}; outcomes {self.outcomes}"

