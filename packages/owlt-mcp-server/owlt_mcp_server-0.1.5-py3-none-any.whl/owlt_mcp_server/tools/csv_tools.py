from owlt_mcp_server.server import mcp
from owlt_mcp_server.utils.trans_func import uni_translate



@mcp.tool()
def translate_text(text: str, language: str) ->str:
    return uni_translate(text, language)