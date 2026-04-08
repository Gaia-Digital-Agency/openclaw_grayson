from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from serena_sites import SerenaSiteClient, SerenaSiteError, load_site_config


def load_payload(inline_json: str | None, file_path: str | None) -> dict[str, Any] | None:
    if inline_json:
        return json.loads(inline_json)
    if file_path:
        return json.loads(Path(file_path).read_text())
    return None


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def infer_collection(task: str) -> str | None:
    lowered = task.lower()
    if any(word in lowered for word in ["blog", "post", "article"]):
        return "posts"
    if any(word in lowered for word in ["service", "services"]):
        return "services"
    if any(word in lowered for word in ["page", "homepage", "landing"]):
        return "pages"
    return None


def infer_global(task: str) -> str | None:
    lowered = task.lower()
    if "header" in lowered:
        return "header"
    if "footer" in lowered:
        return "footer"
    if any(word in lowered for word in ["settings", "contact email", "whatsapp", "social links"]):
        return "settings"
    return None


def infer_slug(task: str) -> str | None:
    quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', task)
    for left, right in quoted:
        value = left or right
        if value:
            return value.strip()

    token_match = re.search(r"\b[a-z0-9]+(?:-[a-z0-9]+)+\b", task.lower())
    if token_match:
        return token_match.group(0)

    return None


def infer_query(task: str) -> str:
    lowered = normalize_text(task)
    lowered = re.sub(r"^(search|find|look for|look up)\s+", "", lowered, flags=re.IGNORECASE)
    return lowered


def interpret_task(task: str) -> dict[str, Any]:
    normalized = normalize_text(task)
    lowered = normalized.lower()
    collection = infer_collection(lowered)
    global_slug = infer_global(lowered)
    slug = infer_slug(normalized)

    if any(word in lowered for word in ["search", "find", "look for", "look up"]):
        return {
            "action": "search",
            "query": infer_query(normalized),
        }

    if "publish" in lowered:
        return {
            "action": "publish",
            "collection": collection or "posts",
            "slug": slug,
        }

    if "approval" in lowered or "approve" in lowered or "ready to publish" in lowered:
        return {
            "action": "approval",
            "collection": collection or "posts",
            "slug": slug,
        }

    if global_slug and any(word in lowered for word in ["update", "change", "set"]):
        return {
            "action": "update-global",
            "global": global_slug,
        }

    if any(word in lowered for word in ["create", "draft", "update", "edit", "rewrite"]):
        return {
            "action": "upsert",
            "collection": collection or "pages",
            "slug": slug,
        }

    return {
        "action": "status",
    }


def run_task(client: SerenaSiteClient, task: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    plan = interpret_task(task)
    action = plan["action"]

    if action == "status":
        return {"plan": plan, "result": client.status()}

    if action == "search":
        return {"plan": plan, "result": client.search(plan["query"])}

    if action == "approval":
        if not plan.get("slug"):
            raise SerenaSiteError("Approval task needs a slug or quoted identifier.")
        return {
            "plan": plan,
            "result": client.request_approval(plan["collection"], slug=plan["slug"]),
        }

    if action == "publish":
        if not plan.get("slug"):
            raise SerenaSiteError("Publish task needs a slug or quoted identifier.")
        return {
            "plan": plan,
            "result": client.publish(plan["collection"], slug=plan["slug"]),
        }

    if action == "update-global":
        if not payload:
            raise SerenaSiteError("Global update tasks require --payload-json or --payload-file.")
        return {
            "plan": plan,
            "result": client.update_global(plan["global"], payload),
        }

    if action == "upsert":
        if not payload:
            return {
                "plan": plan,
                "result": {
                    "ok": False,
                    "needsPayload": True,
                    "message": "Provide --payload-json or --payload-file for create/update tasks.",
                    "suggestedCollection": plan["collection"],
                },
            }

        collection = plan["collection"]
        if collection == "posts":
            result = client.upsert_post(payload)
        elif collection == "pages":
            result = client.upsert_page(payload)
        else:
            raise SerenaSiteError(f"High-level upsert for '{collection}' is not implemented yet.")

        return {"plan": plan, "result": result}

    raise SerenaSiteError(f"Unsupported action plan: {action}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Website manager workflow layer")
    parser.add_argument("site")
    parser.add_argument("task")
    parser.add_argument("--payload-json")
    parser.add_argument("--payload-file")
    args = parser.parse_args()

    try:
        client = SerenaSiteClient(load_site_config(args.site))
        payload = load_payload(args.payload_json, args.payload_file)
        result = run_task(client, args.task, payload)
        print(json.dumps(result, indent=2))
        return 0
    except SerenaSiteError as error:
        print(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
