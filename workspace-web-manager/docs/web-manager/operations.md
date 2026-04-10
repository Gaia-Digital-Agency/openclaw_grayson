# Grayson Web-Manager Operation Interface

This document defines the canonical operation interface for Grayson `web-manager`.

Default transport base path:

- `/api/web-manager`

## Manifest Contract

Grayson should load site manifests that validate against:

- [docs/web-manager/manifest.schema.json](/Users/rogerwoolie/Downloads/gaiada_newai/docs/web-manager/manifest.schema.json)

### Canonical Example

```json
{
  "site": "template",
  "base_url": "http://34.124.244.233/templategda",
  "api_base_path": "/api/web-manager",
  "api_secret_ref": "secret://grayson/sites/templategda",
  "managed_collections": ["pages", "posts", "services"],
  "allowed_capabilities": [
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
    "revalidate:write"
  ],
  "environment": "production",
  "policy": {
    "publish_requires_approval": true,
    "allow_global_updates": true,
    "allow_media_uploads": true
  }
}
```

Concrete example file:

- [docs/web-manager/manifest.example.json](/Users/rogerwoolie/Downloads/gaiada_newai/docs/web-manager/manifest.example.json)

## Operation Model

Grayson `web-manager` should expose a stable internal operation interface regardless of the target site.

Each operation should resolve:

- site manifest
- secret from `api_secret_ref`
- target URL as `base_url + api_base_path + route`
- no legacy fallback should be assumed

## Operation Catalog

### 1. `verify_site`

Purpose:

- verify auth and route availability

Internal input:

```json
{
  "site": "template"
}
```

Transport:

- `GET {base_url}{api_base_path}/auth/verify`

Expected output:

```json
{
  "ok": true,
  "authenticated": true,
  "clientIp": "34.143.206.68",
  "scope": ["auth:verify", "status:read"]
}
```

### 2. `get_site_status`

Purpose:

- discover capabilities and current service readiness

Internal input:

```json
{
  "site": "template"
}
```

Transport:

- `GET {base_url}{api_base_path}/status`

### 3. `search_content`

Purpose:

- search managed content across collections

Internal input:

```json
{
  "site": "template",
  "query": "bali villas",
  "limit": 10
}
```

Transport:

- `GET {base_url}{api_base_path}/content/search?q=...&limit=...`

### 4. `upsert_page`

Purpose:

- create or update a page

Internal input:

```json
{
  "site": "template",
  "payload": {
    "title": "About Web Manager",
    "slug": "about-web-manager",
    "status": "draft",
    "meta": {
      "title": "About Web Manager",
      "description": "Draft page created by web-manager"
    }
  }
}
```

Transport:

- `POST {base_url}{api_base_path}/pages/upsert`

### 5. `upsert_post`

Purpose:

- create or update a post/article

Internal input:

```json
{
  "site": "template",
  "payload": {
    "title": "Yesterday Blog Draft",
    "slug": "yesterday-blog-draft",
    "status": "draft",
    "meta": {
      "title": "Yesterday Blog Draft",
      "description": "Draft post created by web-manager"
    }
  }
}
```

Transport:

- `POST {base_url}{api_base_path}/posts/upsert`

### 6. `update_global`

Purpose:

- update a supported global

Internal input:

```json
{
  "site": "template",
  "global": "settings",
  "payload": {
    "contactEmail": "contact@example.com"
  }
}
```

Transport:

- `POST {base_url}{api_base_path}/globals/update`

### 7. `upload_media`

Purpose:

- upload media into the site media collection

Internal input:

```json
{
  "site": "template",
  "file_path": "/path/to/image.jpg",
  "alt": "Homepage hero",
  "folder": "homepage"
}
```

Transport:

- `POST {base_url}{api_base_path}/media/upload`

### 8. `request_approval`

Purpose:

- check whether a managed document is ready to publish

Internal input:

```json
{
  "site": "template",
  "collection": "posts",
  "slug": "yesterday-blog-draft"
}
```

Transport:

- `POST {base_url}{api_base_path}/approval/request`

### 9. `publish_document`

Purpose:

- publish an approval-ready managed document

Internal input:

```json
{
  "site": "template",
  "collection": "posts",
  "slug": "yesterday-blog-draft",
  "require_approval": true
}
```

Transport:

- `POST {base_url}{api_base_path}/publish`

### 10. `revalidate_target`

Purpose:

- revalidate a page path, slug, or tag

Internal input:

```json
{
  "site": "template",
  "slug": "yesterday-blog-draft"
}
```

Transport:

- `POST {base_url}{api_base_path}/revalidate`

## Natural Task Resolution

Grayson `web-manager` should map natural requests into this operation catalog.

Examples:

- "search drafts about bali villas"
  - `search_content`

- "update the homepage CTA"
  - `upsert_page`

- "post the blog we wrote yesterday"
  - `upsert_post`
  - `request_approval`
  - `publish_document`

- "publish the approved bali article"
  - `request_approval`
  - `publish_document`

## Transport Rules

- use `api_base_path` from manifest
- do not assume or require any legacy alias
- log any site-specific transport divergence explicitly

## Output Shape

At the Grayson layer, operations should return a normalized envelope:

```json
{
  "site": "template",
  "operation": "publish_document",
  "transport": {
    "base_url": "http://34.124.244.233/templategda",
    "api_base_path": "/api/web-manager"
  },
  "result": {}
}
```

This keeps the runtime stable even if site-specific responses evolve.
