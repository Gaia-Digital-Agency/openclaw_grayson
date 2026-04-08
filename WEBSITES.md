# Grayson Web-Manager Site Integration

This workspace can manage multiple websites that expose the reusable management contract.

Primary operator role name: `web-manager`

## Layout

- `sites/*.example.json` - committed manifest templates
- `sites/*.local.json` - local runtime manifests with secrets
- `scripts/web_manager_sites.py` - canonical reusable client library
- `scripts/web_manager_cli.py` - canonical CLI wrapper
- `scripts/web_manager.py` - higher-level workflow wrapper for natural tasks

## Active Website

The current live starter integration is:

- `template`
- base URL: `http://34.124.244.233/template`
- default API base path: `/api/web-manager`
- current bridge host allowlist: `34.143.206.68`

## Quick Start

Verify the live template site:

```bash
python3 scripts/web_manager_cli.py verify template
```

Search content:

```bash
python3 scripts/web_manager_cli.py search template --query template
```

Create or update a post from a JSON file:

```bash
python3 scripts/web_manager_cli.py upsert-post template --file payloads/post.example.json
```

Create or update a page from a JSON file:

```bash
python3 scripts/web_manager_cli.py upsert-page template --file payloads/page.example.json
```

Update a global:

```bash
python3 scripts/web_manager_cli.py update-global template settings --file payloads/settings.example.json
```

Publish a managed document:

```bash
python3 scripts/web_manager_cli.py publish-bundle template posts --slug yesterday-blog-draft --revalidate-tag posts-sitemap
```

Natural-task wrapper:

```bash
python3 scripts/web_manager.py template "search drafts about the homepage"
python3 scripts/web_manager.py template "publish bundle yesterday-blog-draft"
```

## Onboarding Another Similar Website

1. Ensure the website implements the same `/api/web-manager/*` contract.
2. Generate a manifest:

```bash
python3 scripts/web_manager_cli.py onboard <site> \
  --base-url https://example.com \
  --api-secret replace-me \
  --local
```

3. Verify with:

```bash
python3 scripts/web_manager_cli.py doctor <site>
```

4. Run a smoke test:
   - `status`
   - `health`
   - `search`
   - `approval`
   - `publish-bundle`

This keeps the client transferable across similar Payload/Next websites.
