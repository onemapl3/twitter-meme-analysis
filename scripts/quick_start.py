#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
提供一键式的环境检查和设置
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuickStart:
    """快速启动管理器"""
    
    def __init__(self):
        """初始化快速启动管理器"""
        self.current_step = 0
        self.total_steps = 6
        
    def print_header(self):
        """打印启动头部信息"""
        print("=" * 60)
        print("🚀 Twitter Meme分析系统 - 快速启动")
        print("=" * 60)
        print("本脚本将帮助您快速设置和配置系统环境")
        print("=" * 60)
    
    def print_step(self, step_name: str):
        """打印当前步骤"""
        self.current_step += 1
        print(f"\n📋 步骤 {self.current_step}/{self.total_steps}: {step_name}")
        print("-" * 40)
    
    def check_python_version(self):
        """检查Python版本"""
        self.print_step("检查Python环境")
        
        python_version = sys.version_info
        print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python版本过低，需要Python 3.8+")
            return False
        
        print("✅ Python版本符合要求")
        return True
    
    def check_dependencies(self):
        """检查依赖包"""
        self.print_step("检查依赖包")
        
        required_packages = [
            'psycopg2', 'pandas', 'numpy', 'requests', 'schedule'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - 未安装")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️  缺少以下依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements_twitter.txt")
            return False
        
        print("✅ 所有依赖包已安装")
        return True
    
    def check_config_files(self):
        """检查配置文件"""
        self.print_step("检查配置文件")
        
        config_files = [
            'collector_config.json',
            'env_example.txt'
        ]
        
        missing_files = []
        
        for file_path in config_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - 未找到")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"\n⚠️  缺少配置文件: {', '.join(missing_files)}")
            return False
        
        print("✅ 配置文件检查完成")
        return True
    
    def check_data_files(self):
        """检查数据文件"""
        self.print_step("检查数据文件")
        
        data_files = [
            'data/raw/sample_tweets.csv',
            'data/raw/sample_followings.csv',
            'data/processed/enhanced_kol_profiles.json'
        ]
        
        missing_files = []
        
        for file_path in data_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"✅ {file_path} ({file_size:.1f} MB)")
            else:
                print(f"❌ {file_path} - 未找到")
                missing_files.append(file_path)
        
        if missing_files:
            print(f"\n⚠️  缺少数据文件: {', '.join(missing_files)}")
            return False
        
        print("✅ 数据文件检查完成")
        return True
    
    def setup_database(self):
        """设置数据库"""
        self.print_step("设置PostgreSQL数据库")
        
        print("请确保PostgreSQL服务正在运行")
        print("然后运行以下命令设置数据库:")
        print("\n1. 修改collector_config.json中的数据库密码")
        print("2. 运行: python setup_database.py")
        print("3. 运行: python test_database_connection.py")
        
        # 询问用户是否已设置数据库
        response = input("\n数据库是否已设置完成？(y/n): ").lower().strip()
        
        if response in ['y', 'yes', '是']:
            print("✅ 数据库设置完成")
            return True
        else:
            print("⚠️  请先完成数据库设置")
            return False
    
    def configure_twitter_api(self):
        """配置Twitter API"""
        self.print_step("配置Twitter API")
        
        print("请按以下步骤配置Twitter API:")
        print("\n1. 访问 https://developer.twitter.com/")
        print("2. 创建应用并获取Bearer Token")
        print("3. 将Token添加到collector_config.json")
        print("4. 运行: python test_twitter_api.py")
        
        # 询问用户是否已配置API
        response = input("\nTwitter API是否已配置完成？(y/n): ").lower().strip()
        
        if response in ['y', 'yes', '是']:
            print("✅ Twitter API配置完成")
            return True
        else:
            print("⚠️  请先完成Twitter API配置")
            return False
    
    def run_integration_test(self):
        """运行集成测试"""
        self.print_step("运行集成测试")
        
        print("现在运行数据管道集成测试...")
        
        try:
            # 运行数据迁移
            result = subprocess.run([sys.executable, 'data_pipeline_integration.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 数据管道集成测试成功")
                return True
            else:
                print("❌ 数据管道集成测试失败")
                print("错误输出:", result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ 运行集成测试时发生错误: {e}")
            return False
    
    def print_next_steps(self):
        """打印下一步操作"""
        print("\n" + "=" * 60)
        print("🎉 快速启动完成！")
        print("=" * 60)
        
        print("\n📋 下一步操作:")
        print("1. 启动Web界面: python meme_api_server.py")
        print("2. 运行数据采集: python twitter_scheduler.py")
        print("3. 查看分析结果: 访问 http://localhost:5000")
        
        print("\n📚 相关文档:")
        print("- README_Twitter_Collector.md: Twitter采集系统说明")
        print("- README_API.md: API接口说明")
        print("- README.md: 系统总体说明")
        
        print("\n🔧 故障排除:")
        print("- 检查PostgreSQL服务状态")
        print("- 验证Twitter API Token")
        print("- 查看日志文件: twitter_collector.log")
        
        print("\n💡 提示:")
        print("- 首次运行建议使用小规模数据测试")
        print("- 定期备份数据库数据")
        print("- 监控系统资源使用情况")
    
    def run(self):
        """运行快速启动流程"""
        self.print_header()
        
        steps = [
            ("检查Python环境", self.check_python_version),
            ("检查依赖包", self.check_dependencies),
            ("检查配置文件", self.check_config_files),
            ("检查数据文件", self.check_data_files),
            ("设置数据库", self.setup_database),
            ("配置Twitter API", self.configure_twitter_api)
        ]
        
        all_passed = True
        
        for step_name, step_func in steps:
            if not step_func():
                all_passed = False
                print(f"\n❌ 步骤 '{step_name}' 失败，请解决问题后重新运行")
                break
        
        if all_passed:
            print("\n✅ 所有检查通过！现在运行集成测试...")
            
            if self.run_integration_test():
                self.print_next_steps()
            else:
                print("\n❌ 集成测试失败，请检查错误信息")
        else:
            print("\n⚠️  环境检查未完全通过，请解决上述问题后重新运行")

def main():
    """主函数"""
    try:
        quick_start = QuickStart()
        quick_start.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 快速启动过程中发生错误: {e}")
        logger.error(f"快速启动错误: {e}")

if __name__ == "__main__":
    main()
