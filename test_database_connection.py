#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本
用于验证PostgreSQL连接和表结构
"""

import psycopg2
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_database_connection():
    """测试数据库连接"""
    
    try:
        # 读取配置
        with open('collector_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        db_config = config['database']
        
        print("🔍 测试数据库连接...")
        print(f"主机: {db_config['host']}")
        print(f"端口: {db_config['port']}")
        print(f"数据库: {db_config['database']}")
        print(f"用户: {db_config['user']}")
        
        # 测试连接
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        
        # 测试基本查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ 数据库连接成功！")
        print(f"PostgreSQL版本: {version[0]}")
        
        # 检查表结构
        print("\n🔍 检查表结构...")
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("✅ 发现以下表:")
            for table in tables:
                print(f"  - {table[0]} ({table[1]})")
        else:
            print("⚠️  未发现任何表")
        
        # 检查索引
        print("\n🔍 检查索引...")
        cursor.execute("""
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            print("✅ 发现以下索引:")
            for index in indexes:
                print(f"  - {index[0]} (表: {index[1]})")
        else:
            print("⚠️  未发现任何索引")
        
        # 测试数据插入（可选）
        print("\n🔍 测试数据插入...")
        try:
            # 插入测试日志
            cursor.execute("""
                INSERT INTO collection_logs (task_name, execution_time, tweets_collected, users_updated, status)
                VALUES (%s, %s, %s, %s, %s)
            """, ('test_connection', 0.1, 0, 0, 'success'))
            
            conn.commit()
            print("✅ 测试数据插入成功")
            
            # 清理测试数据
            cursor.execute("DELETE FROM collection_logs WHERE task_name = 'test_connection'")
            conn.commit()
            print("✅ 测试数据清理成功")
            
        except Exception as e:
            print(f"⚠️  数据插入测试失败: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 数据库连接测试完成！")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n可能的解决方案:")
        print("1. 检查PostgreSQL服务是否运行")
        print("2. 检查数据库配置是否正确")
        print("3. 运行 setup_database.py 创建数据库")
        return False
        
    except FileNotFoundError:
        print("❌ 未找到 collector_config.json 配置文件")
        return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False

def check_table_data():
    """检查表中的数据"""
    
    try:
        with open('collector_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        db_config = config['database']
        
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        
        print("\n📊 检查表数据...")
        
        # 检查各表的记录数
        tables = ['tweets', 'kol_users', 'meme_analysis', 'collection_logs']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  - {table}: {count} 条记录")
            except Exception as e:
                print(f"  - {table}: 查询失败 ({e})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查表数据失败: {e}")

if __name__ == "__main__":
    print("🚀 开始数据库连接测试...\n")
    
    success = test_database_connection()
    
    if success:
        check_table_data()
        print("\n✅ 所有测试通过！数据库已准备就绪。")
        print("\n下一步操作：")
        print("1. 配置Twitter API Bearer Token")
        print("2. 运行数据采集测试")
    else:
        print("\n❌ 测试失败，请检查配置和数据库状态。")
