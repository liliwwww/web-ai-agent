from bs4 import BeautifulSoup
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
import re
from typing import List, Dict
import datetime
import json
import os
import sys

# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', ''))

print(f"src::{src_path}")
# 将 src 目录添加到系统路径中
sys.path.append(src_path)

from utils.deepseek_api import DeepSeekClient

'''
graph TD
    A[原始HTML 300k] --> B{预处理}
    B --> C[DOM结构分析]
    B --> D[关键区域提取]
    D --> E[分块处理]
    E --> F[模型识别]
    F --> G[结果聚合]
    G --> H[验证与缓存]
'''

class HTMLPreprocessor:
    def __init__(self, max_size=5000):
        self.max_size = max_size  # 每块最大token数
        
    def process(self, html: str) -> list:
        """分块处理流程"""
        # 1. 基础清理

        print(f"清理前{len(html)}")
        cleaned_html = self._basic_clean(html)
        print(f"清理后{len(cleaned_html)}")
        
        # 2. 提取关键区域
        key_sections = self._extract_key_sections(cleaned_html)
        
        # 3. 智能分块
        chunks = self._intelligent_chunking(key_sections)
        
        return chunks
    
    def _basic_clean(self, html: str) -> str:
        """基础清理"""
        # 移除脚本和样式
        cleaned = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
        cleaned = re.sub(r'<style.*?</style>', '', cleaned, flags=re.DOTALL)
        # 压缩空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
    
    def _extract_key_sections(self, html: str) -> list:
        """提取包含交互元素的关键区域"""
        soup = BeautifulSoup(html, 'html.parser')
        sections = []
        
        # 优先提取已知交互区域

        num = 0
        print(f">>>_extract_key_sections ")
        for tag in soup.find_all(['form', 'main', 'div[role="main"]', 'section']):
            num = num + 1
            print(f">>>_extract_key_sections {num} \n {tag.text.strip()} \n")
            if len(tag.text.strip()) > 50:  # 过滤空容器
                sections.append(str(tag))
                
        # 保底提取所有含控件的区域
        print(f">>>_extract_key_sections ELEMENT")
        control_selectors = ['input', 'button', 'select', 'textarea']
        for control in soup.find_all(control_selectors):
            num = num + 1
            parent = control.find_parent(['div', 'section'])
            print(f">>>_extract_key_sections {num} \n {parent} \n")
            
            if parent and parent not in sections:
                sections.append(str(parent))
                
        return sections
    
    def _intelligent_chunking(self, sections: list) -> list:
        """智能分块策略"""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for section in sections:
            section_size = len(section.split())  # 按词数估算
            
            if current_size + section_size > self.max_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
                
            current_chunk.append(section)
            current_size += section_size
            
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks



class ChunkProcessor:
    def __init__(self, api_key: str):
        self.client = DeepSeekClient(api_key)
        self.cache = {}
        
    def process_chunks(self, chunks: List[str]) -> Dict:
        """处理所有分块"""
        all_elements = {}
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            elements = self._process_single_chunk(chunk)
            all_elements.update(elements)
            
        return all_elements
    
    def _process_single_chunk(self, chunk: str) -> Dict:
        """处理单个分块"""
        # 生成优化提示词
        prompt = self._build_prompt(chunk)
        
        # 调用大模型
        try:
            response = self.client.generate_structured(
                prompt=prompt,
                schema=self._get_schema(),
                max_tokens=2000
            )
            return self._parse_response(response)
        except Exception as e:
            print(f"Chunk processing failed: {str(e)}")
            return {}
    
    def _build_prompt(self, chunk: str) -> str:
        """构建分块提示词"""
        return f"""
作为前端自动化专家，请分析以下HTML片段中的交互元素：

**分析要求：**
1. 识别所有表单控件（输入框、按钮、下拉菜单等）
2. 为每个元素生成语义化名称（如：'登录按钮'）
3. 生成可靠的CSS选择器（优先使用aria-label/id/name）
4. 确定元素类型：[text_input, dropdown, date_picker, clickable]

**示例输出：**
{{
  "elements": [
    {{
      "name": "用户名输入框",
      "selector": "input#username",
      "type": "text_input"
    }}
  ]
}}

**当前分块内容：**
{chunk}...（共{len(chunk)}字符）
"""

    def _get_schema(self):
        """返回JSON Schema验证模板"""
        return {
            "type": "object",
            "properties": {
                "elements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "selector": {"type": "string"},
                            "type": {"type": "string"}
                        },
                        "required": ["name", "selector", "type"]
                    }
                }
            }
        }
    
    def _parse_response(self, response: Dict) -> Dict:
        """解析模型响应"""
        parsed = {}
        for elem in response.get('elements', []):
            key = f"{elem['name']}_{elem['type']}"
            parsed[key] = elem
        return parsed
    

#######################
class ResultIntegrator:
    def __init__(self):
        self.selector_counter = {}
        
    def integrate(self, all_results: List[Dict]) -> Dict:
        """整合多块结果"""
        merged = {}
        
        # 第一阶段：合并结果
        for result in all_results:
            for key, elem in result.items():
                if key not in merged:
                    merged[key] = elem
                    self._count_selector(elem['selector'])
                else:
                    self._resolve_conflict(merged[key], elem)
                    
        # 第二阶段：验证选择器
        return self._validate_selectors(merged)
    
    def _count_selector(self, selector: str):
        """统计选择器出现次数"""
        self.selector_counter[selector] = self.selector_counter.get(selector, 0) + 1
        
    def _resolve_conflict(self, existing: Dict, new: Dict):
        """解决元素冲突"""
        # 优先选择高频选择器
        existing_count = self.selector_counter[existing['selector']]
        new_count = self.selector_counter[new['selector']]
        
        if new_count > existing_count:
            existing.update(new)
            
    def _validate_selectors(self, elements: Dict) -> Dict:
        """验证选择器有效性"""
        validated = {}
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('about:blank')
            
            for key, elem in elements.items():
                page.set_content('<html>' + elem['_context'] + '</html>')  # 载入原始上下文
                if page.locator(elem['selector']).count() > 0:
                    validated[key] = elem
                    
            browser.close()
        return validated


def read_file_content(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"错误：文件 {file_name} 未找到。")
    except PermissionError:
        print(f"错误：没有权限读取文件 {file_name}。")
    except Exception as e:
        print(f"发生未知错误：{e}")
    return None

from bs4 import BeautifulSoup

###
###
###
def print_body_children(html, output_file):
    soup = BeautifulSoup(html, 'lxml')
    body = soup.find('body')

    if not body:
        result = "未找到<body>标签"
    else:
        result = "=" * 40 + "\n"
        result += "<body>的直接子级标签：\n"
        result += "=" * 40 + "\n"

        for idx, child in enumerate(body.find_all(recursive=False), 1):
            print("Monitor")
            result += f"\n子标签 #{idx}:\n"
            result += f"标签名: {child.name}\n"
            #result += f"完整内容:\n{child}\n"
            print("打印二级")
            print_direct_subtags(child, output_file, idx, child.name)
            result += "-" * 40 + "\n"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"内容已成功写入到 {output_file} 文件中。")
    except Exception as e:
        print(f"写入文件时出现错误: {e}")
    

###
###
###

def print_body_second_level_tags(html, output_file):
    try:
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html, 'lxml')
        # 查找 body 标签
        body = soup.find('body')

        if body is None:
            result = "未找到 <body> 标签。"
        else:
            result = "=" * 40 + "\n"
            result += "<body> 标签下第 1 层级、第 2 层级和第 3 层级的标签信息：\n"
            result += "=" * 40 + "\n"

            # 遍历 body 标签下的第 1 层级标签
            for idx1, first_level_tag in enumerate(body.find_all(recursive=False), 1):
                result += f"\n第 1 层级子标签 #{idx1}:\n"
                result += f"标签名: {first_level_tag.name}\n"
                # 打印第 1 层级标签的属性
                if first_level_tag.attrs:
                    result += f"属性: {first_level_tag.attrs}\n"
                else:
                    result += "属性: 无\n"
                #result += f"完整内容:\n{first_level_tag}\n"
                result += "-" * 40 + "\n"

                # 遍历第 1 层级标签下的第 2 层级标签
                for idx2, second_level_tag in enumerate(first_level_tag.find_all(recursive=False), 1):
                    result += f"  第 2 层级子标签 #{idx2}:\n"
                    result += f"  标签名: {second_level_tag.name}\n"
                    # 打印第 2 层级标签的属性
                    if first_level_tag.attrs:
                        result += f"属性: {second_level_tag.attrs}\n"
                    else:
                        result += "属性: 无\n"
                    #result += f"  完整内容:\n{second_level_tag}\n"
                    result += "  " + "-" * 40 + "\n"

                    # 遍历第 2 层级标签下的第 3 层级标签
                    for idx3, third_level_tag in enumerate(second_level_tag.find_all(recursive=False), 1):
                        result += f"    第 3 层级子标签 #{idx3}:\n"
                        result += f"    标签名: {third_level_tag.name}\n"
                        # 打印第 3 层级标签的属性
                        if first_level_tag.attrs:
                            result += f"属性: {third_level_tag.attrs}\n"
                        else:
                            result += "属性: 无\n"
                        result += f"    完整内容:\n{third_level_tag}\n"
                        result += "    " + "-" * 40 + "\n"

        # 将结果写入文件
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(result)

        print(f"内容已成功写入到 {output_file} 文件中。")
        print(result)

    except Exception as e:
        print(f"发生错误: {e}")
    
    

def main():
    # 初始化
    preprocessor = HTMLPreprocessor(max_size=2000)
    chunk_processor = ChunkProcessor(api_key="sk-811ba66952094c55b56b51ff87a3013b")
    integrator = ResultIntegrator()
    
    # 获取原始HTML
    #with sync_playwright() as p:
    #    browser = p.chromium.launch()
    #    page = browser.new_page()
    #    page.goto("target_url")
    #    full_html = page.content()
    #    browser.close()
    
    fileName = r'C:\Users\wdp\project\aitest\screenshots\page_20250414_190348.html'
    full_html = read_file_content(fileName)

    print_body_second_level_tags(full_html, "ad1bccd.txt")
    '''
    # 分阶段处理
    chunks = preprocessor.process(full_html)
    all_results = [chunk_processor.process_chunks(chunks)]
    final_elements = integrator.integrate(all_results)
    
    # 保存结果
    suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    
    with open(f'elements_{suffix}.json', "w") as f:
        json.dump(final_elements, f, indent=2)
    '''

if __name__ == "__main__":
   main()         