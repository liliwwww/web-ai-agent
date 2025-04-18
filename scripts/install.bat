@echo off
REM 鏂囦欢鍚嶏細install.bat
echo 姝ｅ湪瀹夎Python渚濊禆...
pip install -r requirements.txt
if errorlevel 1 (
    echo 渚濊禆瀹夎澶辫触锛岃妫€鏌ython鐜
    exit /b 1
)

echo 瀹夎Playwright娴忚鍣?..
playwright install
playwright install-deps

echo 鍒濆鍖栨祴璇?..
python -m pytest src\tests\ -v

if not exist ".env" (
    copy .env.example .env
    echo 璇风紪杈?env鏂囦欢閰嶇疆API瀵嗛挜鍜岀綉绔橴RL
)
