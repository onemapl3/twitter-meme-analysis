#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管道集成脚本
实现从CSV文件读取到实时API采集的平滑切换
"""

import json
import logging
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataPipelineIntegrator:
    """数据管道集成器"""
    
    def __init__(self, config_file='collector_config.json'):
        """初始化集成器"""
        self.config = self._load_config(config_file)
        self.db_config = self.config['database']
        self.db_conn = None
        
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件 {config_file} 未找到")
            raise
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.db_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def migrate_csv_data(self):
        """迁移CSV数据到数据库"""
        print("🔄 开始迁移CSV数据到数据库...")
        
        if not self.connect_database():
            return False
        
        try:
            # 迁移推文数据
            tweets_migrated = self._migrate_tweets()
            
            # 迁移用户关系数据
            users_migrated = self._migrate_users()
            
            # 迁移KOL档案数据
            kol_profiles_migrated = self._migrate_kol_profiles()
            
            print(f"✅ 数据迁移完成！")
            print(f"  - 推文: {tweets_migrated} 条")
            print(f"  - 用户: {users_migrated} 个")
            print(f"  - KOL档案: {kol_profiles_migrated} 个")
            
            return True
            
        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            return False
        finally:
            if self.db_conn:
                self.db_conn.close()
    
    def _migrate_tweets(self) -> int:
        """迁移推文数据"""
        print("  📝 迁移推文数据...")
        
        try:
            # 读取CSV文件
            from config.paths import TWEETS_FILE
            tweets_df = pd.read_csv(TWEETS_FILE)
            print(f"    读取到 {len(tweets_df)} 条推文")
            
            cursor = self.db_conn.cursor()
            
            # 清空现有数据
            cursor.execute("DELETE FROM tweets")
            print("    清空现有推文数据")
            
            # 批量插入数据
            batch_size = 1000
            migrated_count = 0
            
            for i in range(0, len(tweets_df), batch_size):
                batch = tweets_df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    try:
                        # 提取meme提及
                        meme_mentions = self._extract_meme_mentions(row.get('text', ''))
                        
                        # 计算互动指标
                        engagement_metrics = {
                            'likes': int(row.get('likes', 0)),
                            'retweets': int(row.get('retweets', 0)),
                            'replies': int(row.get('replies', 0)),
                            'quotes': int(row.get('quotes', 0))
                        }
                        
                        # 插入数据
                        cursor.execute("""
                            INSERT INTO tweets (
                                tweet_id, text, user_id, username, created_at,
                                retweet_count, like_count, reply_count, quote_count,
                                hashtags, mentions, meme_mentions, engagement_metrics,
                                collected_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            str(row.get('tweet_id', '')),
                            str(row.get('text', '')),
                            str(row.get('user_id', '')),
                            str(row.get('username', '')),
                            row.get('created_at', datetime.now()),
                            int(row.get('retweets', 0)),
                            int(row.get('likes', 0)),
                            int(row.get('replies', 0)),
                            int(row.get('quotes', 0)),
                            [],  # hashtags
                            [],  # mentions
                            meme_mentions,
                            json.dumps(engagement_metrics),
                            datetime.now()
                        ))
                        
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.warning(f"跳过无效推文数据: {e}")
                        continue
                
                # 提交批次
                self.db_conn.commit()
                print(f"    已迁移 {migrated_count} 条推文")
            
            cursor.close()
            return migrated_count
            
        except Exception as e:
            logger.error(f"推文数据迁移失败: {e}")
            return 0
    
    def _migrate_users(self) -> int:
        """迁移用户数据"""
        print("  👥 迁移用户数据...")
        
        try:
            # 读取CSV文件
            from config.paths import FOLLOWINGS_FILE
            followings_df = pd.read_csv(FOLLOWINGS_FILE)
            print(f"    读取到 {len(followings_df)} 条用户关系")
            
            cursor = self.db_conn.cursor()
            
            # 清空现有数据
            cursor.execute("DELETE FROM kol_users")
            print("    清空现有用户数据")
            
            # 提取唯一用户
            unique_users = followings_df[['user_id', 'username']].drop_duplicates()
            migrated_count = 0
            
            for _, row in unique_users.iterrows():
                try:
                    # 计算KOL分数（简化版）
                    kol_score = self._calculate_kol_score(row)
                    kol_tier = self._determine_kol_tier(kol_score)
                    
                    cursor.execute("""
                        INSERT INTO kol_users (
                            user_id, username, display_name, kol_score, kol_tier,
                            profile_data, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(row.get('user_id', '')),
                        str(row.get('username', '')),
                        str(row.get('username', '')),
                        kol_score,
                        kol_tier,
                        json.dumps({'source': 'csv_migration'}),
                        datetime.now()
                    ))
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"跳过无效用户数据: {e}")
                    continue
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"    已迁移 {migrated_count} 个用户")
            return migrated_count
            
        except Exception as e:
            logger.error(f"用户数据迁移失败: {e}")
            return 0
    
    def _migrate_kol_profiles(self) -> int:
        """迁移KOL档案数据"""
        print("  📋 迁移KOL档案数据...")
        
        try:
            # 读取JSON文件
            from config.paths import KOL_PROFILES_FILE
            with open(KOL_PROFILES_FILE, 'r', encoding='utf-8') as f:
                kol_data = json.load(f)
            
            if 'kol_profiles' not in kol_data:
                print("    未找到KOL档案数据")
                return 0
            
            kol_profiles = kol_data['kol_profiles']
            print(f"    读取到 {len(kol_profiles)} 个KOL档案")
            
            cursor = self.db_conn.cursor()
            migrated_count = 0
            
            for profile in kol_profiles:
                try:
                    user_id = profile.get('user_id', '')
                    if not user_id:
                        continue
                    
                    # 更新现有用户记录
                    cursor.execute("""
                        UPDATE kol_users 
                        SET kol_score = %s, kol_tier = %s, profile_data = %s, last_updated = %s
                        WHERE user_id = %s
                    """, (
                        float(profile.get('kol_score', 0)),
                        str(profile.get('kol_tier', 'Tier 4')),
                        json.dumps(profile),
                        datetime.now(),
                        str(user_id)
                    ))
                    
                    if cursor.rowcount > 0:
                        migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"跳过无效KOL档案: {e}")
                    continue
            
            self.db_conn.commit()
            cursor.close()
            
            print(f"    已更新 {migrated_count} 个KOL档案")
            return migrated_count
            
        except Exception as e:
            logger.error(f"KOL档案迁移失败: {e}")
            return 0
    
    def _extract_meme_mentions(self, text: str) -> List[str]:
        """提取推文中的meme提及"""
        if not text or pd.isna(text):
            return []
        
        text = str(text).lower()
        meme_keywords = self.config['collection']['meme_keywords']
        
        mentions = []
        for keyword in meme_keywords:
            if keyword.lower() in text:
                mentions.append(keyword)
        
        return mentions
    
    def _calculate_kol_score(self, user_data: pd.Series) -> float:
        """计算KOL分数（简化版）"""
        # 基于用户名的简单评分
        username = str(user_data.get('username', '')).lower()
        
        score = 0.0
        
        # 包含特定关键词加分
        if any(keyword in username for keyword in ['crypto', 'btc', 'eth', 'nft']):
            score += 30
        elif any(keyword in username for keyword in ['tech', 'ai', 'startup']):
            score += 25
        elif any(keyword in username for keyword in ['trading', 'finance']):
            score += 20
        
        # 用户名长度加分（较长的用户名可能更专业）
        if len(username) > 10:
            score += 10
        
        return min(score, 100.0)  # 最高100分
    
    def _determine_kol_tier(self, score: float) -> str:
        """根据分数确定KOL级别"""
        if score >= 80:
            return 'Tier 1'
        elif score >= 60:
            return 'Tier 2'
        elif score >= 40:
            return 'Tier 3'
        else:
            return 'Tier 4'
    
    def verify_migration(self):
        """验证数据迁移结果"""
        print("\n🔍 验证数据迁移结果...")
        
        if not self.connect_database():
            return False
        
        try:
            cursor = self.db_conn.cursor()
            
            # 检查推文数量
            cursor.execute("SELECT COUNT(*) FROM tweets")
            tweet_count = cursor.fetchone()[0]
            print(f"  推文表: {tweet_count} 条记录")
            
            # 检查用户数量
            cursor.execute("SELECT COUNT(*) FROM kol_users")
            user_count = cursor.fetchone()[0]
            print(f"  用户表: {user_count} 条记录")
            
            # 检查KOL分布
            cursor.execute("SELECT kol_tier, COUNT(*) FROM kol_users GROUP BY kol_tier ORDER BY kol_tier")
            tier_distribution = cursor.fetchall()
            print(f"  KOL级别分布:")
            for tier, count in tier_distribution:
                print(f"    {tier}: {count} 个")
            
            cursor.close()
            
            print(f"\n✅ 数据迁移验证完成！")
            return True
            
        except Exception as e:
            logger.error(f"数据迁移验证失败: {e}")
            return False
        finally:
            if self.db_conn:
                self.db_conn.close()

def main():
    """主函数"""
    print("🚀 开始数据管道集成...\n")
    
    try:
        integrator = DataPipelineIntegrator()
        
        # 执行数据迁移
        success = integrator.migrate_csv_data()
        
        if success:
            # 验证迁移结果
            integrator.verify_migration()
            
            print("\n🎉 数据管道集成完成！")
            print("\n下一步操作：")
            print("1. 配置Twitter API Bearer Token")
            print("2. 运行实时数据采集测试")
            print("3. 验证端到端流程")
        else:
            print("\n❌ 数据管道集成失败")
            
    except Exception as e:
        print(f"❌ 集成过程中发生错误: {e}")

if __name__ == "__main__":
    main()
