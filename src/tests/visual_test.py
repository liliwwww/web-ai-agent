# tests/visual_test.py
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
import cv2
import numpy as np

BASE_DIR = Path(__file__).parent
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
BASELINE_DIR = SCREENSHOTS_DIR / "baseline"
ACTUAL_DIR = SCREENSHOTS_DIR / "actual"
DIFF_DIR = SCREENSHOTS_DIR / "diff"

# 初始化目录
for d in [BASELINE_DIR, ACTUAL_DIR, DIFF_DIR]:
    d.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

def compare_images(baseline, actual, diff, threshold=5):
    """使用OpenCV进行图像差异比较"""
    img1 = cv2.imread(str(baseline))
    img2 = cv2.imread(str(actual))
    
    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # 计算结构相似性
    (score, diff) = cv2.compareSSIM(gray1, gray2, full=True)
    diff = (diff * 255).astype("uint8")
    
    # 保存差异图
    cv2.imwrite(str(diff), diff)
    
    # 验证相似度
    assert score >= threshold/100, f"视觉差异过大，相似度仅{score:.2f}"

def test_homepage_visual(page, request):
    """主页视觉回归测试"""
    test_name = request.node.name
    page.goto("https://your-website.com")
    
    # 截图配置
    baseline = BASELINE_DIR / f"{test_name}.png"
    actual = ACTUAL_DIR / f"{test_name}.png"
    diff = DIFF_DIR / f"{test_name}.png"

    # 获取截图
    page.screenshot(path=actual)
    
    if not baseline.exists():
        actual.rename(baseline)
        pytest.skip(f"创建基线截图: {baseline}")
    
    # 对比截图
    compare_images(baseline, actual, diff, threshold=95)
    
    # 附加截图到报告
    if hasattr(request.config, "_html"):
        request.config._html.add_image(str(actual))
        request.config._html.add_image(str(diff)))

# conftest.py配置（需要单独创建）
"""
# tests/conftest.py
def pytest_html_report_title(report):
    report.title = "视觉测试报告"

def pytest_configure(config):
    config._html = None  # 初始化HTML报告插件
"""
