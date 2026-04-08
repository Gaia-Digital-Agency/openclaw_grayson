# Web Manager

`web-manager` is the preferred agent role for operating connected websites.

It sits above the low-level site client and uses the reusable `/api/web-manager/*` contract on compatible sites, with `/api/serena/*` retained only as a compatibility alias where needed.

## Responsibilities

- verify site connectivity
- search content across connected sites
- create and update pages and posts
- update globals such as `header`, `footer`, and `settings`
- upload media
- request approval readiness
- publish approved content
- revalidate content paths and tags

## Grayson

Under Grayson, the canonical agent name is:

- `web-manager`

That keeps the operational role short and clear.

## Entry Point

Use:

```bash
python3 scripts/web_manager.py template "search drafts about serena"
python3 scripts/web_manager.py template "check approval for serena-blog-smoke-test"
python3 scripts/web_manager.py template "publish serena-blog-smoke-test"
```

For create/update tasks that need structured content, pass a payload file:

```bash
python3 scripts/web_manager.py template "create a draft post" --payload-file payloads/post.example.json
```
