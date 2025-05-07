from playwright.sync_api import Page
from pathlib import Path
from typing import Optional, Dict
import logging
from core.buffer_manager import BufferManager
from utils.ai_integration import AIIntegration

logger = logging.getLogger(__name__)


#playwrigt辅助
#主要三个操作
#1. find_element
#2. _verify_element(self, page: Page, selector: str) -> bool:
#3. _fallback_locate
#4. _fallback_locate


class ElementLocator:
    def __init__(self, buffer: BufferManager, ai_integration: AIIntegration):
        self.buffer = buffer
        self.ai_integration = ai_integration


    # 返回的是 sector吧
    def find_element(self, page: Page, element_name: str, action_type: str):
        """智能元素定位"""

        # 优先使用缓冲区配置
        if element_config := self.buffer.get_element(element_name):
            selector = element_config.get('selector')
            print(f"     >>>buffer元素定位,{element_name}找selector>>>{selector}")
            if self._verify_element(page, selector):
                return selector

        #  AI后备定位
        print(f"     >>>buffer元素定位,找selector>>>{element_name} SELECTOR 不符合预期")
        #print(""">>>AI后备定位>>>""")
        #return self._fallback_locate(page, element_name, action_type)

    def _verify_element(self, page: Page, selector: str) -> bool:
        """验证元素的唯一性"""        
        try:
            elementCount = page.locator(selector).count()
            print(f"     >>>验证元素是否存在>>>{selector}<<< \n\n>>>number:::{elementCount}")
            
            if elementCount == 1:
                return True
            else:
                return False    

        except Exception:
            return False


    # 定位
    def _fallback_locate(self, page: Page, element_name: str, action_type: str):
        """AI辅助定位"""
        print(">>>AI辅助定位>>>")
        html_snippet = page.content()[:2000]
        prompt = f"""
根据以下页面片段定位元素：
{html_snippet}

需要定位的元素特征：
- 名称：{element_name}
- 预期操作类型：{action_type}

请返回最佳的CSS选择器：
"""
        selector = self._get_ai_selector(prompt)
        if self._verify_element(page, selector):
            self.buffer.manual_update(element_name, {"selector": selector})
            return page.locator(selector)
        raise ElementNotFoundError(f"无法定位元素: {element_name}")

    def _get_ai_selector(self, prompt: str) -> str:
        """调用AI获取选择器"""
        try:
            response = self.ai_integration.generate_structured(prompt, {})
            return response.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        except Exception as e:
            logger.error(f"AI选择器获取失败: {str(e)}")
            raise

class ElementNotFoundError(Exception):
    """自定义元素未找到异常"""
    pass