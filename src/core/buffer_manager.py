import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

#管理页面控件json
#包括，增，改，并记录调用日志。

class BufferManager:
    def __init__(self, config_dir: Path, default_profile: str = "default"):
        self.config_dir = config_dir
        self.default_profile = default_profile
        self._ensure_directory()
        print(">>> BufferManager>>>__init__")
        
    def _ensure_directory(self):
        """确保配置文件目录存在"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            logger.info(f"创建配置目录: {self.config_dir}")
            
        default_file = self.config_dir / f"{self.default_profile}.json"
        print(f">>> BufferManager>>>_ensure_directory>>>fileName{default_file}")
        if not default_file.exists():
            print(f">>> BufferManager>>>_ensure_directory>>>NOT EXIST")
            self._save_config({})

        print(">>> BufferManager>>>_ensure_directory")    

    def _get_config_path(self, profile: str = None) -> Path:
        """获取配置文件路径"""
        profile = profile or self.default_profile
        config_path = self.config_dir / f"{profile}.json"
        #print(f"_get_config_path>>>{config_path}")
        return config_path

    def _load_config(self, profile: str = None) -> Dict:
        """加载配置文件"""
        config_path = self._get_config_path(profile)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_config(self, config: Dict, profile: str = None):
        """保存配置文件"""
        config_path = self._get_config_path(profile)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def list_elements(self, profile: str = None) -> List[Dict]:
        """列出所有元素配置"""
        return self._load_config(profile).get('elements', [])

    #根据元素名称，获得element
    def get_element(self, element_name: str, profile: str = None) -> Dict:
        """获取单个元素配置"""
        elements = self._load_config(profile).get('elements', {})

        for element in elements:
            #print(f" compare::{element.get("name")} vs {arg}")
            if element.get("name") == element_name:
                #print(json.dumps(element, indent=2))
                return element
        print(f"元素 '{element_name}' 在缓存中不存在")
        return json.dumps({})

    def batch_update(self, elements: List[Dict], profile: str = None):
        """批量更新元素配置"""
        config = self._load_config(profile)
        current_elements = config.get('elements', {})
        
        for elem in elements:
            existing = current_elements.get(elem['element_name'], {})
            current_elements[elem['element_name']] = {
                **existing,
                **elem,
                "last_updated": datetime.now().isoformat(),
                "success_count": existing.get("success_count", 0)
            }
        
        config['elements'] = current_elements
        self._save_config(config, profile)
        logger.info(f"已更新{len(elements)}个元素配置")

    def record_success(self, element_name: str, profile: str = None):
        """记录成功操作"""
        print(f"record_success>>profile")
        config = self._load_config(profile)
        elements = config['elements']
        print( f"element length::{len(elements)}" )
        
        for element in elements:
            if element["name"] == element_name:
                try:
                    element["success_count"] = int(element["success_count"]) + 1
                    element['last_used'] = datetime.now().isoformat()
                    print(f"已将 {element_name} 的 success_count 增加到 {element['success_count']}")
                except ValueError:
                    print(f"错误: {element_name} 的 success_count 不是有效的整数。")
            
        #写到文件中
        self._save_config(config, profile)

    def manual_update(self, element_name: str, updates: Dict, profile: str = None):
        """手动更新元素配置"""
        config = self._load_config(profile)
        if element_name in config['elements']:
            config['elements'][element_name].update(updates)
            self._save_config(config, profile)
            logger.info(f"已手动更新 {element_name} 配置")