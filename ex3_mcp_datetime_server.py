"""
Exercise 3 - serwer MCP (Model Context Protocol) udostepniajacy dwa narzedzia:
  - get_current_date: zwraca dzisiejsza date (YYYY-MM-DD)
  - get_current_datetime: zwraca dzisiejsza date i czas (YYYY-MM-DDTHH:MM:SS)

Dziala w trybie "streamable HTTP" na porcie 8002, zgodnie z tresci zadania.

URUCHOM W OSOBNYM TERMINALU (i zostaw dzialajacy w tle):
    uv run python ex3_mcp_datetime_server.py

Powinienes zobaczyc komunikat, ze serwer wystartowal na porcie 8002.
Zostaw to okno otwarte, dopoki nie uruchomisz ex3_mcp_client.py w DRUGIM oknie.
"""

import datetime

from fastmcp import FastMCP

mcp = FastMCP("Date and time server")


@mcp.tool(description='Get current date in the format "Year-Month-Day" (YYYY-MM-DD).')
def get_current_date() -> str:
    return datetime.date.today().isoformat()


@mcp.tool(
    description=(
        "Get current date and time in ISO 8601 format, up to seconds, "
        "i.e. YYYY-MM-DDTHH:MM:SS."
    )
)
def get_current_datetime() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8002)
