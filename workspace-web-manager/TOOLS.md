# TOOLS.md

## Available MCP Servers

- `fetch` — Primary tool for all CMS API interactions (login, create posts, list posts, upload media)
- `filesystem` — Read/write workspace files
- `playwright` — Browser automation (use only when fetch is insufficient)

## CMS API

All Payload CMS operations use the `fetch` tool with JSON payloads. See SKILL-BLOG.md for endpoint details.

## Usage Priority

1. `fetch` for API calls (authentication, CRUD operations)
2. `filesystem` for reading skill files and workspace docs
3. `playwright` only as a last resort for browser-based tasks
