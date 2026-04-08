from __future__ import annotations

import json
import mimetypes
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
SITES_DIR = ROOT / "sites"


class SerenaSiteError(RuntimeError):
    pass


@dataclass
class SiteConfig:
    site: str
    base_url: str
    api_base_path: str
    api_secret: str
    managed_collections: list[str]
    allowed_capabilities: list[str]
    transport_aliases: list[str]


def load_site_config(site_name: str) -> SiteConfig:
    local_path = SITES_DIR / f"{site_name}.local.json"
    example_path = SITES_DIR / f"{site_name}.example.json"
    config_path = local_path if local_path.exists() else example_path

    if not config_path.exists():
        raise SerenaSiteError(f"Site manifest not found for '{site_name}'.")

    data = json.loads(config_path.read_text())

    return SiteConfig(
        site=data["site"],
        base_url=data["base_url"].rstrip("/"),
        api_base_path=data.get("api_base_path", "/api/web-manager"),
        api_secret=data["api_secret"],
        managed_collections=list(data.get("managed_collections", [])),
        allowed_capabilities=list(data.get("allowed_capabilities", [])),
        transport_aliases=list(data.get("transport_aliases", ["/api/serena"])),
    )


class SerenaSiteClient:
    def __init__(self, config: SiteConfig):
        self.config = config

    def _build_url(self, route_path: str, base_path: str | None = None) -> str:
        active_base = (base_path or self.config.api_base_path).rstrip("/")
        return f"{self.config.base_url}{active_base}{route_path}"

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
          "Authorization": f"Bearer {self.config.api_secret}",
          "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, path: str, *, payload: Any | None = None, headers: dict[str, str] | None = None) -> Any:
        body = None
        request_headers = self._headers(headers)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        candidate_bases = [self.config.api_base_path, *self.config.transport_aliases]
        seen: set[str] = set()
        last_error: SerenaSiteError | None = None

        for base in candidate_bases:
            if not base or base in seen:
                continue
            seen.add(base)

            request = Request(
                url=self._build_url(path, base),
                method=method,
                headers=request_headers,
                data=body,
            )

            try:
                with urlopen(request) as response:
                    data = response.read().decode("utf-8")
                    return json.loads(data) if data else None
            except HTTPError as error:
                raw = error.read().decode("utf-8")
                try:
                    message = json.loads(raw)
                except json.JSONDecodeError:
                    message = {"error": raw}

                if error.code == 404:
                    last_error = SerenaSiteError(f"{error.code} {message}")
                    continue

                raise SerenaSiteError(f"{error.code} {message}") from error

        if last_error:
            raise last_error
        raise SerenaSiteError("Request failed without a response.")

    def verify(self) -> Any:
        return self._request("GET", "/auth/verify")

    def status(self) -> Any:
        return self._request("GET", "/status")

    def search(self, query: str, limit: int = 10) -> Any:
        safe_query = quote(query)
        return self._request("GET", f"/content/search?q={safe_query}&limit={limit}")

    def upsert_page(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "/pages/upsert", payload=payload)

    def upsert_post(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "/posts/upsert", payload=payload)

    def update_global(self, global_slug: str, payload: dict[str, Any]) -> Any:
        return self._request("POST", "/globals/update", payload={"global": global_slug, "data": payload})

    def request_approval(self, collection: str, *, doc_id: str | None = None, slug: str | None = None) -> Any:
        body: dict[str, Any] = {"collection": collection}
        if doc_id is not None:
            body["id"] = doc_id
        if slug is not None:
            body["slug"] = slug
        return self._request("POST", "/approval/request", payload=body)

    def publish(self, collection: str, *, doc_id: str | None = None, slug: str | None = None, require_approval: bool = True) -> Any:
        body: dict[str, Any] = {"collection": collection, "requireApproval": require_approval}
        if doc_id is not None:
            body["id"] = doc_id
        if slug is not None:
            body["slug"] = slug
        return self._request("POST", "/publish", payload=body)

    def revalidate(self, *, path: str | None = None, slug: str | None = None, tag: str | None = None) -> Any:
        return self._request("POST", "/revalidate", payload={"path": path, "slug": slug, "tag": tag})

    def upload_media(self, file_path: str, *, alt: str | None = None, folder: str | None = None) -> Any:
        source = Path(file_path)
        if not source.exists():
            raise SerenaSiteError(f"Media file not found: {source}")

        boundary = f"serena-{uuid.uuid4().hex}"
        mime_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
        file_bytes = source.read_bytes()

        parts: list[bytes] = []

        def add_field(name: str, value: str) -> None:
            parts.extend(
                [
                    f"--{boundary}\r\n".encode(),
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                    value.encode(),
                    b"\r\n",
                ]
            )

        if alt:
            add_field("alt", alt)
        if folder:
            add_field("folder", folder)

        parts.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="file"; filename="{source.name}"\r\n'.encode(),
                f"Content-Type: {mime_type}\r\n\r\n".encode(),
                file_bytes,
                b"\r\n",
                f"--{boundary}--\r\n".encode(),
            ]
        )

        candidate_bases = [self.config.api_base_path, *self.config.transport_aliases]
        seen: set[str] = set()
        last_error: SerenaSiteError | None = None

        for base in candidate_bases:
            if not base or base in seen:
                continue
            seen.add(base)

            request = Request(
                url=self._build_url("/media/upload", base),
                method="POST",
                headers=self._headers({"Content-Type": f"multipart/form-data; boundary={boundary}"}),
                data=b"".join(parts),
            )

            try:
                with urlopen(request) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                raw = error.read().decode("utf-8")
                try:
                    message = json.loads(raw)
                except json.JSONDecodeError:
                    message = {"error": raw}

                if error.code == 404:
                    last_error = SerenaSiteError(f"{error.code} {message}")
                    continue

                raise SerenaSiteError(f"{error.code} {message}") from error

        if last_error:
            raise last_error
        raise SerenaSiteError("Upload failed without a response.")
