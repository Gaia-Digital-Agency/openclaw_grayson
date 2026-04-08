# Web Manager

`web-manager` is the preferred agent role for operating connected websites.

It sits above the low-level site client and uses the reusable `/api/web-manager/*` contract on compatible sites.

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
python3 scripts/web_manager.py template "search drafts about the homepage"
python3 scripts/web_manager.py template "check approval for yesterday-blog-draft"
python3 scripts/web_manager.py template "publish bundle yesterday-blog-draft"
```

For create/update tasks that need structured content, pass a payload file:

```bash
python3 scripts/web_manager.py template "create a draft post" --payload-file payloads/post.example.json
```

For direct operational commands, use the canonical CLI:

```bash
python3 scripts/web_manager_cli.py health template
python3 scripts/web_manager_cli.py publish-bundle template posts --slug yesterday-blog-draft --revalidate-tag posts-sitemap
python3 scripts/web_manager_cli.py cache template --paths / /posts/yesterday-blog-draft --tags posts-sitemap
python3 scripts/web_manager_cli.py doctor template
```
