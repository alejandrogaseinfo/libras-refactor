import json
import os
import socket
import subprocess
import sys
import unittest
from unittest.mock import AsyncMock, patch

from libras_agents.runtime import (
    Dependencies,
    ProviderUnavailable,
    build_agent,
    doctor,
    run_libras,
)


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, tool, dependencies, query="policy"):
        from agents.tool_context import ToolContext

        arguments = json.dumps({"query": query})
        return await tool.on_invoke_tool(
            ToolContext(
                context=dependencies, tool_name=tool.name,
                tool_call_id="offline-test-call", tool_arguments=arguments,
            ),
            arguments,
        )

    async def test_absent_providers_raise_instead_of_fabricating_evidence(self):
        agent = build_agent(model="offline-only-test-model")
        for tool in agent.tools:
            with self.subTest(tool=tool.name):
                with self.assertRaisesRegex(ProviderUnavailable, "not configured"):
                    await self.invoke(tool, Dependencies())

    async def test_each_tool_uses_only_its_injected_provider(self):
        providers = [AsyncMock(return_value=f"evidence-{i}") for i in range(3)]
        dependencies = Dependencies(*providers)
        agent = build_agent(model="offline-only-test-model")
        for index, tool in enumerate(agent.tools):
            self.assertEqual(await self.invoke(tool, dependencies), f"evidence-{index}")
        for provider in providers:
            provider.assert_awaited_once_with("policy")

    async def test_invalid_query_never_reaches_provider(self):
        provider = AsyncMock(return_value="evidence")
        tool = build_agent(model="offline-only-test-model").tools[0]
        for query in ("   ", "q" * 2001):
            with self.subTest(query_length=len(query)):
                with self.assertRaises(ValueError):
                    await self.invoke(tool, Dependencies(documents=provider), query)
        provider.assert_not_awaited()

    async def test_provider_errors_are_not_converted_into_evidence(self):
        provider = AsyncMock(side_effect=PermissionError("access denied"))
        tool = build_agent(model="offline-only-test-model").tools[0]
        with self.assertRaisesRegex(PermissionError, "access denied"):
            await self.invoke(tool, Dependencies(documents=provider))

    async def test_missing_model_is_rejected_before_runner(self):
        with patch("agents.Runner.run", new_callable=AsyncMock) as runner:
            for model in ("", "   ", None, "offline-only-test-model"):
                with self.subTest(model=model):
                    with self.assertRaises(ValueError):
                        await run_libras("policy", Dependencies(), model=model, api_key="test-key")
            runner.assert_not_awaited()

    async def test_missing_key_is_rejected_before_runner(self):
        with patch("agents.Runner.run", new_callable=AsyncMock) as runner:
            with self.assertRaisesRegex(ValueError, "api_key"):
                await run_libras("policy", Dependencies(), model="explicit-model", api_key="")
            runner.assert_not_awaited()

    async def test_run_is_bounded_and_tracing_is_disabled(self):
        with patch("agents.Runner.run", new_callable=AsyncMock, return_value="result") as runner:
            result = await run_libras(
                "policy", Dependencies(), model="explicit-model", api_key="test-key"
            )
        self.assertEqual(result, "result")
        self.assertEqual(runner.call_args.kwargs["max_turns"], 6)
        config = runner.call_args.kwargs["run_config"]
        self.assertTrue(config.tracing_disabled)
        self.assertFalse(config.trace_include_sensitive_data)

    def test_doctor_constructs_offline_without_exposing_environment_values(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret-sentinel", "OPENAI_MODEL": "model-sentinel"}):
            with patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden")):
                report = doctor()
        encoded = json.dumps(report)
        self.assertNotIn("secret-sentinel", encoded)
        self.assertNotIn("model-sentinel", encoded)
        self.assertEqual(report["status"], "offline-construction-only")
        self.assertEqual(report["teams"], "not-wired")
        self.assertTrue(report["private_blob_filter_checked"])
        self.assertEqual(len(report["tools"]), 3)
        self.assertTrue(all(value == "unconfigured" for value in report["capabilities"].values()))

    def test_fresh_import_and_doctor_block_network_and_override_privacy_environment(self):
        script = """
import json, os, socket
def forbidden(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket.connect = forbidden
socket.create_connection = forbidden
from libras_agents.runtime import doctor
report = doctor()
assert os.environ['OPENAI_AGENTS_DISABLE_TRACING'] == '1'
assert os.environ['OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA'] == '0'
assert os.environ['OPENAI_AGENTS_DONT_LOG_MODEL_DATA'] == '1'
assert os.environ['OPENAI_AGENTS_DONT_LOG_TOOL_DATA'] == '1'
print(json.dumps(report))
"""
        environment = dict(os.environ)
        environment.pop("OPENAI_API_KEY", None)
        environment.pop("OPENAI_MODEL", None)
        environment["OPENAI_AGENTS_DISABLE_TRACING"] = "0"
        environment["OPENAI_AGENTS_DONT_LOG_MODEL_DATA"] = "0"
        completed = subprocess.run(
            [sys.executable, "-c", script], env=environment,
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "offline-construction-only")

    def test_prior_sdk_import_cannot_leak_tool_data_to_sdk_logs(self):
        script = """
import asyncio, io, json, logging, os
os.environ['OPENAI_AGENTS_DISABLE_TRACING'] = '1'
os.environ['OPENAI_AGENTS_DONT_LOG_TOOL_DATA'] = '0'
import agents
from agents.tool_context import ToolContext
output = io.StringIO()
logger = logging.getLogger('openai.agents')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(output))
from libras_agents.runtime import Dependencies, build_agent
async def provider(query):
    return 'sensitive-result-sentinel'
async def check():
    tool = build_agent(model='offline-only-test-model').tools[0]
    arguments = json.dumps({'query': 'sensitive-query-sentinel'})
    context = ToolContext(context=Dependencies(documents=provider), tool_name=tool.name,
        tool_call_id='offline-test', tool_arguments=arguments)
    await tool.on_invoke_tool(context, arguments)
asyncio.run(check())
assert 'sensitive-query-sentinel' not in output.getvalue()
assert 'sensitive-result-sentinel' not in output.getvalue()
"""
        subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)


if __name__ == "__main__":
    unittest.main()
