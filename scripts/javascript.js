// 调试时，在chrome调试控制台测试用脚本；

inputs = document.querySelectorAll("[name='agent_status']");
length( inputs)

// 获取所有 name="agent_num" 的 input 控件
const inputs = document.querySelectorAll("select[name='agent_status']");

// 遍历每个 input 控件
inputs.forEach((input, index) => {
    // 获取当前 input 控件的父元素
    const parentElement = input.parentNode;

    if (parentElement) {
        // 打印父元素的 HTML 内容
        console.log(`第 ${index + 1} 个 input 控件的上级标签 HTML:`);
        console.log(parentElement.outerHTML);
    } else {
        console.log(`第 ${index + 1} 个 input 控件没有上级标签。`);
    }

    // 判断元素是否可见
    const isVisible = (function () {
        // 检查 offsetParent 是否为 null
        if (input.offsetParent === null) {
            return false;
        }
        // 检查元素的矩形区域是否有尺寸
        const rect = input.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    })();

    console.log(`第 ${index + 1} 个 input 控件是3否可见: ${isVisible}`);
});


//测试 update  特别好

// 定位 select 元素
const selectElement = document.querySelector('select[name="agent_status"]');

if (selectElement) {
    // 遍历 select 下的所有 option 元素
    for (let i = 0; i < selectElement.options.length; i++) {
        const option = selectElement.options[i];
        // 检查 option 的文本内容是否为 '已驳回'
        if (option.textContent === '已驳回') {
            // 选中该 option
            option.selected = true;
            break;
        }
    }
    // 触发 change 事件，模拟用户选择操作
    const event = new Event('change', { bubbles: true });
    selectElement.dispatchEvent(event);
} else {
    console.log('未找到符合条件的 select 元素');
}






//###########################


const selectElement = document.querySelector('select#agent_nature');
const targetValue = '4';

// 查找目标选项并选中
for (let i = 0; i < selectElement.options.length; i++) {
    const option = selectElement.options[i];
    if (option.value === targetValue) {
        option.selected = true;
        break;
    }
}

// 触发 change 事件
const event = new Event('change', { bubbles: true });
selectElement.dispatchEvent(event);