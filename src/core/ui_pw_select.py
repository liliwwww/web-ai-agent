
from playwright.sync_api import Playwright, sync_playwright, Page,  expect


#对select操作进行封装

def select_option_and_verify(page: Page, select_selector: str, target_text: str) -> bool:
    """
    Selects an option in a <select> or selectpicker by text and verifies the selected value.
    
    Args:
        page: Playwright Page object.
        select_selector: CSS selector for the <select> element (e.g., 'select[name="agent_status"]').
        target_text: Text of the option to select (e.g., '已驳回').
    
    Returns:
        bool: True if the select's current value matches the target option's value, False otherwise.
    """
    try:
        # Wait for select element
        page.wait_for_selector(select_selector, state="attached", timeout=10000)
        print(f"Found select element: {select_selector}")

        # Check if native select is visible
        is_select_visible = page.eval_on_selector(
            select_selector, 'el => window.getComputedStyle(el).display !== "none"'
        )
        print(f"Is native select visible: {is_select_visible}")

        # Find the value for the option with target_text
        options = page.query_selector_all(f"{select_selector} option")
        target_value = None
        for option in options:
            text = option.text_content().strip()
            if text == target_text:
                target_value = option.get_attribute('value')
                print(f"Found option with text '{target_text}' and value '{target_value}'")
                break

        if not target_value:
            print(f"No option with text '{target_text}' found")
            for option in options:
                text = option.text_content().strip()
                value = option.get_attribute('value')
                print(f"Option: text='{text}', value='{value}'")
            return False

        # Select the option
        if is_select_visible:
            # Native select
            page.select_option(select_selector, value=target_value)
            print(f"Selected '{target_text}' using native select")
        else:
            # Selectpicker
            select_id = page.eval_on_selector(select_selector, 'el => el.id')
            button_selector = f'div.bootstrap-select button[data-id="{select_id}"]'
            option_selector = f'//div[contains(@class, "bootstrap-select")]//a[span[text()="{target_text}"]]'

            page.wait_for_selector(button_selector, state="visible", timeout=5000)
            page.click(button_selector)
            print("Opened selectpicker dropdown")

            page.wait_for_selector(option_selector, state="visible", timeout=5000)
            page.click(option_selector)
            print(f"Selected '{target_text}' from selectpicker dropdown")

            # Sync native select
            page.evaluate(
                """
                (args) => {
                    const select = document.querySelector(args.select_selector);
                    select.value = args.value;
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                }
                """,
                {"select_selector": select_selector, "value": target_value}
            )

        # Verify the selected value
        current_value = page.eval_on_selector(select_selector, 'el => el.value')
        print(f"Current select value: '{current_value}', Expected value: '{target_value}'")
        return current_value == target_value

    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    

# Example usage
if __name__ == "__main__":
    

    with sync_playwright() as p:
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
        print(f"Page title: {page.title()}")
        print(">>Go")

        # Test the function
        selector = 'select[name="agent_status"]'
        text = '已驳回'
        success = select_option_and_verify(page, selector, text)
        print(f"Selection verified: {success}")

        input("Press Enter to close the browser...")
        