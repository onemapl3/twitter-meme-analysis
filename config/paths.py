#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目路径配置文件
统一管理项目中的各种路径，避免硬编码
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 源代码目录
SRC_DIR = PROJECT_ROOT / "src"
CORE_DIR = SRC_DIR / "core"
WEB_DIR = SRC_DIR / "web"
DATA_COLLECTION_DIR = SRC_DIR / "data_collection"
VISUALIZATION_DIR = SRC_DIR / "visualization"
UTILS_DIR = SRC_DIR / "utils"

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INTERMEDIATE_DATA_DIR = DATA_DIR / "intermediate"

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = OUTPUT_DIR / "logs"

# 配置文件目录
CONFIG_DIR = PROJECT_ROOT / "config"

# 文档目录
DOCS_DIR = PROJECT_ROOT / "docs"

# 脚本目录
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# 测试目录
TESTS_DIR = PROJECT_ROOT / "tests"

# 确保所有必要的目录都存在
REQUIRED_DIRS = [
    RAW_DATA_DIR, PROCESSED_DATA_DIR, INTERMEDIATE_DATA_DIR,
    CHARTS_DIR, REPORTS_DIR, LOGS_DIR
]

def ensure_directories():
    """确保所有必要的目录都存在"""
    for dir_path in REQUIRED_DIRS:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ 确保目录存在: {dir_path}")

def get_data_file_path(filename: str, data_type: str = "processed") -> Path:
    """获取数据文件路径
    
    Args:
        filename: 文件名
        data_type: 数据类型 ("raw", "processed", "intermediate")
    
    Returns:
        完整的文件路径
    """
    if data_type == "raw":
        return RAW_DATA_DIR / filename
    elif data_type == "processed":
        return PROCESSED_DATA_DIR / filename
    elif data_type == "intermediate":
        return INTERMEDIATE_DATA_DIR / filename
    else:
        raise ValueError(f"未知的数据类型: {data_type}")

def get_output_file_path(filename: str, output_type: str = "charts") -> Path:
    """获取输出文件路径
    
    Args:
        filename: 文件名
        output_type: 输出类型 ("charts", "reports", "logs")
    
    Returns:
        完整的文件路径
    """
    if output_type == "charts":
        return CHARTS_DIR / filename
    elif output_type == "reports":
        return REPORTS_DIR / filename
    elif output_type == "logs":
        return LOGS_DIR / filename
    else:
        raise ValueError(f"未知的输出类型: {output_type}")

def get_config_file_path(filename: str) -> Path:
    """获取配置文件路径
    
    Args:
        filename: 配置文件名
    
    Returns:
        完整的配置文件路径
    """
    return CONFIG_DIR / filename

# 常用文件路径
KOL_PROFILES_FILE = get_data_file_path("enhanced_kol_profiles.json", "processed")
MEME_DETECTION_FILE = get_data_file_path("enhanced_meme_detection_results.json", "processed")
KOL_ANALYSIS_FILE = get_data_file_path("kol_analysis_results.json", "processed")
TWEETS_FILE = get_data_file_path("sample_tweets.csv", "raw")
FOLLOWINGS_FILE = get_data_file_path("sample_followings.csv", "raw")

if __name__ == "__main__":
    print("🔍 项目路径配置检查...")
    ensure_directories()
    
    print("\n📁 主要目录路径:")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"源代码目录: {SRC_DIR}")
    print(f"数据目录: {DATA_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"配置目录: {CONFIG_DIR}")
    
    print("\n📊 常用文件路径:")
    print(f"KOL档案: {KOL_PROFILES_FILE}")
    print(f"Meme检测结果: {MEME_DETECTION_FILE}")
    print(f"推文数据: {TWEETS_FILE}")
    print(f"关注关系: {FOLLOWINGS_FILE}")
    
    print("\n✅ 路径配置检查完成！")
