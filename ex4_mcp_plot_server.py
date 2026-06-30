"""
Exercise 4 - serwer MCP z narzedziem "line_plot", ktory tworzy wykres liniowy
z podanych danych (Matplotlib) i zwraca go jako obrazek zakodowany w base64.

URUCHOM W OSOBNYM TERMINALU (i zostaw dzialajacy w tle):
    uv run python ex4_mcp_plot_server.py

Serwer wystartuje na porcie 8003.
"""

import base64
import io
from typing import Annotated

import matplotlib

matplotlib.use("Agg")  # backend bez okienek - potrzebne, bo dzialamy jako serwer
import matplotlib.pyplot as plt
from fastmcp import FastMCP

mcp = FastMCP("Visualization server")


@mcp.tool(description="Create a line plot from one or more lists of numbers and return it as a base64-encoded PNG image.")
def line_plot(
    data: Annotated[dict[str, list[float]], "Dictionary mapping series name -> list of numbers to plot."],
    title: Annotated[str, "Plot title."] = "",
    x_label: Annotated[str, "Label for the X axis."] = "",
    y_label: Annotated[str, "Label for the Y axis."] = "",
    legend: Annotated[bool, "Whether to show the legend."] = True,
) -> dict:
    fig, ax = plt.subplots()

    for series_name, values in data.items():
        ax.plot(values, label=series_name)

    if title:
        ax.set_title(title)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if legend:
        ax.legend()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return {"image_base64": image_base64, "format": "png"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8003)
