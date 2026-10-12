# Libras agent project context

Prepare only a minimal Python 3.11 agentic-system base using hosted OpenAI Agents API while retaining future Teams and bounded documentary, database-catalog, and ClickUp evidence boundaries. This is not a full Libras migration.

## Current boundary

- OpenAI owns orchestration and session state. The local gateway supplies an explicit existing agent ID/key, optional model override, environment type none, and the complete three-function allowlist. Do not introduce Agents SDK Agent/Runner or a local Responses reasoning loop.
- The bootstrap provides offline request manifests and injected async read callbacks, bounded to six dispatches, 30 seconds each, 2000 query characters, and 256000 UTF-8 evidence bytes. Local observation is bounded to 120 seconds; stream closure does not confirm remote cancellation.
- Hosted sessions retain state and currently support US residency only, without ZDR. Local SDK tracing flags do not change Agents API retention. Session cancellation, deletion, recovery, and continuation require later lifecycle integration.
- Teams ingress, authentication, Azure clients, and ClickUp adapters are not wired. Environment-variable presence does not establish live readiness.
- `C:\cw\Libras` is a read-only dirty reference. Do not modify it, import its application globals or bundled dependencies, or add it to `PYTHONPATH`.
- Preserve server-side authorization, evidence provenance, citation filtering, bounded results, immutable artifact bindings, and read-only adapter operations. Never expose arbitrary SQL or generic credential/network tools.
- Credentials, live model requests, remote sessions, Teams messages, cloud access, deployment, and publishing require explicit authorization naming the destination, operation, and credential/session. Do not infer it from local development permission.
- Maintain `README.md` in neutral professional Spanish. Code, identifiers, tests, technical instructions, and other artifacts default to English unless explicitly requested otherwise.

## Azure reuse baseline — verified 2026-10-12

The read-only Azure CLI ARM audit verified ten resources in `rg-libras-prod`, subscription ASEINFO Azure `75eecb3a-3825-4a53-bd91-09386a38e8a4`, tenant `abcee5bb-aa0e-4ecb-9377-71f4d0f42c2a`. Nine resources are Central US; Azure Bot is global. This dated baseline does not establish data-plane access or live provider readiness. Preserve existing hosting, identities, configuration and permissions; documentation authorization does not permit recreating resources or changing grants. The project remains a minimal hosted Agents API base.

| Existing resource | Reuse boundary |
| --- | --- |
| `app-libras-prod` | Running Linux HTTPS app; SystemAssigned plus bot UserAssigned identity |
| `app-libras-staging` | Separate Running Linux HTTPS app, not a deployment slot; own SystemAssigned identity |
| `ASP-rglibrasprod-aee7` | Shared Linux B1 Basic compute, one worker and two sites |
| `bot-libras-prod` | F0 UserAssignedMSI; enabled MsTeamsChannel targets production `/api/messages` |
| `id-libras-bot-prod` | Bot authentication UAMI attached only to production; do not assume data-reader grants |
| `id-libras-feedback-export-prod` | Exists, attached to neither app; exporter activity/schedule is unestablished |
| `kv-libras-prod` | Standard RBAC vault, empty access policies; public network Allow and 90-day soft delete |
| `srch-libras-prod` | Free, one replica/partition, Entra-or-key auth with local keys enabled; no service identity |
| `stlibrasconvprod` | StorageV2 Standard LRS, HTTPS/TLS 1.2, no public blobs, network Allow; Azure Tables persistence |
| `stlibrasdbcatalogprod01` | StorageV2 Standard LRS, HTTPS/TLS 1.2, no public blobs; private immutable catalog/SQL artifacts, not a live SQL connection |

| Identity | Principal/object ID | UAMI client ID |
| --- | --- | --- |
| Production SystemAssigned | `2fc398ef-6e81-41c3-b955-62b05d31ac7b` | Not a UAMI |
| Staging SystemAssigned | `cfd4eb89-5e9e-429a-b9db-1f9b98a92b63` | Not a UAMI |
| Bot UAMI | `30fda04b-df31-4747-b70b-5214775194e7` | `bac24639-da91-45a3-ae85-062b07188b9c` |
| Export UAMI | `17eaac8c-4ed4-4700-b5a2-507b97d8391f` | `a8558af3-cfd4-4fc0-a864-85786ac854c1` |

The following four direct, unconditional roles belong to **production SystemAssigned**, separately from bot authentication. Exact scopes concatenate `/subscriptions/75eecb3a-3825-4a53-bd91-09386a38e8a4/resourceGroups/rg-libras-prod` with the suffix below. Existing grants are facts, not permission-change instructions.

| Existing production role | Exact scope suffix |
| --- | --- |
| Search Index Data Reader | `/providers/Microsoft.Search/searchServices/srch-libras-prod` — entire service |
| Key Vault Secrets User | `/providers/Microsoft.KeyVault/vaults/kv-libras-prod` |
| Storage Table Data Contributor | `/providers/Microsoft.Storage/storageAccounts/stlibrasconvprod` — account scope, entity read/write/delete |
| Storage Blob Data Reader | `/providers/Microsoft.Storage/storageAccounts/stlibrasdbcatalogprod01/blobServices/default/containers/evolution-db-catalog` — this container only |

Both apps set `keyVaultReferenceIdentity=SystemAssigned`; do not route vault references through Bot UAMI. Bot `msaAppId` matches its UAMI client ID/resource binding. Teams targets `https://app-libras-prod-h0azhpfef6d4fyax.centralus-01.azurewebsites.net/api/messages`; staging has a separate endpoint and permission parity with production was not established.

The inspected RG/inherited role inventory had 15 assignments and no next page. No matching scoped grant was observed for staging, Bot UAMI or Export UAMI; this is not global absence or proof of effective denial. The separate SharePoint ingestion principal `f0ec8ab2-9bf6-4d82-80e0-4ddbbc2fe26e` has unconditional Search Index Data Contributor over the entire Search service. Its documented name is `libras-sharepoint-ingestion-prod`; it is not one of the ten ARM resources or the bot/runtime/CLI identity. Source documents Graph Sites.Selected plus site-specific read access, which the ARM audit did not revalidate.

Conversation persistence references Azure Tables `librasconversationmap`; configuration also names `librasfeedback`, without establishing current feedback/export activity. Catalog artifacts must preserve release/commit/publication/schema and citation bindings. Catalog shared-key access and endpoint are enabled; network default Deny has AzureServices bypass, 36 IP/CIDR rules, zero VNet/resource-access rules and no private endpoints. Production has no VNet integration. Current outbound 5/5 and possible outbound 22/22 matching rules is metadata parity only: same-region Storage routing does not prove reachability from public outbound rules. No data-plane or secret contents/usage were tested.

Five retained Incremental/Succeeded ARM deployments document Search (July 23), production/shared plan (July 25), vault (July 28), Bot (July 30), and catalog/default Blob/File services (August 26). Conversation storage creation is dated August 8; its original workflow and staging/UAMI provenance remain incomplete. Portal-like names and generic source Bicep do not prove original operator/workflow or complete provisioning. The source templates omit vault/storage/staging/export identity/role assignments.

ClickUp's fixed `mcp.clickup.com/mcp` OAuth broker and server-owned scope registry are runtime source contracts, not evidence of another Azure ARM broker. Azure grants do not grant external ClickUp/OpenAI account or SharePoint site access. See the [dated Azure map, provenance and primary-source limitations](README.md#mapa-de-azure-verificado-2026-10-12) before later separately authorized Teams/provider integration; no Azure access or permission changes are authorized by this documentation unit.

## Local verification

Run from this project root; use its isolated interpreter without activation.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m libras_agents doctor
.\.venv\Scripts\python.exe -m compileall -q src tests
git diff --check
```

The CLI is doctor-only and must never make network requests. Keep functional tests with their behavior and report untested live integrations honestly. Track substantial authorized work in `odd/tasks/`; never add AI attribution to commits, and use Conventional Commits.
