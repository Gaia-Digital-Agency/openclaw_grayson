# Grayson Web-Manager Spec

## Purpose

`web-manager` is Grayson's operational agent for managing connected websites.

It is responsible for structured website operations across multiple similar CMS-backed sites, especially Payload + Next.js sites that expose a standard management API.

This is the canonical role definition. Existing bridge tooling should be treated only as a transitional implementation on the path to this Grayson-owned model.

## Scope

`web-manager` is responsible for:

- site verification and capability discovery
- page creation and updates
- post/article creation and updates
- service/content entry updates where supported
- global configuration updates such as header, footer, and settings
- media uploads
- approval readiness checks
- publish operations
- cross-site content search
- cache/path revalidation

`web-manager` is not responsible for:

- arbitrary deployment shell access by default
- server administration unrelated to site content operations
- acting as a general-purpose assistant
- sending external communications unless explicitly delegated

## Architecture

The canonical architecture has three layers.

### 1. Grayson Agent Layer

Grayson owns the decision-making role:

- agent name: `web-manager`
- interprets natural requests
- selects target site
- decides whether to draft, request approval, publish, or revalidate

### 2. Website Registry Layer

Grayson maintains a site registry with one manifest per connected website.

Each manifest defines:

- `site`
- `base_url`
- auth secret reference
- managed collections
- allowed capabilities
- optional environment tags

### 3. Website Execution Layer

Each website exposes a reusable management contract.

Preferred route family:

- `/api/web-manager/*`

Optional future neutral alternative:

- `/api/agent/*`

Grayson `web-manager` should prefer `/api/web-manager/*` by default.

## Required Website Contract

A compatible website must expose:

- `GET /api/web-manager/auth/verify`
- `GET /api/web-manager/status`
- `POST /api/web-manager/pages/upsert`
- `POST /api/web-manager/posts/upsert`
- `POST /api/web-manager/globals/update`
- `POST /api/web-manager/media/upload`
- `POST /api/web-manager/approval/request`
- `POST /api/web-manager/publish`
- `GET /api/web-manager/content/search`
- `POST /api/web-manager/revalidate`

Optional future endpoints:

- `POST /api/web-manager/workflows/publish-bundle`
- `GET /api/web-manager/approvals/queue`
- `POST /api/web-manager/services/upsert`
- `POST /api/web-manager/forms/upsert`

## Agent Behavior

When receiving a natural-language instruction, `web-manager` should:

1. identify the target site
2. identify the intended content type
3. choose the correct operation
4. require structured payload where needed
5. run approval checks before publish by default
6. only bypass approval when explicitly instructed or policy allows
7. revalidate relevant content after changes

## Natural Task Mapping

Examples:

- "update the homepage CTA"
  - target likely `pages`
  - operation: page update

- "post the blog we wrote yesterday"
  - target likely `posts`
  - operation: post upsert, approval, publish

- "search drafts about bali villas"
  - operation: content search

- "publish the approved bali article"
  - operation: approval check, publish

## Approval Policy

Default policy:

- draft creation: allowed
- draft update: allowed
- global updates: allowed, but auditable
- media upload: allowed
- publish: requires approval check first

Approval readiness should validate at minimum:

- title exists
- slug exists
- required content body exists
- collection-specific required fields exist

Grayson may later add stronger editorial policy such as:

- min body length
- SEO completeness
- category assignment
- media presence

## Security Model

Required:

- shared secret or equivalent agent auth
- IP allowlisting when practical
- narrow endpoint surface
- audit logging

Recommended:

- secret storage outside committed manifests
- per-site secret rotation support
- capability-based restrictions
- environment separation for staging vs production

## Site Manifest Schema

Canonical manifest fields:

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
  "environment": "production"
}
```

Note:

- committed examples should never store live secrets
- local manifests may temporarily contain raw secrets during migration
- Grayson should move to secret references as the canonical model
- Grayson manifests should default `api_base_path` to `/api/web-manager`

## Transferability Rules

To keep `web-manager` transferable across similar sites:

- use capability discovery instead of hardcoding assumptions
- prefer collection-based operations over site-specific handlers
- keep manifests data-driven
- keep workflow policies separate from transport implementation
- avoid branding-specific logic in the core agent

## Current Reference Implementation

The current reference implementation consists of:

- website contract on `34.124.244.233` `template`
- bridge client in `34.143.206.68 ~/.openclaw/workspace`

This implementation proves the contract, but Grayson `web-manager` is the canonical owner going forward.
