# Website Manager

Preferred public role name: `web-manager`

This workspace now includes a higher-level `website-manager` workflow layer on top of the reusable Serena site client.

## Purpose

`website-manager` is the underlying workflow layer for the preferred `web-manager` role for CMS-backed websites that expose the `/api/serena/*` contract.

It is designed to work:

- under Serena now
- under Hutton later

The underlying site contract remains reusable and site-agnostic.

## Responsibilities

- verify connected websites
- search pages, posts, and services
- create/update pages and posts
- update globals like `header`, `footer`, and `settings`
- upload media
- request approval readiness
- publish approved content
- trigger revalidation

## Hutton Mapping

When this moves under Hutton, the recommended role name is:

- `web-manager`

The current files are already neutral enough to move with minimal change:

- `scripts/serena_sites.py`
- `scripts/serena_site_cli.py`
- `scripts/website_manager.py`
- `sites/*.json`

Only the transport contract name on websites still uses `/api/serena/*`. That can stay for compatibility or later be aliased to a more neutral route family.

## Usage

Examples:

```bash
python3 scripts/web_manager.py template "search drafts about serena"
python3 scripts/web_manager.py template "publish serena-blog-smoke-test"
python3 scripts/web_manager.py template "check approval for serena-blog-smoke-test"
python3 scripts/web_manager.py template "create a draft post" --payload-file payloads/post.example.json
```
