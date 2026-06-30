"""
Exercise 2 - narzedzia (tools), ktore pozwalaja LLM czytac pliki CSV i Parquet
z internetu (po URL), uzywajac biblioteki Polars.

Uzywamy Ollamy (lokalny model Qwen3) zamiast lokalnego vLLM (patrz README.md -
powod zmiany). Kod jest niemal identyczny jak w instrukcji laboratorium - to
glowna zaleta podejscia z OpenAI-compatible API, ktore Ollama tez udostepnia.

URUCHOM: uv run python ex2_csv_parquet_tools.py
Wymaga uruchomionej Ollamy z pobranym modelem qwen3:1.7b (patrz README.md krok 2).
"""

import json
from typing import Callable

import polars as pl
from openai import OpenAI

MODEL_NAME = "qwen3:1.7b"

# publiczny przykladowy CSV (dataset pestycydow szkodliwych dla pszczol)
CSV_URL = (
    "https://raw.githubusercontent.com/j-adamczyk/ApisTox_dataset"
    "/master/outputs/dataset_final.csv"
)


def read_remote_csv(url: str, n_rows: int = 10) -> str:
    """Czyta plik CSV spod danego URL i zwraca jego poczatek jako tekst."""
    df = pl.read_csv(url)
    preview = df.head(n_rows)
    return (
        f"Kolumny: {df.columns}\n"
        f"Liczba wierszy: {df.height}\n"
        f"Pierwsze {n_rows} wierszy:\n{preview}"
    )


def read_remote_parquet(url: str, n_rows: int = 10) -> str:
    """Czyta plik Parquet spod danego URL i zwraca jego poczatek jako tekst."""
    df = pl.read_parquet(url)
    preview = df.head(n_rows)
    return (
        f"Kolumny: {df.columns}\n"
        f"Liczba wierszy: {df.height}\n"
        f"Pierwsze {n_rows} wierszy:\n{preview}"
    )


def get_tool_definitions() -> tuple[list[dict], dict[str, Callable]]:
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "read_remote_csv",
                "description": "Reads a CSV file from a given URL and returns a preview of its contents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to the CSV file."},
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_remote_parquet",
                "description": "Reads a Parquet file from a given URL and returns a preview of its contents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to the Parquet file."},
                    },
                    "required": ["url"],
                },
            },
        },
    ]
    tool_name_to_func = {
        "read_remote_csv": read_remote_csv,
        "read_remote_parquet": read_remote_parquet,
    }
    return tool_definitions, tool_name_to_func


def make_llm_request(prompt: str) -> str:
    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")

    messages = [
        {"role": "system", "content": "You are a helpful data analyst assistant. Use tools if you need data."},
        {"role": "user", "content": prompt},
    ]

    tool_definitions, tool_name_to_func = get_tool_definitions()

    for _ in range(10):
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto",
            max_completion_tokens=1000,
        )
        resp_message = response.choices[0].message
        messages.append(resp_message.model_dump())

        print(f"Wygenerowana wiadomosc: {resp_message.model_dump()}")
        print()

        if resp_message.tool_calls:
            for tool_call in resp_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                func = tool_name_to_func[func_name]
                func_result = func(**func_args)

                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(func_result),
                        "tool_call_id": tool_call.id,
                    }
                )
        else:
            return resp_message.content

    return "Nie udalo sie rozwiazac zadania (limit petli)."


if __name__ == "__main__":
    print(f"=== Pytanie 1: ile wierszy ma dataset pod {CSV_URL} ===")
    response = make_llm_request(
        f"How many rows does the CSV dataset at {CSV_URL} have, and what columns does it contain?"
    )
    print("Odpowiedz:\n", response)
    print()

    print("=== Pytanie 2: co znajduje sie w datasecie ===")
    response = make_llm_request(
        f"Look at the CSV file at {CSV_URL} and tell me what kind of data it contains, in simple terms."
    )
    print("Odpowiedz:\n", response)
