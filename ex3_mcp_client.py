"""
Exercise 3 - klient laczacy sie z serwerem MCP (ex3_mcp_datetime_server.py)
i przekazujacy jego narzedzia do LLM (OpenAI API).

WAZNE: najpierw uruchom w OSOBNYM terminalu:
    uv run python ex3_mcp_datetime_server.py
i zostaw go dzialajacego. Dopiero potem w DRUGIM terminalu uruchom ten plik:
    uv run python ex3_mcp_client.py

Uzywa lokalnej Ollamy (model qwen3:1.7b) zamiast OpenAI/vLLM - patrz README.md.
"""

import asyncio
import json
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import OpenAI

MODEL_NAME = "qwen3:1.7b"


class MCPManager:
    def __init__(self, servers: dict[str, str]):
        self.servers = servers
        self.clients = {}
        self.tools = []  # w formacie OpenAI
        self._stack = AsyncExitStack()

    async def __aenter__(self):
        for url in self.servers.values():
            read, write, _ = await self._stack.enter_async_context(
                streamablehttp_client(url)
            )
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            tools_resp = await session.list_tools()
            for t in tools_resp.tools:
                self.clients[t.name] = session
                self.tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.inputSchema,
                        },
                    }
                )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._stack.aclose()

    async def call_tool(self, name: str, args: dict) -> str:
        result = await self.clients[name].call_tool(name, arguments=args)
        return result.content[0].text


async def make_llm_request(prompt: str) -> str:
    mcp_servers = {"date_time_server": "http://localhost:8002/mcp"}

    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")

    async with MCPManager(mcp_servers) as mcp:
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use tools if you need to know the date or time."},
            {"role": "user", "content": prompt},
        ]

        for _ in range(10):
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=mcp.tools,
                tool_choice="auto",
                max_completion_tokens=1000,
            )
            resp_message = response.choices[0].message
            if not resp_message.tool_calls:
                return resp_message.content

            messages.append(resp_message.model_dump())
            for tool_call in resp_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"Wywoluje narzedzie '{func_name}' z argumentami {func_args}")
                func_result = await mcp.call_tool(func_name, func_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(func_result),
                    }
                )

        return "Nie udalo sie rozwiazac zadania (limit petli)."


if __name__ == "__main__":
    prompt = "What is today's date?"
    print("Pytanie:", prompt)
    print("Odpowiedz:", asyncio.run(make_llm_request(prompt)))
    print()

    prompt = "What is the exact current time, down to the second?"
    print("Pytanie:", prompt)
    print("Odpowiedz:", asyncio.run(make_llm_request(prompt)))
