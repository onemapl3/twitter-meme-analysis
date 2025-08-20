#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter API测试脚本
用于验证Twitter API连接和数据获取功能
"""

import requests
import json
import logging
import time
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterAPITester:
    """Twitter API测试器"""
    
    def __init__(self, config_file='collector_config.json'):
        """初始化测试器"""
        self.config = self._load_config(config_file)
        self.api_config = self.config['twitter_api']
        self.base_url = self.api_config['base_url']
        self.bearer_token = self.api_config['bearer_token']
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
    
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件 {config_file} 未找到")
            raise
    
    def test_api_connection(self):
        """测试API连接"""
        print("🔍 测试Twitter API连接...")
        
        if self.bearer_token == "YOUR_BEARER_TOKEN_HERE":
            print("❌ Bearer Token未配置，请先配置有效的Token")
            return False
        
        try:
            # 测试用户查询API
            test_username = "elonmusk"
            url = f"{self.base_url}/users/by/username/{test_username}"
            
            print(f"测试URL: {url}")
            print(f"Bearer Token: {self.bearer_token[:20]}...")
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API连接成功！")
                print(f"用户信息: {data}")
                return True
            elif response.status_code == 401:
                print("❌ API认证失败，请检查Bearer Token")
                return False
            elif response.status_code == 429:
                print("⚠️  API速率限制，请稍后重试")
                return False
            else:
                print(f"❌ API请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API连接测试失败: {e}")
            return False
    
    def test_user_search(self):
        """测试用户搜索功能"""
        print("\n🔍 测试用户搜索功能...")
        
        try:
            # 搜索包含"crypto"的用户
            query = "crypto"
            url = f"{self.base_url}/users/search"
            params = {
                'query': query,
                'max_results': 5
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 用户搜索成功！")
                print(f"找到 {len(data.get('data', []))} 个用户")
                
                for user in data.get('data', [])[:3]:
                    print(f"  - {user.get('username')}: {user.get('name')}")
                return True
            else:
                print(f"❌ 用户搜索失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 用户搜索测试失败: {e}")
            return False
    
    def test_tweet_search(self):
        """测试推文搜索功能"""
        print("\n🔍 测试推文搜索功能...")
        
        try:
            # 搜索包含"doge"的推文
            query = "doge"
            url = f"{self.base_url}/tweets/search/recent"
            params = {
                'query': query,
                'max_results': 5,
                'tweet.fields': 'created_at,public_metrics,author_id'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 推文搜索成功！")
                print(f"找到 {len(data.get('data', []))} 条推文")
                
                for tweet in data.get('data', [])[:3]:
                    print(f"  - ID: {tweet.get('id')}")
                    print(f"    文本: {tweet.get('text')[:100]}...")
                    print(f"    时间: {tweet.get('created_at')}")
                return True
            else:
                print(f"❌ 推文搜索失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 推文搜索测试失败: {e}")
            return False
    
    def test_rate_limits(self):
        """测试速率限制"""
        print("\n🔍 测试API速率限制...")
        
        try:
            # 连续发送多个请求测试速率限制
            test_count = 3
            success_count = 0
            
            for i in range(test_count):
                url = f"{self.base_url}/users/by/username/elonmusk"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"  请求 {i+1}: 成功")
                elif response.status_code == 429:
                    print(f"  请求 {i+1}: 速率限制")
                    break
                else:
                    print(f"  请求 {i+1}: 失败 ({response.status_code})")
                
                time.sleep(0.1)  # 短暂延迟
            
            print(f"✅ 速率限制测试完成，成功请求: {success_count}/{test_count}")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 速率限制测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Twitter API功能测试...\n")
        
        tests = [
            ("API连接测试", self.test_api_connection),
            ("用户搜索测试", self.test_user_search),
            ("推文搜索测试", self.test_tweet_search),
            ("速率限制测试", self.test_rate_limits)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} 执行异常: {e}")
                results.append((test_name, False))
        
        # 输出测试结果摘要
        print("\n📊 测试结果摘要:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{len(results)} 个测试通过")
        
        if passed == len(results):
            print("\n🎉 所有测试通过！Twitter API配置正确。")
            print("\n下一步操作：")
            print("1. 运行数据采集测试")
            print("2. 集成到现有系统")
        else:
            print("\n⚠️  部分测试失败，请检查配置。")
        
        return passed == len(results)

def main():
    """主函数"""
    try:
        tester = TwitterAPITester()
        tester.run_all_tests()
    except Exception as e:
        print(f"❌ 测试器初始化失败: {e}")
        print("请检查配置文件是否正确")

if __name__ == "__main__":
    main()
