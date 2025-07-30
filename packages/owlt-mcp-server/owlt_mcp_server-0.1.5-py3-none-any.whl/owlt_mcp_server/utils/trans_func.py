
# define translate api
import os
from openai import OpenAI
import deepl
import json

file_path = os.path.join(os.path.dirname(__file__), '..', 'myjson.json')
file_path = os.path.abspath(file_path)
with open(file_path, 'r') as f:
    config = json.load(f)

def llm_translate(text, target_lang):
    if target_lang is None:
        target_lang = "Chinese"
    
    
    if target_lang == "chinese" or target_lang == "中文" or target_lang == "zh":
        target_lang = "Chinese"
        
    client = OpenAI(
            # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
            #api_key=os.getenv("DASHSCOPE_API_KEY"),
            api_key = config.get("api_key_ali"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    messages = [
          {
            "role": "user",
            "content": text
          }
        ]
    translation_options = {
          "source_lang": "auto",
          "target_lang": target_lang
        }
        
    completion = client.chat.completions.create(
        model="qwen-mt-turbo",
        messages=messages,
        extra_body={
            "translation_options": translation_options
        }
    )
    
    translate_result = completion.choices[0].message.content
    #print(completion.choices[0].message.content)
    
    return translate_result
    

def deepl_translate(text, target_lang):
    # map to 规定的语言代码
    if target_lang in ["english", "English", "en"]:
        target_lang = "EN-US"
        
    auth_key = config.get("api_key_deepl")  # Replace with your key
    deepl_client = deepl.DeepLClient(auth_key)

    result = deepl_client.translate_text(text, target_lang=target_lang)
    #print(result.text)  # "Bonjour, le monde !"  
    return result.text
    
# translate by two tools   
def uni_translate(text, target_lang):
    return "T1:" + llm_translate(text, target_lang) + "\nT2:" +  deepl_translate(text, target_lang)
    
#test = "我喜欢武汉的热干面"
#test = "I love Wuhan's hot dry noodles"
#print(uni_translate(test, "zh") )
#print(deepl_translate(test, "EN-US") )