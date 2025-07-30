
from .server import mcp
from .tools import csv_tools


def main() -> None:
    mcp.run(transport="stdio")
