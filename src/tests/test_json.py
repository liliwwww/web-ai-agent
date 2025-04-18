# Please install OpenAI SDK first: `pip3 install openai`
import json

text = '''```json
{
  "elements": [
    {
      "element_name": "导航菜单切换按钮",
      "selector": "button.bjui-navbar-toggle",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "联动优势管理后台标题",
      "selector": "tracingprintstream.bjui-navbar-logo",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "日期显示",
      "selector": "span#bjui-date",
      "element_type": "text_input",
      "action_type": "fill"
    },
    {
      "element_name": "时间显示",
      "selector": "span#bjui-clock",
      "element_type": "text_input",
      "action_type": "fill"
    },
    {
      "element_name": "我的账户下拉菜单",
      "selector": "li.dropdown > a.dropdown-toggle",
      "element_type": "dropdown",
      "action_type": "select"
    },
    {
      "element_name": "修改密码",
      "selector": "a[href='/yhbackstage/AdminInfo/resetPass?admin_id=1']",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "注销登录",
      "selector": "a[onclick='loginUp()']",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "切换皮肤下拉菜单",
      "selector": "a.theme.blue",
      "element_type": "dropdown",
      "action_type": "select"
    },
    {
      "element_name": "黑白分明主题",
      "selector": "a.theme_default",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "橘子红了主题",
      "selector": "a.theme_orange",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "紫罗兰主题",
      "selector": "a.theme_purple",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "天空蓝主题",
      "selector": "a.theme_blue",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "绿草如茵主题",
      "selector": "a.theme_green",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "导航菜单左移按钮",
      "selector": "button.bjui-hnav-more-left",
      "element_type": "clickable",
      "action_type": "click"
    },
    {
      "element_name": "系统管理菜单",
      "selector": "a[data-toggle='slidebar'] > i.fa-check-square-o",
      "element_type": "clickable",
      "action_type": "click"
    }
  ]
}
```
'''

cleaned_text = text.replace("```json", "").strip()
cleaned_text = cleaned_text.replace("```", "").strip()

#

print(f"reponse>>>{cleaned_text}")

try:
    json.loads(cleaned_text)
    print("load ok ")
except Exception as e: 
    print(f"ERROR ERROR{e}")