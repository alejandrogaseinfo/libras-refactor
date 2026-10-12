# Libras OpenAI Agents bootstrap

## Objective
Prepare an isolated, runnable Python 3.11 development base for migrating Libras orchestration from Terra to OpenAI Agents SDK while retaining Teams and existing Azure services.

## Problem and scope
The reference checkout is C:\cw\Libras, inside the C:\cw monorepo at 2591bdc5e272b26453c6ac30b0c987530c0d5e69. Its dirty working tree and bundled dependencies must remain untouched. The parent workspace contains extracted dependencies, so the new project lives in libras-agents/ with its own Git repository and virtual environment.

Authorized: local files, dependency installation, deterministic tests, offline SDK construction, and feature-branch work-unit commits. Azure configuration, deployment, Teams messages, ClickUp requests, model requests, and credential reuse require a later explicitly scoped authorization.

## Design
- Use locally hosted OpenAI Agents SDK behind injected documentary, database-catalog and ClickUp read-provider contracts.
- Keep model selection explicit and provider integrations disabled until supplied; never load legacy application globals or .env files automatically.
- Reuse the pure private-Blob citation detector with source attribution.
- Document Teams authentication and bounded evidence/authorization contracts for later migration.
- Disable tracing in the runtime and redact SDK model/tool logging.
- Keep README in neutral professional Spanish; provide English project context in agent.md and the canonical AGENTS.md pointer.

## Delivery and routing
Delivery strategy: single-pr; no push, PR or merge in this task. Forecast revised to approximately 550 authored additions, excluding the generated dependency lock/environment. The isolated bootstrap, contract tests, source/resource mapping, and requested project context form one coherent local preparation unit; retaining useful checks and documentation explains the increase from 340. Future migration units can be sliced separately. Initial reviewed boundary: planning commit b18f37d860881fca3551cf7cf6734ff2fc175454.

Route: delegated direct. Trigger evidence: unfamiliar legacy mapping and multiple non-trivial implementation files. One read-only explorer mapped source boundaries; one writer prepares the base. No parallel writes.

## Tasks
- [x] T1 — Install an isolated environment, create lazy SDK/tool wiring, reuse the citation utility, document Azure/legacy mappings, add project agent instructions and a Spanish README, and verify offline behavior. Implementation, writer checks and parent readback complete; local commit and native review evidence follow below.

Acceptance: a clean environment resolves pinned dependencies; the doctor command constructs three tool schemas without credentials or remote activity; absent providers and missing model configuration fail clearly; Blob citation classification is checked; all new-project tests pass; original source remains untouched; README is neutral professional Spanish and AGENTS.md directs future agents to agent.md.

## Verification
Applicable test-first runner: .venv\Scripts\python.exe -m unittest discover -s tests -v. Observe meaningful RED before runtime/evidence implementation, then GREEN. Documentation and packaging get structural checks, not invented RED evidence.

Required checks: unittest discovery, pip check, python -m libras_agents doctor, compileall for src/tests, git diff --check. Do not execute Runner.run against a real service. Writer self-verification and one parent offline doctor spot check are required; independent verification follows native assessed risk.

## Progress and evidence
- Exploration complete: Python 3.11.6 available; source Teams host and business-tool boundaries mapped.
- SDK metadata verified: openai-agents 0.23.1, Python >=3.10; Microsoft Agents aiohttp 1.8.0 supports Python >=3.10.
- Public GitHub reference returned 404; authenticated access was not used.
- RDD status: on by default. Staged candidate assessed medium because of .env.example; review is due because the slice budget was reached. Native consent/review remains pending and is separate from the completed local functional checks.
- Engram mirror pending: mem_save and mem_review blocked because host session resolution could not be confirmed. No session identity was invented.
- T1 environment: Python 3.11.6 isolated in .venv; editable installation completed without legacy PYTHONPATH/packages. Resolved openai-agents 0.23.1, openai 3.29.0, Microsoft hosting/MSAL 1.8.0, Azure Search 12.0.0, Identity 1.26.0, Key Vault Secrets 4.11.3, and Blob Storage 12.31.0. requirements.lock holds 63 exact pins, including pip/setuptools, with no editable absolute source path. The documented --no-deps --no-build-isolation editable install passed.
- RED observed: tests were written before runtime/evidence. Discovery exited 1 with two missing-module import errors after dependency installation; this was import-only RED, not a claimed behavioral assertion failure. First implemented run additionally exposed seven direct-tool test harness errors: SDK 0.23.1 expects agents.tool_context.ToolContext. The harness now supplies its required tool identity/arguments.
- GREEN observed: .venv\Scripts\python.exe -m unittest discover -s tests -v exited 0; 13 tests passed. Checks cover SDK-wrapped absent-provider failures, injected delegation, invalid queries, provider authorization errors, model/key refusal before Runner, six-turn bounds, privacy, network-blocked fresh import/doctor, prior SDK import logging, and Blob citation policy.
- Privacy finding: the pinned SDK caches sensitive-logging flags at import. The runtime also disables its standard openai.agents logger before construction/run, preserving privacy when another caller imported SDK first. No tool/model request was sent during checks.
- Required checks observed exit 0: pip check (no broken requirements), python -m libras_agents doctor (three schemas; offline-construction-only; sources unconfigured; Teams not-wired), compileall -q src tests, and git diff --check. Microsoft hosting/MSAL and Azure client modules imported successfully with network connections blocked. BOM, final-newline and trailing-whitespace checks also passed for all authored files.
- Accepted user steering: added agent.md plus AGENTS.md pointer; translated README fully to neutral professional Spanish while preserving commands, identifiers, resource names and links. Other technical artifacts remain English.
- Uncommitted authored scaffold count: 525 additions across code, tests, configuration and project documentation; generated requirements.lock is 65 lines. Task-document changes are additional. The 400-line estimate remains advisory; useful tests/docs were retained. Commit identity and native assessment outcome remain pending parent action.
- Untested by design: live Teams authentication/delivery, Azure and ClickUp provider behavior, retrieval quality, model behavior, and deployment. Source C:\cw\Libras was read only; no source file was changed by this worker.
- Parent structural readback and offline doctor spot check passed. Staged git diff --check passed. Initial untracked-candidate assessment was unassessable; explicit staging resolved that inventory condition, after which native assessment reported medium (606 changed lines including generated lock).
- Planning baseline: b18f37d860881fca3551cf7cf6734ff2fc175454. Rollback boundary: this isolated project's bootstrap files and environment; the legacy repository and Azure resources are unaffected.

## Next step
Record the local work-unit commit and native review outcome, then migrate bounded providers and the authenticated Teams adapter in separate authorized work units.
