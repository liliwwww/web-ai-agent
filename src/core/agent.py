import os
import json
import logging
from pathlib import Path
from typing import List, Dict
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from utils.ai_integration import AIIntegration  # 引入 AIIntegration 类
from utils.playwright_helpers import ElementLocator
from core.buffer_manager import BufferManager
from core.ui_pw_select import select_option_and_verify


##主要三个方法：

1.#识别页面元素
#    def recognize_elements(self, url: str):

2.#AI解析 并执行命令
#    def execute_command(self,  url:str, command: str):

3.#执行page操作
#    def _perform_action(self, page, action: Dict):    


# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class WebAIAgent:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = AIIntegration(api_key)  # 使用 AIIntegration 类初始化 self.client
        self.buffer = BufferManager(
            config_dir=Path(os.getenv("CONFIG_DIR")),
            default_profile="default"
        )
        self.locator = ElementLocator(self.buffer, self.client)
        self.current_page = None

    def initPage():
        # 连接到 Chrome 调试端口
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        print("成功连接到 Chrome 调试端口")

        # 获取现有上下文和页面
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        return page

    #识别页面元素
    def recognize_elements(self, url: str):
        """智能识别页面元素"""
        with sync_playwright() as p:

            if ( str != 'current-Page'):
                print("打开新页面")
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(url)    
            else:
                print("连接到 Chrome 调试端口")
                # 连接到 Chrome 调试端口
                browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("成功连接到 Chrome 调试端口")

                # 获取现有上下文和页面
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()

            #网络监控集成    
            page.on("request", lambda req: logger.debug(f"Request: {req.method} {req.url}"))
            page.on("response", lambda res: logger.debug(f"Response: {res.status} {res.url}"))

            try:
                main_content = page.query_selector('main') or page.query_selector('body')
                html_snippet = main_content.inner_html()[:3000]  # 限制内容长度
                prompt = self._build_element_prompt(html_snippet)

                # 调用AI接口
                response = self.client.generate_structured(
                    prompt=prompt,
                    schema_path="config/schemas/element_schema.json"
                )

                # 更新缓冲区
                self.buffer.batch_update(response["elements"])
                logger.info(f"成功识别到{len(response['elements'])}个元素")

                # 保存页面快照
                page.screenshot(path=f"config/snapshots/{url.split('//')[1]}.png")

            except Exception as e:
                logger.error(f"元素识别失败: {str(e)}")
                raise
            finally:
                browser.close()

    #执行命令
    def execute_command(self,  url:str, command: str):
        """执行自然语言指令"""
        with sync_playwright() as p:

            if ( url == 'current-Page'):
                print("连接到 Chrome 调试端口")
                # 连接到 Chrome 调试端口
                browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
                print("成功连接到 Chrome 调试端口")

                # 获取现有上下文和页面
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
    
            else:                
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(url)
                print("打开新页面")

                
            #网络监控集成    
            page.on("request", lambda req: logger.debug(f"Request: {req.method} {req.url}"))
            page.on("response", lambda res: logger.debug(f"Response: {res.status} {res.url}"))


            try:
                actions = self._parse_command(command)
                for action in actions:
                    self._perform_action(page, action)
                logger.info("指令执行成功")
            except Exception as e:
                logger.error(f"指令执行失败: {str(e)}")
                raise
            #finally:
                #browser.close()

    def _build_element_prompt(self, html: str) -> str:
        """构建元素识别提示词"""
        return f"""
作为专业的Web自动化助手，请分析以下HTML片段：
{html}

请用JSON格式返回分析结果，包含以下字段：
- element_name: 基于可见文本或标签的语义化名称
- selector: 优先使用aria-label、id、name的属性选择器
- element_type: 从[text_input, dropdown, date_picker, clickable]中选择
- action_type: 支持的操作类型[fill, click, select, date_select]

示例输出：
{{
  "elements": [
    {{
      "element_name": "代理商编号",
      "selector": "input[aria-label='代理商编号']",
      "element_type": "text_input",
      "action_type": "fill"
    }}
  ]
}}
"""

    def _parse_command(self, command: str) -> List[Dict]:
        """解析自然语言指令"""
        #step1 那配置文件的所有element
        elements = self.buffer.list_elements()
        
        #step2 准备提示词
        prompt = f"""
根据以下元素配置将用户指令转换为操作序列：
{json.dumps(elements, indent=2, ensure_ascii=False)}

指令解析规则：
1. 匹配最接近的element_name
2. 数值参数用{{value}}表示
3. 时间参数用ISO格式

用户指令：{command}

请输出JSON格式的操作序列：
{{
  "actions": [
    {{
      "element": "元素名称",
      "action": "操作类型",
      "value": "参数值" 
    }}
  ]
}}
"""
        #step3 请求deepseek,返回 action list
        return self.client.generate_actions(prompt)


    #执行page操作
    def _perform_action(self, page, action: Dict):
        """执行单个操作"""
        #print(">>>_perform_action 跳过智能定位")
        

        #上面都找到了。没有找到就不会有返回结果了
        selector = self.locator.find_element(
            page,
            action["element"],
            action["action"]
        )

        # 根据返回的selector，再次构建element.
        # 因为，在select_option_and_verify()方法中，需要selector
        # 在这个类里面，又不想再初始化buffer_manage了
        element = page.locator(selector)
        if element is None:
            print("     _>>>perform_action 没有找到预期的 page.element 不执行操作")
            return

        #
        #element = page.locator(selector)
        print(f"     >>>_perform_action:{action["element"]}::{action["action"]}" )

        #常用指令：
        #document.querySelectorAll('input[name="agent_num"]') 

        try:
            #text   
            if action["action"] == "text_input":
                print(f"     >>>_perform_action>>> fill:{action["value"]}" )
                element.fill(action["value"])    
                print(f"     >>>_perform_action>>> fill:ok" )
            
            #button
            elif action["action"] == "clickable":
                print(f"     >>>_perform_action>>> click" )
                element.click()
                print(f"     >>>_perform_action>>> click:ok" )
            
            #select
            elif action["action"] == "dropdown":
                print(f"     >>>_perform_action>>> select 第{action["value"]}个选项" )
                # 不用element了
                # element.select_option(action["value"],timeout=5000);
                result = select_option_and_verify(page,selector,action["value"])
                print(f"     >>>_perform_action>>> select ok" )
            else:
                print(f">>>_perform_action>>> ACTION NOT SUPPORTED" )
            
            
            self.buffer.record_success(action["element"])
        except Exception as e:
            print(f">>>_perform_action ERROR ERROR ERROR {e}")


#
class Debugger:
    """调试工具类"""
    @staticmethod
    def validate_selector(element_name: str, page):
        """验证选择器有效性"""
        agent = WebAIAgent()
        with sync_playwright() as p:
            #browser = p.chromium.launch()
            #page = browser.new_page()
            #page.goto(os.getenv("DEFAULT_PAGE_URL"))

            try:
                element = agent.locator.find_element(page, element_name)
                element.highlight()
                page.wait_for_timeout(2000)
                return True
            except Exception as e:
                logger.error(f"验证失败: {str(e)}")
                return False
            #finally:
            #    browser.close()
