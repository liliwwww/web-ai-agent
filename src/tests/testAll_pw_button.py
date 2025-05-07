import re
from playwright.sync_api import Playwright, sync_playwright, Page,  expect
import time
import asyncio


### 验证一下窗口

def close_dialog_if_open(page: Page, dialog_locator):
    """关闭打开的对话框"""
    try:
        dialog = page.locator( dialog_locator )
        if dialog.is_visible():
            print(f"检测到《《《打开》》》 的对话框{dialog_locator}，尝试关闭")
            '''
            close_button = dialog.locator("a.close")
            if  close_button.count() > 0:
                close_button.click()
                print("对话框关闭按钮已点击")
            else:
                # 尝试点击背景关闭
                dialog.locator("div.bjui-dialogBackground").click()
                print("对话框背景已点击")
            # 等待对话框消失
            dialog.wait_for(state="hidden", timeout=5000)
            print("对话框已关闭")
            '''
        else:
            print(f"检测到《《《关闭》》》 的对话框{dialog_locator}，尝试关闭")
    except Exception as e:
        print(f"关闭对话框时发生错误: {e}")





#######对外暴露方法
def click_element_when_ready(page: Page, selector: str, first: bool = True, timeout: int = 10000) -> bool:
    """
    异步点击指定元素，等待元素可见且启用后执行点击操作。

    Args:
        page (Page): Playwright 的页面对象。
        selector (str): 元素选择器（如 "input[name='sm_name']"）。
        first (bool): 是否只点击第一个匹配元素。默认 True。
        timeout (int): 等待超时时间（毫秒）。默认 10000ms。

    Returns:
        bool: 点击成功返回 True，失败返回 False。

    Raises:
        Logs errors and saves a screenshot on failure.
    """
    try:

        print(">>>>click_element_when_ready 1")
        # 创建定位器
        locator = page.locator(selector)

        print(">>>>click_element_when_ready 2")
        if first:
            locator = locator.first
        else:
            # 1 就是第二个
            locator = page.locator(selector).nth(1)
            print("点击第二个按钮.1>>>")
            

        print(">>>>click_element_when_ready 3{}")
        # 等待元素可见
        locator.wait_for(state="visible", timeout=timeout)
        print(f"元素 {selector} 已可见")

        print(">>>>click_element_when_ready 4")

        # 检查元素是否启用
        is_enabled = locator.is_enabled()
        if not is_enabled:
            print(f"错误: 元素 {selector} 已禁用")
            page.screenshot(path="error_screenshot_disabled.png")
            return False

        # 执行点击
        print(">>>>click_element_when_ready 5")
        locator.click(timeout=timeout)
        print(f"成功点击元素 {selector}")
        
        # 可选：保存点击后截图，便于验证
        page.screenshot(path="after_click_screenshot.png")
        print("截图已保存: after_click_screenshot.png")
        return True

    except TimeoutError:
        print(f"错误: 元素 {selector} 在 {timeout}ms 内未变得可见或可点击")
        page.screenshot(path="error_screenshot_timeout.png")
        print("截图已保存: error_screenshot_timeout.png")
        return False
    except Exception as e:
        print(f"点击元素 {selector} 时发生错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        print("截图已保存: error_screenshot_general.png")
        return False

def click_element_by_role(page: Page, role: str, name: str, first: bool = True, timeout: int = 10000) -> bool:
    """
    异步点击指定元素，等待元素可见且启用后执行点击操作。

    Args:
        page (Page): Playwright 的页面对象。
        role (str):     元素选择器（如 ""）。
        selector (str): 元素选择器（如 "input[name='sm_name']"）。
        first (bool): 是否只点击第一个匹配元素。默认 True。
        timeout (int): 等待超时时间（毫秒）。默认 10000ms。

    Returns:
        bool: 点击成功返回 True，失败返回 False。

    Raises:
        Logs errors and saves a screenshot on failure.
    """
    try:

        print(">>>>click_element_when_ready 1")
        # 创建定位器
        
        locator = page.get_by_role(role=role, name=name)

        print(">>>>click_element_when_ready 2")
        if first:
            locator = locator.first
        else:
            # 1 就是第二个
            locator = page.locator(locator).nth(1)
            print("点击第二个按钮.1>>>")
            

        print(">>>>click_element_when_ready 3{}")
        # 等待元素可见
        locator.wait_for(state="visible", timeout=timeout)
        print(f"元素   #{role}>>>{name}  已可见")

        print(">>>>click_element_when_ready 4")

        # 检查元素是否启用
        is_enabled = locator.is_enabled()
        if not is_enabled:
            print(f"错误: 元素 #{role}>>>{name}  已禁用")
            page.screenshot(path="error_screenshot_disabled.png")
            return False

        # 执行点击
        print(">>>>click_element_when_ready 5")
        locator.click(timeout=timeout)
        print(f"成功点击元素 #{role}>>>{name} ")
        
        # 可选：保存点击后截图，便于验证
        page.screenshot(path="after_click_screenshot.png")
        print("截图已保存: after_click_screenshot.png")
        return True

    except TimeoutError:
        print(f"错误: 元素 #{role}>>>{name}  在 {timeout}ms 内未变得可见或可点击")
        page.screenshot(path="error_screenshot_timeout.png")
        print("截图已保存: error_screenshot_timeout.png")
        return False
    except Exception as e:
        print(f"点击元素  #{role}>>>{name}  时发生错误: {e}")
        page.screenshot(path="error_screenshot_general.png")
        print("截图已保存: error_screenshot_general.png")
        return False
     

###
def element_Info( element ):
    is_visible = element.is_visible()
    is_enabled = element.is_enabled()
    print(f"元素{ element }可见: {is_visible}, 元素启用: {is_enabled}")

#############验证用#######################

def click_query_button( page , selector):

    ##在点击第二个按钮前，现验证一下页面的层是否打开了；

    #dialog_locator = "div.bjui-dialog-wrap"
    #close_dialog_if_open(page, dialog_locator)

    try:

        # 验证选择器
        # step1 ,现看看有几个
        #count =  page.locator(selector).count()
        #print(f"找到 {count} 个匹配按钮{selector}")

        #if count == 0:
        #    print("错误: 未找到查询按钮")
        #    page.screenshot(path="no_button_screenshot.png")
        #    return
        
        
        print("点击第二个按钮>>>")
        locatorA = page.locator(selector)
        print("点击第二个按钮.1>>>")
        #locatorA.wait_for(state="visible", timeout=20000)
        #print(f"点击第二个按钮.2>>>元素 {selector} 已可见")

        #is_enabled = locatorA.is_enabled()
        #if not is_enabled:
        #    print(f"点击第二个按钮>>>错误: 元素 {selector}  已禁用")
        
        print("点击第二个按钮>>> >>>before click =======")
        success = locatorA.click(timeout=30000)
        print(f"点击第二个按钮>>> >>>{success} =======")
    

        if success:
            print("操作完成：成功点击查询按钮")
        else:
            print("操作失败：无法点击查询按钮")

    except Exception as e:
        print(f"主程序错误: {e}")
        page.screenshot(path="main_error_screenshot.png")
        print("截图已保存: main_error_screenshot.png")
    finally:
        print("任务完成，浏览器保持打开状态")


def testSelector(page,selector):

    try:
        print(f">>\n\n需要判断的selector是：{selector}")
        locator = page.locator(selector)
        count = locator.count()
        print(f" 找到{ count }各符合条件的控件")
        # 检查元素是否可见
        is_visible = locator.isVisible()
        print(f"元素是否可见: {is_visible}")
    except:
        print(f"⚡⚡⚡ERROR ")


def printElementValue(input_element):
    try:
        value = input_element.input_value()
        print(f"    Input 文本框的值为: {value}")
    except:
        print("     >>>printElementValue ERROR ")



def check_agent_num_visibility(page):
    
    # Define the selectors for the three agent_num inputs
    
    #selectors = [
    #    'form[action="/yhbackstage/AgentInfo/applylist"] input[name="agent_num"]',
    #    'form[action="/yhbackstage/AgentInfo/firsttrial"] input[name="agent_num"]',
    #    'form[action="/yhbackstage/AgentInfo/verifylist"] input[name="agent_num"]'
    #]
    selectors = [
        'form[action="/yhbackstage/AgentInfo/applylist"] input[name="agent_name"]',
     ]

    # Check visibility and element count for each agent_num input
    for index, selector in enumerate(selectors, 1):
        try:
            # Find all elements matching the selector
            elements = page.query_selector_all(selector)
            element_count = len(elements)

            if element_count == 0:
                print(f"第 {index} 个 agent_num 控件: 未找到符合条件的元素")
            elif element_count > 1:
                print(f"第 {index} 个 agent_num 控件: 找到 {element_count} 个符合条件的元素")
                # Check visibility for each matching element
                for i, element in enumerate(elements, 1):
                    is_visible = element.is_visible()
                    print(f"  元素 {i} 是否可见: {is_visible}")
                    print(f"  元素 {i} 的值: {printElementValue(element) }")
                    
            else:
                print(f"第 {index} 个 agent_num 控件: 找到 1 个符合条件的元素")
                # Check visibility for the single matching element
                is_visible = elements[0].is_visible()
                print(f"  元素 1 是否可见: {is_visible}")
                print(f"  元素 1 是否可见: {elements[0]}")
                print(f"  元素的值: {printElementValue(elements[0]) }")

        except Exception as e:
            print(f"第 {index} 个 agent_num 控件检查失败: {str(e)}")



def run(playwright: Playwright) -> None:

    # 连接到 Chrome 调试端口
    browser = playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
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
    print(f"Page title: {page.title()}")
    print(">>Go")
    
    selctor0 = "[name='agent_status']"
                
    selector1 = "form[action=\'/yhbackstage/AgentInfo/applylist\'] input[name=\'agent_name\']"
    selector2 = 'form[action="/yhbackstage/AgentInfo/firsttrial"] input[name="agent_num"]'
    selector3 = 'form[action="/yhbackstage/AgentInfo/verifylist"] input[name="agent_num"]'

    #check_agent_num_visibility(page)

    elementCount = page.locator(selctor0).count()
    print(f"elementCount>>>{selector1}<<< \n\n     {elementCount}")

    #testSelector(page,selector1)
    #testSelector(page,selector2)
    #testSelector(page,selector1)
    '''
    print(">>44.4")
    page.locator("input[name=\"sm_name\"]").click()
    print(">>44.5")
    page.locator("input[name=\"sm_name\"]").fill("张三")

    print(">>55")
    #page.get_by_role("button", name=" 查询").nth(1).click()
    click_query_button(page=page)

    selectora = '#pagerForm button[type="submit"][data-icon="search"]'
    click_element_when_ready( page=page,
                selector=selectora,first = False )   
    print(">>5633")
    page.get_by_role("cell", name="18245636954").click()
    page.get_by_role("button", name=" 选择").click()
    '''

    #代理商性质
    #xpath = "//*[@id='myForm1']/fieldset[1]/table/tbody/tr[2]/td[1]/p[1]/div/button/span[2]"
    '''
    selector = 'button[data-id="agent_nature"][title="经销商"]'
    success = click_query_button(
        page=page,
        selector=selector
    )
    '''

    #page.get_by_role("button", name="下一步").click()

    print(">>>start")
    #success = click_element_by_role(page,"button","下一步" )
    
    #success = page.get_by_role("group", name="其他信息").locator("#haha").click()
    #print(f"》》》执行结果{success}")

if __name__ == "__main__":    
    with sync_playwright() as playwright:
        run(playwright)
