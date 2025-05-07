import os
import json
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path
from typing import List, Dict





# 获取 src 目录的绝对路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', ''))

print(f"src::{src_path}")
# 将 src 目录添加到系统路径中
sys.path.append(src_path)



from core.buffer_manager import BufferManager


# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

buffer = BufferManager(
    config_dir=Path(os.getenv("CONFIG_DIR")),
    default_profile="default"
)


buffer.record_success('业务员查询按钮（销售）')