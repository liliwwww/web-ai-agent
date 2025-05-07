# web-ai-agent


##init_config.py是生成初始化的页面控件配置json.

##debugConsole.py是调试工具，主要处理流程
    1.根据用户prompt和 页面控件配置json， 生成执行指令actions(调用AI模型)
    2.通过playwright，执行执行指令actions.




## 因为py程序分包，如果跨包调用需要告诉python路径。

# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
print(f"src::{src_path}")
# 将 src 目录添加到系统路径中
sys.path.append(src_path)




{
  "elements": [
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
}