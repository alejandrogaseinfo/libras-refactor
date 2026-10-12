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
