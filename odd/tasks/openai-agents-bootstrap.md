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

## Delivery and routing
Delivery strategy: ask-on-risk; no push, PR or merge in this task. Forecast: approximately 340 authored additions, excluding dependency/environment artifacts. Initial reviewed boundary: bootstrap planning commit, to be recorded after creation.

Route: delegated direct. Trigger evidence: unfamiliar legacy mapping and multiple non-trivial implementation files. One read-only explorer mapped source boundaries; one writer prepares the base. No parallel writes.

## Tasks
- [ ] T1 — Install an isolated environment, create lazy SDK/tool wiring, reuse the citation utility, document Azure/legacy mappings, and verify offline behavior.

Acceptance: a clean environment resolves pinned dependencies; the doctor command constructs three tool schemas without credentials or remote activity; absent providers and missing model configuration fail clearly; Blob citation classification is checked; all new-project tests pass; original source remains untouched.

## Verification
Applicable test-first runner: .venv\Scripts\python.exe -m unittest discover -s tests -v. Observe meaningful RED before runtime/evidence implementation, then GREEN. Documentation and packaging get structural checks, not invented RED evidence.

Required checks: unittest discovery, pip check, python -m libras_agents doctor, compileall for src/tests, git diff --check. Do not execute Runner.run against a real service. Writer self-verification and one parent offline doctor spot check are required; independent verification follows native assessed risk.

## Progress and evidence
- Exploration complete: Python 3.11.6 available; source Teams host and business-tool boundaries mapped.
- SDK metadata verified: openai-agents 0.23.1, Python >=3.10; Microsoft Agents aiohttp 1.8.0 supports Python >=3.10.
- Public GitHub reference returned 404; authenticated access was not used.
- RDD status: on by default. Native risk assessment and transitions pending implementation.
- Engram mirror pending: mem_save and mem_review blocked because host session resolution could not be confirmed. No session identity was invented.
- Commit identity, observed checks, authored count, and native assessment outcome: pending.

## Next step
Complete T1 locally, then migrate bounded providers and the authenticated Teams adapter in separate authorized work units.
