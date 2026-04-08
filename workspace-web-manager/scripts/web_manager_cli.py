from __future__ import annotations

import argparse
import json
from pathlib import Path

from web_manager_sites import (
    DEFAULT_ALLOWED_CAPABILITIES,
    DEFAULT_MANAGED_COLLECTIONS,
    WebManagerError,
    WebManagerSiteClient,
    build_site_manifest,
    load_site_config,
    validate_site_config,
    write_site_manifest,
)


def load_json_payload(inline_json: str | None, file_path: str | None) -> dict:
    if inline_json:
        return json.loads(inline_json)
    if file_path:
        return json.loads(Path(file_path).read_text())
    raise WebManagerError("Provide either --json or --file.")


def build_client(site: str) -> WebManagerSiteClient:
    return WebManagerSiteClient(load_site_config(site))


def main() -> int:
    parser = argparse.ArgumentParser(description="Grayson web-manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify")
    verify.add_argument("site")

    status = subparsers.add_parser("status")
    status.add_argument("site")

    health = subparsers.add_parser("health")
    health.add_argument("site")

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("site")

    search = subparsers.add_parser("search")
    search.add_argument("site")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)

    upsert_page = subparsers.add_parser("upsert-page")
    upsert_page.add_argument("site")
    upsert_page.add_argument("--json")
    upsert_page.add_argument("--file")

    upsert_post = subparsers.add_parser("upsert-post")
    upsert_post.add_argument("site")
    upsert_post.add_argument("--json")
    upsert_post.add_argument("--file")

    update_global = subparsers.add_parser("update-global")
    update_global.add_argument("site")
    update_global.add_argument("global_slug")
    update_global.add_argument("--json")
    update_global.add_argument("--file")

    approval = subparsers.add_parser("approval")
    approval.add_argument("site")
    approval.add_argument("collection")
    approval_group = approval.add_mutually_exclusive_group(required=True)
    approval_group.add_argument("--id")
    approval_group.add_argument("--slug")

    publish = subparsers.add_parser("publish")
    publish.add_argument("site")
    publish.add_argument("collection")
    publish_group = publish.add_mutually_exclusive_group(required=True)
    publish_group.add_argument("--id")
    publish_group.add_argument("--slug")
    publish.add_argument("--skip-approval", action="store_true")

    publish_bundle = subparsers.add_parser("publish-bundle")
    publish_bundle.add_argument("site")
    publish_bundle.add_argument("collection")
    publish_bundle_group = publish_bundle.add_mutually_exclusive_group(required=True)
    publish_bundle_group.add_argument("--id")
    publish_bundle_group.add_argument("--slug")
    publish_bundle.add_argument("--revalidate-path")
    publish_bundle.add_argument("--revalidate-tag")

    revalidate = subparsers.add_parser("revalidate")
    revalidate.add_argument("site")
    revalidate.add_argument("--path")
    revalidate.add_argument("--slug")
    revalidate.add_argument("--tag")

    cache = subparsers.add_parser("cache")
    cache.add_argument("site")
    cache.add_argument("--path")
    cache.add_argument("--slug")
    cache.add_argument("--tag")
    cache.add_argument("--paths", nargs="*")
    cache.add_argument("--tags", nargs="*")

    upload = subparsers.add_parser("upload-media")
    upload.add_argument("site")
    upload.add_argument("file_path")
    upload.add_argument("--alt")
    upload.add_argument("--folder")

    onboard = subparsers.add_parser("onboard")
    onboard.add_argument("site")
    onboard.add_argument("--base-url", required=True)
    onboard.add_argument("--api-secret", required=True)
    onboard.add_argument("--api-base-path", default="/api/web-manager")
    onboard.add_argument("--local", action="store_true")
    onboard.add_argument("--force", action="store_true")
    onboard.add_argument("--managed-collections", nargs="*", default=DEFAULT_MANAGED_COLLECTIONS)
    onboard.add_argument("--allowed-capabilities", nargs="*", default=DEFAULT_ALLOWED_CAPABILITIES)

    args = parser.parse_args()

    try:
        if args.command == "onboard":
            manifest = build_site_manifest(
                site=args.site,
                base_url=args.base_url,
                api_secret=args.api_secret,
                api_base_path=args.api_base_path,
                managed_collections=list(args.managed_collections),
                allowed_capabilities=list(args.allowed_capabilities),
            )
            path = write_site_manifest(
                site=args.site,
                manifest=manifest,
                local=args.local,
                force=args.force,
            )
            print(json.dumps({"ok": True, "site": args.site, "path": str(path), "manifest": manifest}, indent=2))
            return 0

        client = build_client(args.site)

        if args.command == "verify":
            result = client.verify()
        elif args.command == "status":
            result = client.status()
        elif args.command == "health":
            result = client.health()
        elif args.command == "doctor":
            issues = validate_site_config(load_site_config(args.site))
            result = {
                "ok": len(issues) == 0,
                "site": args.site,
                "manifestIssues": issues,
                "config": client.describe_local_config(),
                "verify": client.verify(),
                "status": client.status(),
                "health": client.health(),
            }
        elif args.command == "search":
            result = client.search(args.query, args.limit)
        elif args.command == "upsert-page":
            result = client.upsert_page(load_json_payload(args.json, args.file))
        elif args.command == "upsert-post":
            result = client.upsert_post(load_json_payload(args.json, args.file))
        elif args.command == "update-global":
            result = client.update_global(args.global_slug, load_json_payload(args.json, args.file))
        elif args.command == "approval":
            result = client.request_approval(args.collection, doc_id=args.id, slug=args.slug)
        elif args.command == "publish":
            result = client.publish(
                args.collection,
                doc_id=args.id,
                slug=args.slug,
                require_approval=not args.skip_approval,
            )
        elif args.command == "publish-bundle":
            result = client.publish_bundle(
                args.collection,
                doc_id=args.id,
                slug=args.slug,
                revalidate_path=args.revalidate_path,
                revalidate_tag=args.revalidate_tag,
            )
        elif args.command == "revalidate":
            result = client.revalidate(path=args.path, slug=args.slug, tag=args.tag)
        elif args.command == "cache":
            result = client.cache(
                path=args.path,
                slug=args.slug,
                tag=args.tag,
                paths=args.paths,
                tags=args.tags,
            )
        elif args.command == "upload-media":
            result = client.upload_media(args.file_path, alt=args.alt, folder=args.folder)
        else:
            raise WebManagerError(f"Unsupported command: {args.command}")

        print(json.dumps(result, indent=2))
        return 0
    except WebManagerError as error:
        print(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
