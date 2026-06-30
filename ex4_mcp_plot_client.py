"""
Exercise 4 - prosty klient testujacy serwer z wykresami (ex4_mcp_plot_server.py).
Nie pytamy tu LLM - laczymy sie z serwerem MCP bezposrednio, wywolujemy narzedzie
"line_plot" z przykladowymi danymi i zapisujemy wynikowy obrazek na dysk,
zeby moc zrobic z niego zrzut ekranu / dolaczyc do raportu.

WAZNE: najpierw uruchom w OSOBNYM terminalu:
    uv run python ex4_mcp_plot_server.py
Dopiero potem w DRUGIM terminalu:
    uv run python ex4_mcp_plot_client.py
"""

import asyncio
import base64
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main() -> None:
    url = "http://localhost:8003/mcp"

    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            sample_data = {
                "Sprzedaz 2024": [10, 15, 13, 18, 22, 25, 30],
                "Sprzedaz 2025": [12, 14, 19, 21, 28, 33, 35],
            }

            result = await session.call_tool(
                "line_plot",
                arguments={
                    "data": sample_data,
                    "title": "Przykladowa sprzedaz miesieczna",
                    "x_label": "Miesiac",
                    "y_label": "Sprzedaz (tys. PLN)",
                    "legend": True,
                },
            )

            payload = json.loads(result.content[0].text)
            image_bytes = base64.b64decode(payload["image_base64"])

            output_path = "ex4_wykres_wynikowy.png"
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            print(f"Wykres zapisany do pliku: {output_path}")
            print("Otworz ten plik, zeby zobaczyc wygenerowany wykres.")


if __name__ == "__main__":
    asyncio.run(main())
