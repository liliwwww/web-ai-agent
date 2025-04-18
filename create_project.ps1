# 文件名：create_project.ps1
# 右键选择 "使用 PowerShell 运行"
# 或执行：powershell -ExecutionPolicy Bypass -File create_project.ps1

param(
    [string]$ProjectName = "web-ai-agent"
)

# 创建目录结构
$dirs = @(
    "$ProjectName",
    "$ProjectName\config\elements",
    "$ProjectName\config\prompts",
    "$ProjectName\src\core",
    "$ProjectName\src\utils",
    "$ProjectName\src\tests",
    "$ProjectName\scripts",
    "$ProjectName\logs"
)

New-Item -Path $dirs -ItemType Directory -Force | Out-Null

# 生成 requirements.txt
@"
playwright==1.42.0
python-dotenv==1.0.0
deepseek-api==0.1.2
json5==0.9.14
pytest==8.0.2
jsonschema==4.21.1
"@ | Out-File -Encoding utf8 "$ProjectName\requirements.txt"

# 生成 .env 示例
@"
DEEPSEEK_API_KEY=your_api_key_here
DEFAULT_PAGE_URL=https://your-target-website.com
CONFIG_DIR=./config/elements
"@ | Out-File -Encoding utf8 "$ProjectName\.env.example"

# 生成核心代码 (agent.py)
@"
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from ..utils.ai_integration import DeepSeekClient
from ..utils.playwright_helpers import SmartLocator

class WebAIAgent:
    def __init__(self):
        load_dotenv()
        self.client = DeepSeekClient(os.getenv("DEEPSEEK_API_KEY"))
        self.locator = SmartLocator(os.getenv("CONFIG_DIR"))
    
    def execute_command(self, command: str):
        '''执行自然语言指令'''
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(os.getenv("DEFAULT_PAGE_URL"))
            
            actions = self._parse_command(command)
            for action in actions:
                self._perform_action(page, action)
            
            browser.close()

    def _parse_command(self, command: str) -> list:
        '''解析自然语言指令'''
        prompt = self._build_prompt(command)
        return self.client.generate_actions(prompt)

    def _perform_action(self, page, action: dict):
        '''执行单个操作'''
        element = self.locator.find_element(page, action['element_name'])
        if action['action_type'] == 'fill':
            element.fill(action['value'])
        elif action['action_type'] == 'click':
            element.click()
"@ | Out-File -Encoding utf8 "$ProjectName\src\core\agent.py"

# 生成批处理安装脚本
@"
@echo off
REM 文件名：install.bat
echo 正在安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败，请检查Python环境
    exit /b 1
)

echo 安装Playwright浏览器...
playwright install
playwright install-deps

echo 初始化测试...
python -m pytest src\tests\ -v

if not exist ".env" (
    copy .env.example .env
    echo 请编辑.env文件配置API密钥和网站URL
)
"@ | Out-File -Encoding utf8 "$ProjectName\scripts\install.bat"

# 生成调试脚本
@"
# 文件名：debug_console.py
import code
from src.core.agent import WebAIAgent

agent = WebAIAgent()
print("调试控制台已启动，可用命令：")
print("- execute('你的指令')")
print("- debug_element('元素名称')")

def execute(cmd):
    return agent.execute_command(cmd)

code.interact(local=locals())
"@ | Out-File -Encoding utf8 "$ProjectName\scripts\debug_console.py"

# 输出完成信息
Write-Host "项目 $ProjectName 创建完成！" -ForegroundColor Green
Write-Host "后续步骤："
Write-Host "1. 进入项目目录：cd $ProjectName"
Write-Host "2. 运行安装脚本：scripts\install.bat"
Write-Host "3. 编辑 .env 文件配置参数"
Write-Host "4. 启动调试控制台：python scripts\debug_console.py"