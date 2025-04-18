# scripts/debug_console.py
from src.core.agent import WebAIAgent, Debugger
import systray

agent = WebAIAgent()

def execute(command: str):
    """执行示例：execute('在代理商编号输入9999')"""
    return agent.execute_command(command)

def validate(element: str):
    """验证元素：validate('代理商编号')"""
    return Debugger.validate_selector(element)

# 在 debug_console.py 中添加
systray.create_tray_icon()

print("调试控制台已就绪！")