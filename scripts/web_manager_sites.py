from __future__ import annotations

import json
import mimetypes
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
SITES_DIR = ROOT / "sites"
DEFAULT_API_BASE_PATH = "/api/web-manager"
DEFAULT_TRANSPORT_ALIASES: list[str] = []
DEFAULT_MANAGED_COLLECTIONS = ["pages", "posts", "services"]
DEFAULT_ALLOWED_CAPABILITIES = [
    "auth:verify",
    "status:read",
    "pages:write",
    "posts:write",
    "services:write",
    "globals:write",
    "media:write",
    "approval:write",
    "publish:write",
    "search:read",
    "revalidate:write",
    "workflows:write",
    "operations:read",
    "cache:write",
]


class WebManagerError(RuntimeError):
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


def _site_manifest_path(site_name: str, *, local: bool) -> Path:
    suffix = "local" if local else "example"
    return SITES_DIR / f"{site_name}.{suffix}.json"


def load_site_config(site_name: str) -> SiteConfig:
    local_path = _site_manifest_path(site_name, local=True)
    example_path = _site_manifest_path(site_name, local=False)
    config_path = local_path if local_path.exists() else example_path

    if not config_path.exists():
        raise WebManagerError(f"Site manifest not found for '{site_name}'.")

    data = json.loads(config_path.read_text())

    return SiteConfig(
        site=data["site"],
        base_url=data["base_url"].rstrip("/"),
        api_base_path=data.get("api_base_path", DEFAULT_API_BASE_PATH),
        api_secret=data["api_secret"],
        managed_collections=list(data.get("managed_collections", DEFAULT_MANAGED_COLLECTIONS)),
        allowed_capabilities=list(data.get("allowed_capabilities", DEFAULT_ALLOWED_CAPABILITIES)),
        transport_aliases=list(data.get("transport_aliases", DEFAULT_TRANSPORT_ALIASES)),
    )


def validate_site_config(config: SiteConfig) -> list[str]:
    issues: list[str] = []

    if not config.site:
        issues.append("Missing site identifier.")
    if not config.base_url.startswith(("http://", "https://")):
        issues.append("Base URL must start with http:// or https://.")
    if not config.api_base_path.startswith("/"):
        issues.append("api_base_path must start with '/'.")
    if not config.api_secret:
        issues.append("Missing api_secret.")
    if not config.managed_collections:
        issues.append("No managed_collections configured.")
    if not config.allowed_capabilities:
        issues.append("No allowed_capabilities configured.")

    return issues


def build_site_manifest(
    *,
    site: str,
    base_url: str,
    api_secret: str,
    api_base_path: str = DEFAULT_API_BASE_PATH,
    managed_collections: list[str] | None = None,
    allowed_capabilities: list[str] | None = None,
    transport_aliases: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "site": site,
        "base_url": base_url.rstrip("/"),
        "api_base_path": api_base_path,
        "api_secret": api_secret,
        "managed_collections": managed_collections or DEFAULT_MANAGED_COLLECTIONS,
        "allowed_capabilities": allowed_capabilities or DEFAULT_ALLOWED_CAPABILITIES,
        "transport_aliases": transport_aliases or DEFAULT_TRANSPORT_ALIASES,
    }


def write_site_manifest(
    *,
    site: str,
    manifest: dict[str, Any],
    local: bool,
    force: bool = False,
) -> Path:
    path = _site_manifest_path(site, local=local)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and not force:
        raise WebManagerError(f"Manifest already exists: {path}")

    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return path


class WebManagerSiteClient:
    def __init__(self, config: SiteConfig):
        self.config = config

    def _candidate_bases(self) -> list[str]:
        seen: set[str] = set()
        ordered = [self.config.api_base_path, *self.config.transport_aliases]
        result: list[str] = []
        for base in ordered:
            if base and base not in seen:
                seen.add(base)
                result.append(base.rstrip("/"))
        return result

    def _build_url(self, route_path: str, base_path: str) -> str:
        return f"{self.config.base_url}{base_path}{route_path}"

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.config.api_secret}",
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        body = None
        request_headers = self._headers(headers)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        last_error: WebManagerError | None = None

        for base in self._candidate_bases():
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
                    last_error = WebManagerError(f"{error.code} {message}")
                    continue

                raise WebManagerError(f"{error.code} {message}") from error

        if last_error:
            raise last_error
        raise WebManagerError("Request failed without a response.")

    def verify(self) -> Any:
        return self._request("GET", "/auth/verify")

    def status(self) -> Any:
        return self._request("GET", "/status")

    def health(self) -> Any:
        return self._request("GET", "/operations/health")

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

    def publish(
        self,
        collection: str,
        *,
        doc_id: str | None = None,
        slug: str | None = None,
        require_approval: bool = True,
    ) -> Any:
        body: dict[str, Any] = {"collection": collection, "requireApproval": require_approval}
        if doc_id is not None:
            body["id"] = doc_id
        if slug is not None:
            body["slug"] = slug
        return self._request("POST", "/publish", payload=body)

    def publish_bundle(
        self,
        collection: str,
        *,
        doc_id: str | None = None,
        slug: str | None = None,
        revalidate_path: str | None = None,
        revalidate_tag: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {"collection": collection}
        if doc_id is not None:
            body["id"] = doc_id
        if slug is not None:
            body["slug"] = slug
        if revalidate_path is not None:
            body["revalidatePath"] = revalidate_path
        if revalidate_tag is not None:
            body["revalidateTag"] = revalidate_tag
        return self._request("POST", "/workflows/publish-bundle", payload=body)

    def revalidate(self, *, path: str | None = None, slug: str | None = None, tag: str | None = None) -> Any:
        return self._request("POST", "/revalidate", payload={"path": path, "slug": slug, "tag": tag})

    def cache(
        self,
        *,
        path: str | None = None,
        slug: str | None = None,
        tag: str | None = None,
        paths: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Any:
        return self._request(
            "POST",
            "/operations/cache",
            payload={
                "path": path,
                "slug": slug,
                "tag": tag,
                "paths": paths or [],
                "tags": tags or [],
            },
        )

    def upload_media(self, file_path: str, *, alt: str | None = None, folder: str | None = None) -> Any:
        source = Path(file_path)
        if not source.exists():
            raise WebManagerError(f"Media file not found: {source}")

        boundary = f"web-manager-{uuid.uuid4().hex}"
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

        last_error: WebManagerError | None = None
        for base in self._candidate_bases():
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
                    last_error = WebManagerError(f"{error.code} {message}")
                    continue

                raise WebManagerError(f"{error.code} {message}") from error

        if last_error:
            raise last_error
        raise WebManagerError("Upload failed without a response.")

    def describe_local_config(self) -> dict[str, Any]:
        return asdict(self.config)
