# Web Manager

`web-manager` is the preferred agent role for operating connected websites.

It sits above the low-level Serena site client and uses the reusable `/api/serena/*` contract already installed on compatible sites.

## Responsibilities

- verify site connectivity
- search content across connected sites
- create and update pages and posts
- update globals such as `header`, `footer`, and `settings`
- upload media
- request approval readiness
- publish approved content
- revalidate content paths and tags

## Hutton

When this moves under Hutton, the recommended agent name remains:

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
