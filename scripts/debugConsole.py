# debug_console.py
import cmd
import json
import logging
import sys
import os
from typing import List, Dict
from pathlib import Path
from playwright.sync_api import sync_playwright




# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))

print(f"src::{src_path}")
# 将 src 目录添加到系统路径中
sys.path.append(src_path)


from core.agent import WebAIAgent,logger
from core.buffer_manager import BufferManager
from utils.playwright_helpers import ElementLocator
from utils.ai_integration import AIIntegration


'''
# 1. 显示当前配置
(web-ai) > show_config

# 2. 调试问题元素
(web-ai) > debug_element 查询按钮

# 3. 更新选择器
(web-ai) > update_selector 查询按钮 button#search-btn

# 4. 测试指令
(web-ai) > execute '在查询按钮输入测试并点击'

# 5. 查看日志
(web-ai) > view_logs 5
'''

class DebugConsole(cmd.Cmd):
    intro = """
=== Web自动化调试控制台 ===
输入 help 查看可用命令
输入 exit 退出程序
"""
    prompt = "(web-ai) > "

    def __init__(self):
        super().__init__()
        self.agent = WebAIAgent()
        self.buffer = BufferManager(config_dir=Path("config/elements"))

        print(f"buffer \n\n\n") 
        self.buffer.list_elements()
        print("f\n\n\n")

        aiClient = AIIntegration(
            api_key=os.getenv("DEEPSEEK_API_KEY")
        )
        
        self.locator = ElementLocator(self.buffer, aiClient)
        logging.basicConfig(level=logging.INFO)

    def do_chrome(self, actions)-> List[Dict]:

        print(f"_do_chrome1 {self}")
        print(f"_do_chrome2 {actions}")
        
        with sync_playwright() as p:
            #browser = p.chromium.launch(headless=False)
            #page = browser.new_page()
            #page.goto(self.agent.default_url)

            print("连接到 Chrome 调试端口")
            # 连接到 Chrome 调试端口
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("成功连接到 Chrome 调试端口")

            # 枚举所有上下文
            for context in browser.contexts:
                print(f"Context ID: {context}")
                # 枚举当前上下文下的所有页面
                for page1 in context.pages:
                    print(f"  Page URL: {page1.url}")
                    if page1.url == 'http://39.105.217.139:8181/yhbackstage/Index/index':
                        page = page1
            print("自检完成")
            print(f"\n\nPage title: {page.title()}\n\n")
            print(">>Go")


            #网络监控集成    
            page.on("request", lambda req: logger.debug(f"Request: {req.method} {req.url}"))
            page.on("response", lambda res: logger.debug(f"Response: {res.status} {res.url}"))

            #把json转换成指令列表
            action_List = actions.get('actions',[])
            for idx, action in enumerate(action_List, 1):
                print(f"\n⚡ 正在执行操作 {idx}/{len(action_List)}:")
                print(f"  元素: {action['element']}")
                print(f"  操作: {action['action']}")
                if 'value' in action:
                    print(f"  值: {action['value']}")
                
                self.agent._perform_action(page, action)
                print("✅ 操作成功")
            
            #browser.close()
        print("\n🎉 所有操作执行完成")

    def do_execute(self, arg):
        """执行自然语言指令\n用法: execute <指令文本>\n示例: execute '在代理商编号输入9999'"""
        if not arg:
            print("错误：需要提供指令文本")
            return
            
        try:
            print("🔄 正在解析指令...")
            actions = self.agent._parse_command(arg)
            print(f"🔧 解析到 {len(actions)} 个操作")
            
            self.do_chrome( actions)
            
        except Exception as e:
            logging.error(f"执行失败: {str(e)}")
            print(f"❌ 发生错误: {str(e)}")

    def do_debug_element(self, arg):
        """调试元素定位\n用法: debug_element <元素名称>\n示例: debug_element '代理商编号'"""
        if not arg:
            print("错误：需要提供元素名称")
            return
            
        try:
            print(f"🔍 正在验证元素 '{arg}'...")
            selector = self.buffer.get_element(arg)['selector']


            print(f"selector from buffer::{selector}")
            
            if False:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=False)
                    page = browser.new_page()
                    page.goto(self.agent.default_url)
                    
                    element = page.locator(selector)
                    count = element.count()
                    
                    if count > 0:
                        element.first().highlight()
                        print(f"✅ 找到 {count} 个匹配元素")
                        page.wait_for_timeout(2000)  # 保持高亮状态
                    else:
                        print("❌ 未找到匹配元素")
                    
                    browser.close()
                
        except Exception as e:
            print(f"❌ 调试失败: {str(e)}")

    def do_show_config(self, arg):
        """显示当前元素配置\n用法: show_config [元素名称]\n示例: show_config 或 show_config '代理商编号'"""
        print("show11")
        try:
            elements = self.buffer.list_elements()
            if arg:
                findIt = False
                for element in elements:
                    #print(f" compare::{element.get("name")} vs {arg}")
                    if element.get("name") == arg:
                        print(element["selector"])
                        print(json.dumps(element, indent=2))
                        findIt = True
                if(  not findIt):
                    print(f"元素 '{arg}' 不存在")

            else:
                
                print(json.dumps(elements, indent=2))
                
        except Exception as e:
            print(f"❌ 获取配置失败: {str(e)}")

    def do_update_selector(self, arg):
        """手动更新元素选择器\n用法: update_selector <元素名称> <新选择器>\n示例: update_selector 查询按钮 'button.search-btn'"""
        args = arg.split()
        if len(args) != 2:
            print("错误：需要提供元素名称和新选择器")
            return
            
        element_name, new_selector = args
        try:
            self.buffer.manual_update(element_name, {"selector": new_selector})
            print(f"✅ 已更新 {element_name} 的选择器为: {new_selector}")
        except Exception as e:
            print(f"❌ 更新失败: {str(e)}")

    def do_view_logs(self, arg):
        """查看最新日志\n用法: view_logs [行数=10]"""
        lines = 10
        try:
            if arg: lines = int(arg)
            with open("logs/app.log") as f:
                print("".join(f.readlines()[-lines:]))
        except Exception as e:
            print(f"❌ 查看日志失败: {str(e)}")

    def do_exit(self, arg):
        """退出控制台"""
        print("👋 正在退出...")
        return True

    def default(self, line):
        """默认执行指令的快捷方式"""
        if line.startswith("!"):
            self.do_execute(line[1:])
        else:
            print(f"⚠️ 未知命令: {line}\n输入 help 查看可用命令")



    # 添加截图功能
    def do_screenshot(self, arg):
        """保存当前页面截图"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(self.agent.default_url)
            page.screenshot(path=f"screenshots/{arg}.png")
            browser.close()

    # 添加元素搜索功能
    def do_search_element(self, arg):
        """搜索包含关键字的元素"""
        elements = [k for k in self.buffer.list_elements() if arg in k]
        print("匹配元素:", elements)


string_data = "{'actions': [{'element': '代理商名称输入框', 'action': 'text_input', 'value': '1111'}, {'element': '审核状态下拉框', 'action': 'dropdown', 'value': '1'}, {'element': '查询按钮', 'action': 'clickable', 'value': ''}]}"
text = "{'actions': [{'element': '查询按钮', 'action': 'clickable', 'value': ''}]}"


if __name__ == "__main__":
    try:
        #原始字符串
        DebugConsole().cmdloop()

    except KeyboardInterrupt:
        print("\n操作已取消")


#根据action，单步调试解析action
#        print("AAAA")
#        string_data = string_data.replace("'","\"")
#        actions = json.loads(string_data)
        
#        cc = DebugConsole()
#        cc.do_chrome(actions)