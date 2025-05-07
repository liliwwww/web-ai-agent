import json
import logging
from openai import OpenAI
from typing import Dict, List
from utils.deepseek_api import DeepSeekClient

logger = logging.getLogger(__name__)

class AIIntegration:
    def __init__(self, api_key: str):
        self.client = DeepSeekClient(api_key)

    def callOpenJson(self,prompt:str)-> Dict:

        client = OpenAI(
            api_key="sk-811ba66952094c55b56b51ff87a3013b",
            base_url="https://api.deepseek.com",
        )

        system_prompt = """
        你是一个前端工程师
        """

        user_prompt = prompt
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}]


        print("wait open ai")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
        )

        print("call openai result")
        return(json.loads(response.choices[0].message.content))


    #负责请求deepseek client
    #生成json;
    def generate_structured(self, prompt: str, schema: Dict) -> Dict:
        """生成结构化数据"""
        try:
            print("\n>>>> AIIntegration >>> 请求openai api wait...")
            response = self.callOpenJson( prompt )
            print(f"\n>>>> AIIntegration result:{response}")
            return response
        except Exception as e:
            logger.error(f"AI接口调用失败: {str(e)}")
            raise



    #生成操作序列。
    def generate_actions(self, prompt: str) -> List[Dict]:
        """生成操作序列"""
        #给 generate_structured 传递两个参数 
        # para1 提示词；
        # para2 schema；
        response = self.generate_structured(
            prompt=prompt,
            schema={
                "type": "object",
                "properties": {
                    "actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "element": {"type": "string"},
                                "action": {"type": "string"},
                                "value": {"type": "string"}
                            }
                        }
                    }
                }
            }
        )

        #直接返回, json中需要包含actions前缀
        return response