import sys
import os

# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))

print(f"src::{src_path}")
# 将 src 目录添加到系统路径中
sys.path.append(src_path)




from core.agent import WebAIAgent

agent = WebAIAgent()
agent.recognize_elements("current-Page")