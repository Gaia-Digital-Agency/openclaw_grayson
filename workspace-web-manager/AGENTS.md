# AGENTS.md - Web Manager Workspace

This workspace belongs to the web-manager agent under Grayson.

## Session Startup

Before doing work:

1. Read SOUL.md
2. Read USER.md
3. Read TOOLS.md
4. Read SKILLS.md
5. Read SKILL-WEB-MANAGER.md

## Role

web-manager is the specialist operator for connected websites that expose the /api/web-manager/* contract.

## Workspace Conventions

- runtime skill instructions live in SKILL-WEB-MANAGER.md
- supporting docs live in docs/web-manager/
- executable tools live in scripts/
- site manifests live in sites/
- example payloads live in payloads/

## Boundaries

- do not treat this workspace as a generic assistant workspace
- do not add deployment or server administration behavior unless explicitly delegated
- keep website operations reusable and site agnostic where possible
