# Serena Website Integration

This workspace can manage multiple websites that expose the reusable management contract.

Primary operator role name: `web-manager`

## Layout

- `sites/*.example.json` - committed manifest templates
- `sites/*.local.json` - local runtime manifests with secrets
- `scripts/serena_sites.py` - reusable client library
- `scripts/serena_site_cli.py` - CLI wrapper for common Serena actions
- `scripts/web_manager.py` - higher-level workflow wrapper for natural tasks

## Active Website

The current live starter integration is:

- `template`
- base URL: `http://34.124.244.233/template`
- default API base path: `/api/web-manager`
- Serena host allowlist: `34.143.206.68`

## Quick Start

Verify the live template site:

```bash
python3 scripts/serena_site_cli.py verify template
```

Search content:

```bash
python3 scripts/serena_site_cli.py search template --query serena
```

Create or update a post from a JSON file:

```bash
python3 scripts/serena_site_cli.py upsert-post template --file payloads/post.example.json
```

Create or update a page from a JSON file:

```bash
python3 scripts/serena_site_cli.py upsert-page template --file payloads/page.example.json
```

Update a global:

```bash
python3 scripts/serena_site_cli.py update-global template settings --file payloads/settings.example.json
```

Publish a managed document:

```bash
python3 scripts/serena_site_cli.py publish template posts --slug yesterday-blog-draft
```

Natural-task wrapper:

```bash
python3 scripts/web_manager.py template "search drafts about serena"
python3 scripts/web_manager.py template "publish serena-blog-smoke-test"
```

## Onboarding Another Similar Website

1. Ensure the website implements the same `/api/web-manager/*` contract.
2. Copy `sites/template.example.json` to `sites/<site>.local.json`.
3. Fill in:
   - `base_url`
   - `api_base_path`
   - `api_secret`
   - `allowed_capabilities`
4. Verify with:

```bash
python3 scripts/serena_site_cli.py verify <site>
```

5. Run a smoke test:
   - `status`
   - `search`
   - `approval`
   - `publish`

This keeps the client transferable across similar Payload/Next websites.

The bridge client now prefers `/api/web-manager/*` by default and only falls back to compatibility aliases such as `/api/serena/*` when necessary.
