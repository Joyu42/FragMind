"""
应用配置管理模块
管理 API keys、数据库路径等配置信息
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """应用配置类"""
    
    # 项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    
    # LLM API 配置
    # 优先从环境变量读取，后续代码会从 QSettings 读取覆盖
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    @classmethod
    def get_api_key(cls):
        """获取 API Key，优先从 QSettings 读取"""
        from PyQt6.QtCore import QSettings
        settings = QSettings("FragMind", "AppConfig")
        key = settings.value("api_key", "")
        return key if key else cls.DEEPSEEK_API_KEY
    
    # 数据库配置
    DATABASE_PATH =  "data/fragmind.db"
    DATABASE_FULL_PATH = BASE_DIR / DATABASE_PATH
    
    # 确保数据目录存在
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        cls.DATABASE_FULL_PATH.parent.mkdir(parents=True, exist_ok=True)
    


# 初始化配置
Config.ensure_directories()
