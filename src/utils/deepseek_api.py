# src/utils/deepseek_api.py
import json
import logging
import requests
from typing import Dict, Optional, Any
from pydantic import BaseModel, ValidationError
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class DeepSeekResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cost_ms: Optional[int] = None

class DeepSeekClient:
    def __init__(
        self,
        api_key: str='sk-811ba66952094c55b56b51ff87a3013b',
        base_url: str = "https://api.deepseek.com/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        DeepSeek API 客户端
        
        参数：
        - api_key: 认证密钥
        - base_url: API基础地址
        - timeout: 请求超时时间（秒）
        - max_retries: 最大重试次数
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _handle_response(self, response: requests.Response) -> DeepSeekResponse:
        """统一处理API响应"""
        try:
            response.raise_for_status()
            resp_data = response.json()
            
            return DeepSeekResponse(
                success=True,
                data=resp_data.get('data'),
                cost_ms=resp_data.get('cost_ms'),
            )
        except json.JSONDecodeError:
            logger.error("Invalid JSON response")
            return DeepSeekResponse(
                success=False,
                error="Invalid response format"
            )
        except RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return DeepSeekResponse(
                success=False,
                error=str(e)
            )

    def generate(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> DeepSeekResponse:
        """
        生成文本内容
        
        参数：
        - prompt: 输入提示
        - model: 使用的模型名称
        - temperature: 生成温度
        - max_tokens: 最大token数
        """
        endpoint = f"{self.base_url}/completions"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout
                )
                return self._handle_response(response)
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    return DeepSeekResponse(
                        success=False,
                        error=f"Request failed after {self.max_retries} retries: {str(e)}"
                    )
                logger.warning(f"Retrying ({attempt+1}/{self.max_retries})...")

        return DeepSeekResponse(success=False, error="Unknown error")

    def chat_completions(
        self,
        messages: list,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        response_format: Optional[dict] = None,
        **kwargs
    ) -> DeepSeekResponse:
        """
        聊天补全接口（兼容OpenAI格式）
        
        参数：
        - messages: 消息列表
        - model: 模型名称
        - response_format: 响应格式要求
        """
        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }

        

        if response_format:
            payload["response_format"] = response_format


        return self._send_request(endpoint, payload)

    def generate_structured(
        self,
        prompt: str,
        schema: dict,
        model: str = "deepseek-chat",
        **kwargs
    ) -> Dict:
        """
        生成结构化数据
        
        参数：
        - prompt: 输入提示
        - schema: JSON Schema验证模板
        - model: 模型名称
        """
        messages = [{
            "role": "user",
            "content": f"{prompt}\n\n请严格按照以下JSON Schema格式响应：\n{json.dumps(schema, indent=2)}"
        }]

        print(f"\n\n\n >>>>请求deepseek  {prompt} wait...")

        response = self.chat_completions(
            messages=messages,
            model=model,
            response_format={"type": "json_object"},
            **kwargs
        )

        print(f">>>>请求deepseek result: {response}")
        if not response.success:
            raise ValueError(f"API请求失败：{response.error}")

        try:
            
            print(response.choices[0].message.content)

            text = response.data['choices'][0]['message']['content']
            cleaned_text = text.replace("```json", "").strip()
            cleaned_text = cleaned_text.replace("```", "").strip()
            print(f">>>>请求deepseek back {cleaned_text}")
            return json.loads(cleaned_text)
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"响应解析失败：{str(e)}")
            raise ValueError("无效的响应格式") from e

    def _send_request(self, endpoint: str, payload: dict) -> DeepSeekResponse:
        """发送通用请求"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout
                )

                print(">>>deepseek api>>>_send_request>>>")
                return self._handle_response(response)
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    return DeepSeekResponse(
                        success=False,
                        error=f"Request failed after {self.max_retries} retries: {str(e)}"
                    )
                logger.warning(f"Retrying ({attempt+1}/{self.max_retries})...")

        return DeepSeekResponse(success=False, error="Unknown error")

# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = DeepSeekClient(api_key="your_api_key_here")

    # 生成文本示例
    response = client.generate("请写一首关于春天的诗")
    if response.success:
        print("生成结果：", response.data)
    else:
        print("错误：", response.error)

    # 结构化数据生成示例
    schema = {
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
    
    try:
        actions = client.generate_structured(
            "在代理商编号输入9999并点击查询",
            schema=schema
        )
        print("解析结果：", actions)
    except ValueError as e:
        print("结构化生成失败：", str(e))