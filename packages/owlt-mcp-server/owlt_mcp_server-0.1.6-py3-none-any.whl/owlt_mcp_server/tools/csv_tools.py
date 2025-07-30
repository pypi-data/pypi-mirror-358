from owlt_mcp_server.server import mcp
from owlt_mcp_server.utils.trans_func import uni_translate
from owlt_mcp_server.utils.trans_func import dseek_translate
from owlt_mcp_server.utils.trans_func import lara_translate

@mcp.tool()
def translate_text(text: str, language: str) ->str:
    return uni_translate(text, language)
    
    
    
@mcp.tool()
def use_deepseek_translate(text: str, language: str) ->str:
    return dseek_translate(text, language)
    
@mcp.tool()
def use_lara(text: str, language: str) ->str:
    return lara_translate(text, language)