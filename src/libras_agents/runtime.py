"""Hosted Agents API gateway; OpenAI orchestrates, local callbacks only read evidence."""

import asyncio
import math
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from importlib.metadata import version

from .evidence import is_private_blob_url

ReadProvider = Callable[[str], Awaitable[str]]
_TOOLS = {
    "search_documents": ("documents", "Read authorized documentary evidence with source citations."),
    "search_database_catalog": ("database_catalog", "Read authorized catalog evidence; never execute arbitrary SQL."),
    "search_clickup": ("clickup", "Read authorized ClickUp evidence with source identifiers."),
}


@dataclass(frozen=True)
class Dependencies:
    """Providers enforce authorization, provenance, bounded results, and read-only access."""

    documents: ReadProvider | None = None
    database_catalog: ReadProvider | None = None
    clickup: ReadProvider | None = None


class ProviderUnavailable(RuntimeError):
    """A source was not configured; no evidence was retrieved."""


class CallbackLimitExceeded(RuntimeError):
    """The local dispatch budget was exhausted, without confirming remote cancellation."""


class SessionObservationTimeout(TimeoutError):
    """The local observation ended; the hosted turn may still be running."""


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"An explicit nonempty {name} is required.")
    return value.strip()


def function_definitions() -> list[dict]:
    """Return the complete hosted allowlist, replacing any saved agent tool list."""
    return [{
        "type": "function", "name": name, "description": description,
        "parameters": {
            "type": "object", "properties": {"query": {"type": "string", "minLength": 1, "maxLength": 2000}},
            "required": ["query"], "additionalProperties": False,
        },
    } for name, (_, description) in _TOOLS.items()]


def build_request_manifest(user_text: str, *, agent_id: str, model: str | None = None) -> dict:
    """Build an offline request description; the saved agent supplies its model by default."""
    agent = {"tools": function_definitions()}
    if model is not None:
        agent["model"] = _required_text(model, "model override")
    return {
        "agent_id": _required_text(agent_id, "existing agent_id"),
        "agent": agent, "environment": {"type": "none"},
        "input": _required_text(user_text, "user input"), "stream": True,
    }


def _timeout_bound(value: float, ceiling: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 < value <= ceiling:
        raise ValueError(f"{name} must be positive and at most {ceiling} seconds.")
    return value


class Callbacks:
    """Dispatch only explicit live SDK requests; never infer replay from stored history."""

    def __init__(self, dependencies: Dependencies, *, max_dispatches: int = 6, callback_timeout: float = 30):
        if isinstance(max_dispatches, bool) or not isinstance(max_dispatches, int) or not 1 <= max_dispatches <= 6:
            raise ValueError("max_dispatches must be an integer from 1 to 6.")
        self.dependencies = dependencies
        self.max_dispatches = max_dispatches
        self.callback_timeout = _timeout_bound(callback_timeout, 30, "callback_timeout")
        self.dispatches = 0
        self.first_error: Exception | None = None

    async def dispatch(self, name: str, arguments: dict[str, object]) -> str:
        try:
            if name not in _TOOLS:
                raise PermissionError("Function is outside the approved callback allowlist.")
            if not isinstance(arguments, dict) or set(arguments) != {"query"}:
                raise ValueError("Callback arguments must contain only query.")
            query = _required_text(arguments["query"], "search query")
            if len(arguments["query"]) > 2000:
                raise ValueError("Search query must contain at most 2000 characters.")
            if self.dispatches >= self.max_dispatches:
                raise CallbackLimitExceeded("Local callback budget exhausted; remote cancellation is unconfirmed.")
            self.dispatches += 1
            provider_name = _TOOLS[name][0]
            provider = getattr(self.dependencies, provider_name)
            if provider is None:
                raise ProviderUnavailable(f"{provider_name} provider is not configured; no evidence retrieved.")
            result = await asyncio.wait_for(provider(query), timeout=self.callback_timeout)
            if not isinstance(result, str) or len(result.encode("utf-8")) > 256_000:
                raise ValueError("Provider evidence must be text bounded to 256000 UTF-8 bytes.")
            return result
        except Exception as error:
            if self.first_error is None:
                self.first_error = error
            raise

    @property
    def handlers(self) -> dict[str, Callable]:
        def bind(name):
            async def handler(arguments):
                return await self.dispatch(name, arguments)
            return handler
        return {name: bind(name) for name in _TOOLS}

    def raise_failure(self) -> None:
        # The SDK sends a generic failed result and may still collect a completed turn.
        if self.first_error is not None:
            raise self.first_error


async def run_session(user_text: str, dependencies: Dependencies, *, agent_id: str,
                      api_key: str, model: str | None = None, wait_timeout: float = 120):
    """Start one authorized hosted session; local timeout does not cancel remote work."""
    manifest = build_request_manifest(user_text, agent_id=agent_id, model=model)
    api_key = _required_text(api_key, "api_key")
    wait_timeout = _timeout_bound(wait_timeout, 120, "wait_timeout")
    callbacks = Callbacks(dependencies)
    from openai import AsyncOpenAI

    async with AsyncOpenAI(api_key=api_key, base_url="https://api.openai.com/v1",
                           timeout=30.0, max_retries=0) as client:
        async def observe():
            stream = await client.beta.agents.sessions.create(**manifest, tool_handlers=callbacks.handlers)
            async with stream:
                return await stream.get_final_result()
        try:
            result = await asyncio.wait_for(observe(), timeout=wait_timeout)
        except TimeoutError as error:
            callbacks.raise_failure()
            raise SessionObservationTimeout("Local observation timed out; remote cancellation is unconfirmed.") from error
        except Exception:
            callbacks.raise_failure()
            raise
        callbacks.raise_failure()
        return result


def doctor() -> dict:
    """Report hosted definitions and environment presence without credentials or requests."""
    environment_names = (
        "OPENAI_API_KEY", "OPENAI_AGENT_ID", "OPENAI_MODEL", "MICROSOFT_APP_ID", "MICROSOFT_APP_PASSWORD",
        "MICROSOFT_APP_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID",
        "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_KEY", "AZURE_SEARCH_INDEX",
        "AZURE_STORAGE_CONNECTION_STRING", "CLICKUP_API_TOKEN",
    )
    return {
        "product": "OpenAI Agents API", "client_version": version("openai"),
        "status": "offline-manifest-only", "teams": "not-wired",
        "capabilities": {provider: "unconfigured" for provider, _ in _TOOLS.values()},
        "tools": function_definitions(),
        "environment_presence": {name: bool(os.environ.get(name)) for name in environment_names},
        "private_blob_filter_checked": (
            is_private_blob_url("https://offline.blob.core.windows.net/evidence/file")
            and not is_private_blob_url("https://example.org/evidence")
        ),
        "account_access_verified": False, "live_configuration_verified": False,
    }
