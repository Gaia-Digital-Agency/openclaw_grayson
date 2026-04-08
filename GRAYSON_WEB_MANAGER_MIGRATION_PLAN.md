# Grayson Web-Manager Migration Plan

## Goal

Move from the current bridge implementation to a canonical Grayson-owned `web-manager` system without breaking existing website integrations.

## Current State

### Website Side

The `template` website on `34.124.244.233` already exposes the working management contract under:

- `/api/web-manager/*`

Verified live capabilities:

- auth verify
- status
- page upsert
- post upsert
- global update
- media upload
- approval request
- publish
- content search
- revalidate

### Bridge Side

The current bridge client exists in:

- `34.143.206.68:/home/azlan/.openclaw/workspace`

This includes:

- site manifests
- low-level client
- CLI wrapper
- workflow wrapper

This bridge should be treated as transitional.

## Target State

Canonical ownership moves to Grayson:

- agent: `web-manager`
- site registry: Grayson-managed
- workflow policies: Grayson-managed
- secret references: Grayson-managed

The existing website API contract remains reusable and can continue to function during migration.

## Migration Phases

### Phase 1. Canonicalize Role Ownership

Status: ready now

Actions:

- declare Grayson `web-manager` as the canonical owner
- treat the existing bridge as temporary tooling only
- freeze further legacy naming decisions

### Phase 2. Lift the Site Registry Into Grayson

Actions:

- move manifest model into Grayson
- convert raw secret storage to secret references
- normalize manifest schema
- preserve current fields:
  - `site`
  - `base_url`
  - `managed_collections`
  - `allowed_capabilities`

Deliverable:

- Grayson registry of connected websites

### Phase 3. Lift the Workflow Layer Into Grayson

Actions:

- move natural task interpretation into Grayson `web-manager`
- re-implement current bridge workflow commands in Grayson-native form
- keep the same operations:
  - verify
  - status
  - search
  - upsert page
  - upsert post
  - update global
  - upload media
  - request approval
  - publish
  - revalidate

Deliverable:

- Grayson `web-manager` runtime that no longer depends on the current bridge workspace

### Phase 4. Introduce Neutral Website Route Aliases

Actions:

- make `/api/web-manager/*` the default route family for all new Grayson clients
- optionally support `/api/agent/*` later if needed

Recommendation:

- aliases are already in place on the reference site
- Grayson should now prefer `/api/web-manager/*`
Deliverable:

- neutral transport naming without breaking existing sites

### Phase 5. Expand Site Compatibility

Actions:

- define minimum compatibility checklist for future sites
- standardize smoke tests
- publish onboarding checklist
- add optional capability flags for site-specific features

Deliverable:

- reusable onboarding path for each new compatible website

## Compatibility Strategy

During migration, preserve backward compatibility:

- same request/response shapes
- same auth semantics
- same capability names
- same collection-based workflow model

That allows:

- old bridge tools to keep working
- Grayson `web-manager` to adopt the contract incrementally

## Secret Handling Plan

Current bridge state:

- raw secret may exist in local manifest for operational convenience

Target Grayson state:

- replace `api_secret` with `api_secret_ref`
- store secret in Grayson-managed secret store
- never commit raw live secrets in canonical manifests

## Recommended Immediate Next Steps

1. Create the Grayson `web-manager` manifest schema.
2. Create the Grayson `web-manager` operation interface matching the current contract.
3. Default Grayson manifests to `api_base_path=/api/web-manager`.
4. Leave the current bridge untouched until Grayson is operational.

## Recommended Deferred Steps

After Grayson `web-manager` is active:

1. Move site manifests from bridge workspace into Grayson.
2. Move secrets into Grayson-managed secret storage.
3. Retire bridge-only docs.
4. Remove any remaining legacy naming once all clients are moved.

## Success Criteria

Migration is complete when:

- Grayson `web-manager` can operate connected sites directly
- no production workflow depends on the transitional bridge
- all site manifests live in Grayson
- secrets are reference-based, not inline
- `/api/web-manager/*` is the default route family for Grayson clients
- onboarding a new compatible site uses the canonical Grayson flow

## Canonical Position

From this point forward:

- Grayson `web-manager` is the canonical operational owner
- the current bridge is an implementation bridge only
- the current `template` site is the reference integration, not the final naming authority
