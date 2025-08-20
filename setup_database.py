#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库设置脚本
用于创建PostgreSQL数据库、用户和表结构
"""

import psycopg2
import logging
import json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_and_tables():
    """创建数据库和表结构"""
    
    # 读取配置
    try:
        with open('collector_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error("未找到collector_config.json文件")
        return False
    
    db_config = config['database']
    
    # 连接到PostgreSQL服务器（默认postgres数据库）
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database='postgres',
            user='postgres',  # 使用默认超级用户
            password='postgres'  # 默认密码，请根据实际情况修改
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        logger.info("成功连接到PostgreSQL服务器")
        
        # 创建数据库
        db_name = db_config['database']
        try:
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"成功创建数据库: {db_name}")
        except psycopg2.errors.DuplicateDatabase:
            logger.info(f"数据库 {db_name} 已存在")
        
        # 创建用户
        try:
            cursor.execute(f"CREATE USER {db_config['user']} WITH PASSWORD '{db_config['password']}'")
            logger.info(f"成功创建用户: {db_config['user']}")
        except psycopg2.errors.DuplicateObject:
            logger.info(f"用户 {db_config['user']} 已存在")
        
        # 授予权限
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_config['user']}")
        logger.info(f"成功授予用户 {db_config['user']} 对数据库 {db_name} 的所有权限")
        
        cursor.close()
        conn.close()
        
        # 连接到新创建的数据库
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_name,
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        # 创建表结构
        create_tables(cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("数据库设置完成！")
        return True
        
    except Exception as e:
        logger.error(f"数据库设置失败: {e}")
        return False

def create_tables(cursor):
    """创建表结构"""
    
    # 推文表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id SERIAL PRIMARY KEY,
            tweet_id VARCHAR(50) UNIQUE NOT NULL,
            text TEXT NOT NULL,
            user_id VARCHAR(50) NOT NULL,
            username VARCHAR(100),
            created_at TIMESTAMP,
            retweet_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            quote_count INTEGER DEFAULT 0,
            is_retweet BOOLEAN DEFAULT FALSE,
            is_quote BOOLEAN DEFAULT FALSE,
            hashtags TEXT[],
            mentions TEXT[],
            urls TEXT[],
            media_urls TEXT[],
            language VARCHAR(10),
            engagement_metrics JSONB,
            meme_mentions TEXT[],
            collected_at TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("创建推文表成功")
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_user_id ON tweets(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_meme_mentions ON tweets USING GIN(meme_mentions)")
    
    # KOL用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kol_users (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) UNIQUE NOT NULL,
            username VARCHAR(100) NOT NULL,
            display_name VARCHAR(200),
            description TEXT,
            followers_count INTEGER DEFAULT 0,
            following_count INTEGER DEFAULT 0,
            tweet_count INTEGER DEFAULT 0,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP,
            profile_image_url TEXT,
            is_kol BOOLEAN DEFAULT TRUE,
            kol_score FLOAT DEFAULT 0.0,
            kol_tier VARCHAR(20) DEFAULT 'Tier 4',
            profile_data JSONB,
            last_updated TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("创建KOL用户表成功")
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kol_users_username ON kol_users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_kol_users_kol_score ON kol_users(kol_score)")
    
    # Meme分析结果表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meme_analysis (
            id SERIAL PRIMARY KEY,
            meme_name VARCHAR(100) NOT NULL,
            analysis_date DATE NOT NULL,
            score FLOAT DEFAULT 0.0,
            mention_count INTEGER DEFAULT 0,
            engagement_total INTEGER DEFAULT 0,
            kol_mentions JSONB,
            trend_data JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(meme_name, analysis_date)
        )
    """)
    logger.info("创建Meme分析结果表成功")
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meme_analysis_date ON meme_analysis(analysis_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meme_analysis_score ON meme_analysis(score)")
    
    # 数据采集日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collection_logs (
            id SERIAL PRIMARY KEY,
            task_name VARCHAR(100) NOT NULL,
            execution_time FLOAT,
            tweets_collected INTEGER DEFAULT 0,
            users_updated INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT NOW()
        )
    """)
    logger.info("创建数据采集日志表成功")

if __name__ == "__main__":
    print("开始设置数据库...")
    success = create_database_and_tables()
    if success:
        print("✅ 数据库设置完成！")
        print("\n下一步操作：")
        print("1. 修改collector_config.json中的数据库密码")
        print("2. 配置Twitter API Bearer Token")
        print("3. 运行测试脚本验证连接")
    else:
        print("❌ 数据库设置失败，请检查错误日志")
