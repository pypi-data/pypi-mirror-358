
from server import mcp
import tools.csv_tools


def main() -> None:
    mcp.run(transport="stdio")
