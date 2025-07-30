from server import mcp
from utils.trans_func import uni_translate



@mcp.tool()
def translate_text(text: str, language: str) ->str:
    return uni_translate(text, language)