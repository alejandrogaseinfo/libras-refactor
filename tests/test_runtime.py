import asyncio
import json
import os
import socket
import subprocess
import sys
import unittest
from unittest.mock import AsyncMock, patch

import httpx2
from openai import AsyncOpenAI as RealAsyncOpenAI
from openai.lib.beta.agents import AgentTurnResultError

from libras_agents import runtime


def session_events(*, tool_name=None, outcome="completed", idle_only=False):
    """Minimal ordered public Agents API events, served only by MockTransport."""
    turn = {
        "id": "turn_test", "session_id": "session_test", "agent_id": "agent_existing",
        "object": "agent.session.turn", "created_at": 1, "status": "in_progress",
        "subagent_id": None,
    }
    session = {"id": "session_test", "required_actions": [], "status": "in_progress"}
    events = [
        {"type": "agent.session.created", "session": session},
        {"type": "agent.session.turn.created", "session_id": "session_test",
         "turn_id": "turn_test", "turn": turn},
    ]
    if tool_name:
        call = {
            "id": "item_call", "type": "function_call", "turn_id": "turn_test",
            "call_id": "call_test", "name": tool_name, "arguments": {"query": "policy"},
            "status": "in_progress",
        }
        events.extend([
            {"type": "agent.session.turn.item.added", "session_id": "session_test",
             "turn_id": "turn_test", "output_index": 0, "item": call},
            {"type": "agent.session.requires_action", "session": {
                **session, "required_actions": [{"type": "function_call", "turn_id": "turn_test",
                    "call_id": "call_test", "name": tool_name, "arguments": {"query": "policy"}}],
            }},
            {"type": "agent.session.in_progress", "session": session},
        ])
    if not idle_only:
        if outcome == "completed":
            events.append({
                "type": "agent.session.turn.item.done", "session_id": "session_test",
                "turn_id": "turn_test", "output_index": 1, "item": {
                    "id": "message_test", "type": "message", "turn_id": "turn_test",
                    "role": "assistant", "status": "completed", "phase": "final_answer",
                    "content": [{"type": "output_text", "text": "grounded answer", "annotations": []}],
                },
            })
        events.append({
            "type": f"agent.session.turn.{outcome}", "session_id": "session_test",
            "turn_id": "turn_test", "turn": {**turn, "status": outcome},
        })
    events.append({"type": "agent.session.idle", "session": {**session, "status": "idle"}})
    for index, event in enumerate(events):
        event["event_id"] = f"event_{index}"
    return "".join(f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events)


class AgentsApiTests(unittest.IsolatedAsyncioTestCase):
    async def gateway(self, dependencies=None, *, tool_name=None, outcome="completed", idle_only=False, model=None):
        requests = []

        def transport(request):
            requests.append(request)
            if request.url.path == "/v1/agents/sessions":
                return httpx2.Response(200, headers={"content-type": "text/event-stream"},
                    stream=httpx2.ByteStream(session_events(
                        tool_name=tool_name, outcome=outcome, idle_only=idle_only).encode()))
            if request.url.path == "/v1/agents/sessions/session_test/events":
                return httpx2.Response(200, json={})
            raise AssertionError(f"Unexpected mock path: {request.url.path}")

        def client_factory(**kwargs):
            return RealAsyncOpenAI(http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)), **kwargs)

        with patch("openai.AsyncOpenAI", side_effect=client_factory):
            result = await runtime.run_session(
                "question", dependencies or runtime.Dependencies(),
                agent_id="agent_existing", api_key="offline-test-key", model=model,
            )
        return result, requests

    def test_manifest_uses_saved_agent_model_and_replaces_complete_tool_list(self):
        manifest = runtime.build_request_manifest("question", agent_id="agent_existing")
        self.assertNotIn("model", manifest["agent"])
        self.assertEqual(manifest["environment"], {"type": "none"})
        self.assertTrue(manifest["stream"])
        self.assertEqual(manifest["agent_id"], "agent_existing")
        self.assertEqual({tool["name"] for tool in manifest["agent"]["tools"]},
            {"search_documents", "search_database_catalog", "search_clickup"})

    def test_explicit_model_override_is_optional_but_cannot_be_blank(self):
        manifest = runtime.build_request_manifest("question", agent_id="agent_existing", model="explicit-model")
        self.assertEqual(manifest["agent"]["model"], "explicit-model")
        with self.assertRaises(ValueError):
            runtime.build_request_manifest("question", agent_id="agent_existing", model=" ")

    async def test_invalid_credentials_agent_and_input_fail_before_client_creation(self):
        with patch("openai.AsyncOpenAI") as client:
            for values in (
                {"api_key": ""}, {"agent_id": " "}, {"user_text": " "}, {"model": " "},
            ):
                arguments = {"user_text": "question", "agent_id": "agent_existing", "api_key": "test-key", **values}
                with self.subTest(values=values), self.assertRaises(ValueError):
                    await runtime.run_session(dependencies=runtime.Dependencies(), **arguments)
            client.assert_not_called()

    async def test_real_client_uses_agents_beta_endpoint_headers_and_saved_model(self):
        result, requests = await self.gateway()
        self.assertEqual(result.output_text, "grounded answer")
        self.assertEqual(result.session_id, "session_test")
        request = requests[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(str(request.url), "https://api.openai.com/v1/agents/sessions")
        self.assertEqual(request.headers["OpenAI-Beta"], "agents=v1")
        self.assertEqual(request.headers["Authorization"], "Bearer offline-test-key")
        body = json.loads(request.content)
        self.assertNotIn("model", body["agent"])
        self.assertEqual(len(body["agent"]["tools"]), 3)
        self.assertEqual(body["input"], "question")

    async def test_real_client_automatically_returns_callback_result_with_call_binding(self):
        provider = AsyncMock(return_value="document evidence")
        result, requests = await self.gateway(runtime.Dependencies(documents=provider), tool_name="search_documents")
        provider.assert_awaited_once_with("policy")
        self.assertEqual(result.turn.status, "completed")
        event = json.loads(requests[1].content)["events"][0]
        self.assertEqual(event, {"type": "agent.session.input.tool_result", "turn_id": "turn_test",
            "call_id": "call_test", "success": True, "output": "document evidence"})
        self.assertTrue(requests[1].headers["Idempotency-Key"])

    async def test_sdk_callback_failure_preserves_local_exception(self):
        for provider, exception in ((None, runtime.ProviderUnavailable),
                (AsyncMock(side_effect=PermissionError("access denied")), PermissionError)):
            with self.subTest(exception=exception), self.assertRaises(exception):
                await self.gateway(runtime.Dependencies(documents=provider), tool_name="search_documents")

    async def test_unknown_hosted_function_cannot_dispatch(self):
        provider = AsyncMock(return_value="evidence")
        with self.assertRaises(AgentTurnResultError) as raised:
            await self.gateway(runtime.Dependencies(documents=provider), tool_name="execute_sql")
        self.assertEqual(raised.exception.reason, "requires_action")
        provider.assert_not_awaited()

    async def test_failure_cancellation_and_plain_idle_are_not_success(self):
        for outcome in ("failed", "cancelled"):
            with self.subTest(outcome=outcome), self.assertRaises(AgentTurnResultError) as raised:
                await self.gateway(outcome=outcome)
            self.assertEqual(raised.exception.reason, outcome)
        with self.assertRaises(AgentTurnResultError) as raised:
            await self.gateway(idle_only=True)
        self.assertEqual(raised.exception.reason, "incomplete")

    async def test_callback_allowlist_queries_and_dispatch_count_are_bounded(self):
        provider = AsyncMock(return_value="evidence")
        callbacks = runtime.Callbacks(runtime.Dependencies(documents=provider), max_dispatches=1)
        for name, arguments in (("execute_sql", {"query": "policy"}),
                ("search_documents", {"query": " "}), ("search_documents", {"query": "q" * 2001}),
                ("search_documents", {"query": "policy", "api_key": "not-allowed"})):
            with self.subTest(name=name, arguments=arguments), self.assertRaises((ValueError, PermissionError)):
                await callbacks.dispatch(name, arguments)
        provider.assert_not_awaited()
        self.assertEqual(await callbacks.dispatch("search_documents", {"query": "policy"}), "evidence")
        with self.assertRaises(runtime.CallbackLimitExceeded):
            await callbacks.dispatch("search_documents", {"query": "again"})
        provider.assert_awaited_once_with("policy")

    async def test_callback_timeout_is_not_fabricated_evidence(self):
        async def slow_provider(query):
            await asyncio.sleep(1)
            return "evidence"
        callbacks = runtime.Callbacks(runtime.Dependencies(documents=slow_provider), callback_timeout=0.001)
        with self.assertRaises(TimeoutError):
            await callbacks.dispatch("search_documents", {"query": "policy"})

    async def test_local_wait_timeout_closes_stream_without_claiming_remote_cancel(self):
        requests = []

        class SlowStream(httpx2.AsyncByteStream):
            closed = False

            async def __aiter__(self):
                await asyncio.sleep(1)
                yield session_events().encode()

            async def aclose(self):
                self.closed = True

        stream = SlowStream()

        def transport(request):
            requests.append(request)
            return httpx2.Response(200, headers={"content-type": "text/event-stream"}, stream=stream)

        def client_factory(**kwargs):
            return RealAsyncOpenAI(http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(transport)), **kwargs)

        with patch("openai.AsyncOpenAI", side_effect=client_factory):
            with self.assertRaisesRegex(runtime.SessionObservationTimeout, "cancellation is unconfirmed"):
                await runtime.run_session("question", runtime.Dependencies(), agent_id="agent_existing",
                    api_key="offline-test-key", wait_timeout=0.2)
        self.assertTrue(stream.closed)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].url.path, "/v1/agents/sessions")

    def test_doctor_reports_api_product_without_environment_values_or_network(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret-sentinel", "OPENAI_AGENT_ID": "agent-sentinel"}):
            with patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden")):
                report = runtime.doctor()
        self.assertEqual(report["product"], "OpenAI Agents API")
        self.assertEqual(report["status"], "offline-manifest-only")
        self.assertNotIn("secret-sentinel", json.dumps(report))
        self.assertNotIn("agent-sentinel", json.dumps(report))
        self.assertEqual(report["teams"], "not-wired")
        self.assertFalse(report["account_access_verified"])
        self.assertTrue(report["private_blob_filter_checked"])

    def test_fresh_import_and_doctor_never_import_agents_sdk_or_connect(self):
        script = """
import json, socket, sys
def forbidden(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket.connect = forbidden
socket.create_connection = forbidden
from libras_agents.runtime import doctor
report = doctor()
assert 'agents' not in sys.modules
print(json.dumps(report))
"""
        environment = dict(os.environ)
        for name in ("OPENAI_API_KEY", "OPENAI_AGENT_ID", "OPENAI_MODEL"):
            environment.pop(name, None)
        completed = subprocess.run([sys.executable, "-c", script], env=environment,
            capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["product"], "OpenAI Agents API")


if __name__ == "__main__":
    unittest.main()
