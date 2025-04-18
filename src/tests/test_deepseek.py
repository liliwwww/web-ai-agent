# Please install OpenAI SDK first: `pip3 install openai`
import sys
import os
from openai import OpenAI
import json


# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ''))

print(f"src::{src_path}")
# 将 src 目录添加到系统路径中
sys.path.append(src_path)


from utils.deepseek_api import DeepSeekClient

client = OpenAI(api_key="sk-811ba66952094c55b56b51ff87a3013b", base_url="https://api.deepseek.com")


prompt = '''
根据以下元素配置将用户指令转换为操作序列：
[
  {
    "name": "代理商编号输入框",
    "selector": "input[name='agent_num']",
    "type": "text_input"
  },
  {
    "name": "代理商名称输入框",
    "selector": "input[name='agent_name']",
    "type": "text_input"
  },
  {
    "name": "法人身份证号精准查询框",
    "selector": "input[name='_identity_num']",
    "type": "text_input"
  },
  {
    "name": "销售经理姓名输入框",
    "selector": "#sm_name",
    "type": "text_input"
  },
  {
    "name": "业务员查询按钮（销售）",
    "selector": "button#haha1",
    "type": "clickable"
  },
  {
    "name": "运营经理姓名输入框",
    "selector": "input[name='maintain.sm_name']",
    "type": "text_input"
  },
  {
    "name": "业务员查询按钮（运营）",
    "selector": "button#haha",
    "type": "clickable"
  },
  {
    "name": "登录账号输入框",
    "selector": "#admin_name",
    "type": "text_input"
  },
  {
    "name": "部门选择下拉框",
    "selector": "select[name='department']",
    "type": "dropdown"
  },
  {
    "name": "大区选择下拉框",
    "selector": "select[name='argeaarea']",
    "type": "dropdown"
  },
  {
    "name": "分公司选择下拉框",
    "selector": "select[name='branchoffice']",
    "type": "dropdown"
  },
  {
    "name": "审核状态下拉框",
    "selector": "select[name='agent_status']",
    "type": "dropdown"
  },
  {
    "name": "代理商性质下拉框",
    "selector": "select[name='agent_nature']",
    "type": "dropdown"
  },
  {
    "name": "添加时间起始日期选择器",
    "selector": "input[name='startlocaldate']",
    "type": "date_picker"
  },
  {
    "name": "添加时间截止日期选择器",
    "selector": "input[name='endlocaldate']",
    "type": "date_picker"
  },
  {
    "name": "查询按钮",
    "selector": "button[data-icon='search']",
    "type": "clickable"
  },
  {
    "name": "清空查询按钮",
    "selector": "a[onclick*='reloadForm']",
    "type": "clickable"
  },
  {
    "name": "添加代理商按钮",
    "selector": "a[rel='AgentInfo_add']",
    "type": "clickable"
  }
]

指令解析规则：
1. 匹配最接近的element_name
2. 数值参数用{value}表示
3. 时间参数用ISO格式

用户指令：点击查询按钮,在代理商名称框中输入"wangdapeng",在审核状态下拉框下选择第1个选项,最后点击查询按钮

请输出JSON格式的操作序列：
{
  "actions": [
    {
      "element": "元素名称",
      "action": "操作类型",
      "value": "参数值"
    }
  ]
}

输出JSON 的schema定义如下：
schema1={
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
'''
prompt1 = "请给我讲一个笑话"


def callOpenJson():


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

    print("result")
    print(json.loads(response.choices[0].message.content))



def callOpenAI():


    client = OpenAI(
        api_key="sk-811ba66952094c55b56b51ff87a3013b",
        base_url="https://api.deepseek.com",
    )

    system_prompt = """
    The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format. 

    EXAMPLE INPUT: 
    Which is the highest mountain in the world? Mount Everest.

    EXAMPLE JSON OUTPUT:
    {
        "question": "Which is the highest mountain in the world?",
        "answer": "Mount Everest"
    }
    """

    user_prompt = "Which is the longest river in the world? The Nile River."

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

    print("result")
    print(json.loads(response.choices[0].message.content))

# 使用示例
if __name__ == "__main__":

    callOpenJson()
    
    '''

    print(f"\n\n\n{prompt}\n\n\n")

    # 初始化客户端
    client = DeepSeekClient(api_key="sk-811ba66952094c55b56b51ff87a3013b")

    
    
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
            prompt,
            schema=schema
        )
        print("解析结果：", actions)

        #aa = client.chat_completions( prompt)
        #print("解析结果：", aa)
    except ValueError as e:
        print("结构化生成失败：", str(e))
    
    '''