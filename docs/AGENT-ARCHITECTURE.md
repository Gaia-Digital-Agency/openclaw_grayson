# Agent Architecture

Grayson is a multi-agent AI system built on OpenClaw.

## Agents

| Agent | ID | Workspace |
|-------|----|-----------|
| **Grayson** | main | workspace-main |
| **Sales** | sales | workspace-sales |
| **CRM** | crm | workspace-crm |
| **Accounts** | accounts | workspace-accounts |
| **SocMed** | socmed | workspace-socmed |
| **SEO** | seo | workspace-seo |
| **Ads** | ads | workspace-ads |
| **Branding** | branding | workspace-branding |
| **Copywriter** | copywriter | workspace-copywriter |
| **Web Manager** | web-manager | workspace-web-manager |

## Delegation

Grayson (main) delegates to: sales, crm, accounts, socmed, seo, ads, branding, copywriter, web-manager

## Configuration

- State dir: `/opt/.openclaw-gda`
- Config: `/opt/.openclaw-gda/openclaw.json`
- Gateway port: 18889
- Model: deepseek/deepseek-chat (fallback: google/gemini-2.5-flash)

## Workspace Structure

Each agent workspace follows:

```
workspace-{agent}/
  IDENTITY.md      -- Name, role
  SOUL.md          -- Voice and output rules
  USER.md          -- Owner context
  TOOLS.md         -- Available tools
  SKILLS.md        -- Skill index
  SKILL-*.md       -- Specific workflows
```
