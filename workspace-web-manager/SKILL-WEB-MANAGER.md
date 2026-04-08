# SKILL-WEB-MANAGER.md

Use this skill when Grayson or a delegated operator needs to manage connected websites through the /api/web-manager/* contract.

## Responsibilities

- verify site connectivity and capability status
- search content across connected sites
- create and update pages and posts
- update globals such as header, footer, and settings
- upload media
- run approval readiness checks
- publish approved content
- trigger path or tag revalidation

## Entry Points

Use the natural task wrapper for operator facing instructions.

Examples:
python3 scripts/web_manager.py template "search drafts about the homepage"
python3 scripts/web_manager.py template "check approval for yesterday-blog-draft"
python3 scripts/web_manager.py template "publish bundle yesterday-blog-draft"

Use the lower level CLI for direct operations.

Examples:
python3 scripts/web_manager_cli.py health template
python3 scripts/web_manager_cli.py doctor template
python3 scripts/web_manager_cli.py publish-bundle template posts --slug yesterday-blog-draft --revalidate-tag posts-sitemap

For create or update tasks that need structured content, pass a payload file.

Example:
python3 scripts/web_manager.py template "create a draft post" --payload-file payloads/post.example.json

## Working Rules

- prefer /api/web-manager/* as the canonical website interface
- treat this workspace as the operational implementation for the web-manager agent under Grayson
- keep website specific manifests under sites/
- keep payload examples under payloads/
- keep supporting design and migration docs under docs/web-manager/

## Supporting Docs

- docs/web-manager/overview.md
- docs/web-manager/spec.md
- docs/web-manager/operations.md
- docs/web-manager/sites.md
- docs/web-manager/workflow-layer.md
- docs/web-manager/migration-plan.md
- docs/web-manager/manifest.schema.json
- docs/web-manager/manifest.example.json
