#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter数据采集器 - 小范围数据采集系统
实现智能数据筛选、去重和PostgreSQL存储
"""

import os
import json
import time
import logging
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import requests
from dataclasses import dataclass, asdict
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TweetData:
    """推文数据结构"""
    tweet_id: str
    text: str
    user_id: str
    username: str
    created_at: str
    retweet_count: int
    like_count: int
    reply_count: int
    quote_count: int
    is_retweet: bool
    is_quote: bool
    hashtags: List[str]
    mentions: List[str]
    urls: List[str]
    media_urls: List[str]
    language: str
    collected_at: str

@dataclass
class UserData:
    """用户数据结构"""
    user_id: str
    username: str
    display_name: str
    description: str
    followers_count: int
    following_count: int
    tweet_count: int
    verified: bool
    created_at: str
    profile_image_url: str
    is_kol: bool
    kol_score: float
    kol_tier: str
    collected_at: str

class TwitterDataCollector:
    """Twitter数据采集器"""
    
    def __init__(self, config_file: str = 'collector_config.json'):
        """初始化采集器"""
        self.config = self._load_config(config_file)
        self.db_conn = None
        self.session = requests.Session()
        self.setup_database()
        
    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "twitter_data",
                    "user": "postgres",
                    "password": "password"
                },
                "twitter_api": {
                    "bearer_token": "YOUR_BEARER_TOKEN",
                    "base_url": "https://api.twitter.com/2",
                    "rate_limit": 450,
                    "rate_limit_window": 900
                },
                "collection": {
                    "max_tweets_per_run": 5000,
                    "max_users_per_run": 1000,
                    "time_window_hours": 24,
                    "kol_priority": True,
                    "meme_keywords": ["doge", "shib", "pepe", "moon", "pump", "fomo"]
                }
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logger.info(f"已创建默认配置文件: {config_file}")
            return default_config
    
    def setup_database(self):
        """设置PostgreSQL数据库"""
        try:
            self.db_conn = psycopg2.connect(**self.config['database'])
            self._create_tables()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def _create_tables(self):
        """创建数据表"""
        with self.db_conn.cursor() as cursor:
            # 创建推文表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id SERIAL PRIMARY KEY,
                    tweet_id VARCHAR(50) UNIQUE NOT NULL,
                    text TEXT NOT NULL,
                    user_id VARCHAR(50) NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    retweet_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    quote_count INTEGER DEFAULT 0,
                    is_retweet BOOLEAN DEFAULT FALSE,
                    is_quote BOOLEAN DEFAULT FALSE,
                    hashtags JSONB,
                    mentions JSONB,
                    urls JSONB,
                    media_urls JSONB,
                    language VARCHAR(10),
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_hash VARCHAR(64) UNIQUE
                )
            """)
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
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
                    is_kol BOOLEAN DEFAULT FALSE,
                    kol_score FLOAT DEFAULT 0.0,
                    kol_tier VARCHAR(20),
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_user_id ON tweets(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_hashtags ON tweets USING GIN(hashtags)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_kol ON users(is_kol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_kol_score ON users(kol_score)")
            
            self.db_conn.commit()
            logger.info("数据库表创建完成")
    
    def collect_kol_tweets(self, kol_users: List[str]) -> Tuple[int, int]:
        """采集KOL推文数据"""
        logger.info(f"开始采集KOL推文，目标用户数: {len(kol_users)}")
        
        total_tweets = 0
        total_users = 0
        
        for user_id in kol_users:
            try:
                tweets = self._fetch_user_tweets(user_id)
                if tweets:
                    saved_count = self._save_tweets(tweets)
                    total_tweets += saved_count
                    logger.info(f"用户 {user_id} 采集到 {len(tweets)} 条推文，保存 {saved_count} 条")
                
                # 更新用户信息
                user_info = self._fetch_user_info(user_id)
                if user_info:
                    self._save_user(user_info)
                    total_users += 1
                
                # 速率限制控制
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"采集用户 {user_id} 数据失败: {e}")
                continue
        
        logger.info(f"KOL推文采集完成，总计: {total_tweets} 条推文，{total_users} 个用户")
        return total_tweets, total_users
    
    def _fetch_user_tweets(self, user_id: str) -> List[TweetData]:
        """获取用户推文"""
        try:
            # 这里应该使用Twitter API，现在用模拟数据
            # 实际实现时需要替换为真实的API调用
            return self._generate_mock_tweets(user_id)
        except Exception as e:
            logger.error(f"获取用户推文失败: {e}")
            return []
    
    def _fetch_user_info(self, user_id: str) -> Optional[UserData]:
        """获取用户信息"""
        try:
            # 这里应该使用Twitter API，现在用模拟数据
            return self._generate_mock_user(user_id)
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def _generate_mock_tweets(self, user_id: str) -> List[TweetData]:
        """生成模拟推文数据（用于测试）"""
        tweets = []
        base_time = datetime.now() - timedelta(hours=24)
        
        for i in range(5):  # 每个用户生成5条推文
            tweet_time = base_time + timedelta(hours=i*4)
            tweet_data = TweetData(
                tweet_id=f"{user_id}_{i}_{int(time.time())}",
                text=f"这是用户 {user_id} 的第 {i+1} 条推文 #测试 #meme",
                user_id=user_id,
                username=f"user_{user_id}",
                created_at=tweet_time.isoformat(),
                retweet_count=i,
                like_count=i*2,
                reply_count=i//2,
                quote_count=i//3,
                is_retweet=False,
                is_quote=False,
                hashtags=["测试", "meme"],
                mentions=[],
                urls=[],
                media_urls=[],
                language="zh",
                collected_at=datetime.now().isoformat()
            )
            tweets.append(tweet_data)
        
        return tweets
    
    def _generate_mock_user(self, user_id: str) -> UserData:
        """生成模拟用户数据（用于测试）"""
        return UserData(
            user_id=user_id,
            username=f"user_{user_id}",
            display_name=f"用户 {user_id}",
            description="这是一个测试用户",
            followers_count=1000 + int(user_id) * 100,
            following_count=500 + int(user_id) * 50,
            tweet_count=2000 + int(user_id) * 200,
            verified=True,
            created_at="2020-01-01T00:00:00Z",
            profile_image_url="",
            is_kol=True,
            kol_score=80.0 + float(user_id) * 2.0,
            kol_tier="Tier 2",
            collected_at=datetime.now().isoformat()
        )
    
    def _save_tweets(self, tweets: List[TweetData]) -> int:
        """保存推文到数据库"""
        saved_count = 0
        
        with self.db_conn.cursor() as cursor:
            for tweet in tweets:
                try:
                    # 生成数据哈希，用于去重
                    data_hash = self._generate_tweet_hash(tweet)
                    
                    cursor.execute("""
                        INSERT INTO tweets (
                            tweet_id, text, user_id, username, created_at,
                            retweet_count, like_count, reply_count, quote_count,
                            is_retweet, is_quote, hashtags, mentions, urls,
                            media_urls, language, data_hash
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (data_hash) DO NOTHING
                    """, (
                        tweet.tweet_id, tweet.text, tweet.user_id, tweet.username,
                        tweet.created_at, tweet.retweet_count, tweet.like_count,
                        tweet.reply_count, tweet.quote_count, tweet.is_retweet,
                        tweet.is_quote, json.dumps(tweet.hashtags), json.dumps(tweet.mentions),
                        json.dumps(tweet.urls), json.dumps(tweet.media_urls),
                        tweet.language, data_hash
                    ))
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存推文失败: {e}")
                    continue
        
        self.db_conn.commit()
        return saved_count
    
    def _save_user(self, user: UserData):
        """保存用户信息到数据库"""
        with self.db_conn.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO users (
                        user_id, username, display_name, description,
                        followers_count, following_count, tweet_count,
                        verified, created_at, profile_image_url,
                        is_kol, kol_score, kol_tier
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET
                        followers_count = EXCLUDED.followers_count,
                        following_count = EXCLUDED.following_count,
                        tweet_count = EXCLUDED.tweet_count,
                        kol_score = EXCLUDED.kol_score,
                        kol_tier = EXCLUDED.kol_tier,
                        collected_at = CURRENT_TIMESTAMP
                """, (
                    user.user_id, user.username, user.display_name, user.description,
                    user.followers_count, user.following_count, user.tweet_count,
                    user.verified, user.created_at, user.profile_image_url,
                    user.is_kol, user.kol_score, user.kol_tier
                ))
                self.db_conn.commit()
                
            except Exception as e:
                logger.error(f"保存用户信息失败: {e}")
    
    def _generate_tweet_hash(self, tweet: TweetData) -> str:
        """生成推文数据哈希，用于去重"""
        content = f"{tweet.tweet_id}_{tweet.text}_{tweet.user_id}_{tweet.created_at}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_collection_stats(self) -> Dict:
        """获取采集统计信息"""
        with self.db_conn.cursor() as cursor:
            # 推文统计
            cursor.execute("SELECT COUNT(*) FROM tweets")
            total_tweets = cursor.fetchone()[0]
            
            # 用户统计
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # KOL统计
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_kol = TRUE")
            total_kols = cursor.fetchone()[0]
            
            # 今日采集统计
            today = datetime.now().date()
            cursor.execute("SELECT COUNT(*) FROM tweets WHERE DATE(collected_at) = %s", (today,))
            today_tweets = cursor.fetchone()[0]
            
            return {
                "total_tweets": total_tweets,
                "total_users": total_users,
                "total_kols": total_kols,
                "today_tweets": today_tweets,
                "collection_date": today.isoformat()
            }
    
    def cleanup_old_data(self, days: int = 30):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.db_conn.cursor() as cursor:
            cursor.execute("DELETE FROM tweets WHERE created_at < %s", (cutoff_date,))
            deleted_tweets = cursor.rowcount
            
            cursor.execute("DELETE FROM users WHERE collected_at < %s AND is_kol = FALSE", (cutoff_date,))
            deleted_users = cursor.rowcount
            
            self.db_conn.commit()
            
            logger.info(f"清理完成: 删除 {deleted_tweets} 条旧推文，{deleted_users} 个旧用户")
    
    def close(self):
        """关闭数据库连接"""
        if self.db_conn:
            self.db_conn.close()
            logger.info("数据库连接已关闭")

def main():
    """主函数"""
    try:
        # 创建采集器
        collector = TwitterDataCollector()
        
        # 模拟KOL用户列表（实际应该从现有数据中获取）
        kol_users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
        
        # 执行采集
        tweets_count, users_count = collector.collect_kol_tweets(kol_users)
        
        # 获取统计信息
        stats = collector.get_collection_stats()
        logger.info(f"采集统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 清理旧数据
        collector.cleanup_old_data(days=30)
        
        logger.info("数据采集任务完成")
        
    except Exception as e:
        logger.error(f"数据采集失败: {e}")
    finally:
        if 'collector' in locals():
            collector.close()

if __name__ == "__main__":
    main()
