#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
推特热门项目筛选系统
====================

该系统分析推特数据集，识别并筛选热门项目，计算影响力得分。
"""

import os
import re
import csv
import json
import datetime
import logging
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("twitter_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置参数
CONFIG = {
    'tweets_file': 'sample_tweets.csv',
    'followings_file': 'sample_followings.csv',
    'min_mentions': 5,
    'min_engagement': 10,
    'min_score': 20,
    'mention_weight': 0.3,
    'engagement_weight': 0.4,
    'influence_weight': 0.3,
    'trend_weight': 0.2,
    'trend_dampening': 0.1,
    'results_file': 'hot_projects.json',
    'charts_dir': 'charts'
}

class DataLoader:
    """数据加载模块，负责高效读取大型CSV文件"""
    
    def __init__(self, config):
        self.config = config
        
    def load_tweets_in_chunks(self, chunk_size=10000):
        """分块读取推文数据"""
        logger.info(f"开始加载推文数据: {self.config['tweets_file']}")
        try:
            chunks = pd.read_csv(self.config['tweets_file'], chunksize=chunk_size)
            return chunks
        except Exception as e:
            logger.error(f"加载推文数据失败: {e}")
            raise
    
    def load_followings_in_chunks(self, chunk_size=10000):
        """分块读取关注关系数据"""
        logger.info(f"开始加载关注关系数据: {self.config['followings_file']}")
        try:
            chunks = pd.read_csv(self.config['followings_file'], chunksize=chunk_size)
            return chunks
        except Exception as e:
            logger.error(f"加载关注关系数据失败: {e}")
            raise
    
    def calculate_user_stats(self):
        """计算用户统计数据（粉丝数、活跃度等）"""
        logger.info("计算用户统计数据")
        
        # 初始化用户统计数据结构
        user_stats = {}
        
        # 计算用户发文频率和互动量
        tweet_counts = defaultdict(int)
        engagement_per_user = defaultdict(float)
        
        # 处理推文数据，计算每个用户的发文数和互动量
        for tweet_chunk in self.load_tweets_in_chunks():
            for _, tweet in tweet_chunk.iterrows():
                user_id = tweet.get('user_id')
                if user_id and not pd.isna(user_id):
                    # 增加发文计数
                    tweet_counts[user_id] += 1
                    
                    # 计算互动量
                    engagement = (
                        float(tweet.get('likes', 0)) * 0.5 +
                        float(tweet.get('retweets', 0)) * 1.0 +
                        float(tweet.get('replies', 0)) * 0.7
                    )
                    engagement_per_user[user_id] += engagement
        
        # 计算粉丝数据
        follower_counts = defaultdict(int)
        
        # 处理关注关系数据
        for following_chunk in self.load_followings_in_chunks():
            for _, following in following_chunk.iterrows():
                followed_id = following.get('following_user_id')
                if followed_id and not pd.isna(followed_id):
                    # 增加被关注计数
                    follower_counts[followed_id] += 1
        
        # 整合所有用户数据
        all_user_ids = set(list(tweet_counts.keys()) + list(follower_counts.keys()))
        
        # 计算每个用户的统计数据
        for user_id in all_user_ids:
            # 基本数据
            tweets_count = tweet_counts.get(user_id, 0)
            followers_count = follower_counts.get(user_id, 0)
            engagement = engagement_per_user.get(user_id, 0)
            
            # 计算活跃度系数 (0.1-1.0)
            activity = min(tweets_count / 30.0, 1.0)
            if activity < 0.1:
                activity = 0.1
            
            # 计算影响力
            # 影响力 = 粉丝数 * 活跃度 * (1 + 互动量/100)
            influence = followers_count * activity * (1 + engagement/100.0)
            
            # 存储用户统计数据
            user_stats[user_id] = {
                'tweets_count': tweets_count,
                'followers_count': followers_count,
                'engagement': engagement,
                'activity': activity,
                'influence': influence
            }
        
        logger.info(f"完成用户统计数据计算，共 {len(user_stats)} 个用户")
        return user_stats

class DataCleaner:
    """数据清洗模块，负责处理缺失值、异常值和格式化数据"""
    
    def __init__(self):
        self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were'])
        
    def clean_tweet_text(self, text):
        """清洗推文文本"""
        if pd.isna(text):
            return ""
        
        # 移除URL
        text = re.sub(r'http\S+', '', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\$\#\@]', ' ', text)
        # 规范化空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def normalize_timestamp(self, timestamp):
        """规范化时间戳格式"""
        try:
            if pd.isna(timestamp):
                return None
            return pd.to_datetime(timestamp)
        except:
            return None
    
    def process_tweet_chunk(self, chunk):
        """处理一个推文数据块"""
        # 复制数据避免修改原始数据
        processed = chunk.copy()
        
        # 清洗文本
        processed['cleaned_text'] = processed['text'].apply(self.clean_tweet_text)
        
        # 规范化时间戳
        processed['normalized_time'] = processed['created_at'].apply(self.normalize_timestamp)
        
        # 处理互动量（填充缺失值为0）
        for col in ['views', 'replies', 'retweets', 'likes', 'bookmarks']:
            if col in processed.columns:
                processed[col] = processed[col].fillna(0).astype(int)
        
        return processed

class ProjectIdentifier:
    """项目识别模块，从推文中识别和提取项目"""
    
    def __init__(self):
        # 已知项目关键词列表
        self.known_projects = set(['bitcoin', 'ethereum', 'solana', 'nft', 'defi'])
        # 项目相关正则表达式
        self.project_patterns = [
            r'\$([A-Za-z0-9]+)',  # $符号标记的通证
            r'#([A-Za-z0-9]+)',   # 标签
            r'@([A-Za-z0-9_]+)'   # 提及用户
        ]
    
    def extract_projects(self, text):
        """从文本中提取项目标识符"""
        if pd.isna(text) or not text:
            return []
        
        projects = []
        
        # 使用正则表达式匹配
        for pattern in self.project_patterns:
            matches = re.findall(pattern, text)
            projects.extend(matches)
        
        # 匹配已知项目关键词
        text_lower = text.lower()
        for project in self.known_projects:
            if project in text_lower:
                projects.append(project)
        
        # 移除重复项
        return list(set(projects))
    
    def process_tweet_batch(self, processed_tweets):
        """处理一批推文，提取项目"""
        # 为每条推文提取项目
        projects_by_tweet = []
        
        for _, tweet in processed_tweets.iterrows():
            if pd.isna(tweet['cleaned_text']):
                projects_by_tweet.append([])
                continue
                
            projects = self.extract_projects(tweet['cleaned_text'])
            projects_by_tweet.append(projects)
        
        # 添加项目列表到数据框
        processed_tweets['projects'] = projects_by_tweet
        return processed_tweets

class ScoreCalculator:
    """评分计算模块，计算项目热度得分"""
    
    def __init__(self, config):
        self.config = config
    
    def calculate_mention_score(self, project_mentions, max_mentions):
        """计算提及次数得分"""
        if max_mentions == 0:
            return 0
        return (project_mentions / max_mentions) * 100
    
    def calculate_engagement_score(self, project_engagement, max_engagement):
        """计算互动量得分"""
        if max_engagement == 0:
            return 0
        return (project_engagement / max_engagement) * 100
    
    def calculate_influence_score(self, project_influence, max_influence):
        """计算用户影响力得分"""
        if max_influence == 0:
            return 0
        return (project_influence / max_influence) * 100
    
    def calculate_trend_bonus(self, recent_mentions, previous_mentions):
        """计算趋势加成"""
        if previous_mentions == 0:
            return self.config['trend_weight'] if recent_mentions > 0 else 0
            
        growth_rate = (recent_mentions - previous_mentions) / previous_mentions
        
        if growth_rate < 0:
            return growth_rate * self.config['trend_dampening']
        else:
            return growth_rate * self.config['trend_weight']
    
    def calculate_final_score(self, mention_score, engagement_score, influence_score, trend_bonus):
        """计算最终得分"""
        base_score = (
            mention_score * self.config['mention_weight'] +
            engagement_score * self.config['engagement_weight'] +
            influence_score * self.config['influence_weight']
        )
        
        final_score = base_score * (1 + trend_bonus)
        return final_score

class AnalysisManager:
    """分析管理模块，协调整个分析流程"""
    
    def __init__(self, config):
        self.config = config
        self.data_loader = DataLoader(config)
        self.data_cleaner = DataCleaner()
        self.project_identifier = ProjectIdentifier()
        self.score_calculator = ScoreCalculator(config)
        
        # 创建输出目录
        if not os.path.exists(config['charts_dir']):
            os.makedirs(config['charts_dir'])
    
    def run_analysis(self):
        """运行完整分析流程"""
        logger.info("开始分析流程")
        
        # 1. 收集项目数据
        project_data = self.collect_project_data()
        
        # 2. 计算评分
        scored_projects = self.calculate_scores(project_data)
        
        # 3. 筛选热门项目
        hot_projects = self.filter_hot_projects(scored_projects)
        
        # 4. 生成结果
        self.generate_results(hot_projects)
        
        logger.info("分析完成")
        return hot_projects
    
    def collect_project_data(self):
        """收集项目数据"""
        logger.info("收集项目数据")
        
        # 用户统计数据
        user_stats = self.data_loader.calculate_user_stats()
        
        # 项目数据
        project_data = defaultdict(lambda: {
            'mentions': 0,
            'engagement': 0,
            'influence': 0,
            'recent_mentions': 0,
            'previous_mentions': 0,
            'tweets': [],
            'users': set()
        })
        
        # 处理推文数据
        for tweet_chunk in self.data_loader.load_tweets_in_chunks():
            # 清洗数据
            cleaned_chunk = self.data_cleaner.process_tweet_chunk(tweet_chunk)
            
            # 识别项目
            processed_chunk = self.project_identifier.process_tweet_batch(cleaned_chunk)
            
            # 统计项目数据
            for _, tweet in processed_chunk.iterrows():
                projects = tweet['projects']
                
                # 跳过没有项目的推文
                if not projects:
                    continue
                
                # 计算互动量
                engagement = (
                    float(tweet.get('likes', 0)) * 0.5 +
                    float(tweet.get('retweets', 0)) * 1.0 +
                    float(tweet.get('replies', 0)) * 0.7
                )
                
                # 获取推文时间
                tweet_time = tweet['normalized_time']
                is_recent = False
                if tweet_time is not None:
                    now = datetime.datetime.now()
                    days_ago = (now - tweet_time).days
                    is_recent = days_ago <= 7
                
                # 用户ID
                user_id = tweet.get('user_id')
                
                # 更新项目数据
                for project in projects:
                    project_data[project]['mentions'] += 1
                    project_data[project]['engagement'] += engagement
                    
                    # 记录推文
                    project_data[project]['tweets'].append(tweet['tweet_id'])
                    
                    # 记录用户
                    if user_id is not None:
                        project_data[project]['users'].add(user_id)
                    
                    # 记录近期/早期提及
                    if is_recent:
                        project_data[project]['recent_mentions'] += 1
                    else:
                        project_data[project]['previous_mentions'] += 1
                    
                    # 计算用户影响力（如果有用户统计数据）
                    if user_id in user_stats:
                        user_influence = user_stats[user_id]['influence']
                        project_data[project]['influence'] += user_influence
        
        return project_data
    
    def calculate_scores(self, project_data):
        """计算项目评分"""
        logger.info("计算项目评分")
        
        # 找出最大值用于标准化
        max_mentions = max([data['mentions'] for data in project_data.values()], default=0)
        max_engagement = max([data['engagement'] for data in project_data.values()], default=0)
        max_influence = max([data['influence'] for data in project_data.values()], default=0)
        
        # 计算各项分值
        scored_projects = []
        
        for project, data in project_data.items():
            # 基础分值计算
            mention_score = self.score_calculator.calculate_mention_score(
                data['mentions'], max_mentions
            )
            
            engagement_score = self.score_calculator.calculate_engagement_score(
                data['engagement'], max_engagement
            )
            
            influence_score = self.score_calculator.calculate_influence_score(
                data['influence'], max_influence
            )
            
            # 趋势加成
            trend_bonus = self.score_calculator.calculate_trend_bonus(
                data['recent_mentions'], data['previous_mentions']
            )
            
            # 最终分值
            final_score = self.score_calculator.calculate_final_score(
                mention_score, engagement_score, influence_score, trend_bonus
            )
            
            # 保存项目得分
            scored_project = {
                'name': project,
                'mentions': data['mentions'],
                'engagement': data['engagement'],
                'influence': data['influence'],
                'recent_mentions': data['recent_mentions'],
                'previous_mentions': data['previous_mentions'],
                'mention_score': mention_score,
                'engagement_score': engagement_score,
                'influence_score': influence_score,
                'trend_bonus': trend_bonus,
                'final_score': final_score,
                'unique_users': len(data['users']),
                'tweet_count': len(data['tweets'])
            }
            
            scored_projects.append(scored_project)
        
        # 按最终得分排序
        scored_projects.sort(key=lambda x: x['final_score'], reverse=True)
        return scored_projects
    
    def filter_hot_projects(self, scored_projects):
        """筛选热门项目"""
        logger.info("筛选热门项目")
        
        # 应用筛选标准
        hot_projects = [
            project for project in scored_projects
            if (
                project['mentions'] >= self.config['min_mentions'] and
                project['engagement'] >= self.config['min_engagement'] and
                project['final_score'] >= self.config['min_score']
            )
        ]
        
        return hot_projects
    
    def generate_results(self, hot_projects):
        """生成分析结果"""
        logger.info("生成分析结果")
        
        # 保存为JSON文件
        with open(self.config['results_file'], 'w', encoding='utf-8') as f:
            json.dump(
                {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'projects': hot_projects
                }, 
                f, indent=2
            )
        
        # 生成热度排名图
        self.generate_score_chart(hot_projects[:20])
        
        # 生成用户参与度图
        self.generate_user_engagement_chart(hot_projects[:10])
    
    def generate_score_chart(self, top_projects):
        """生成热度得分图表"""
        plt.figure(figsize=(12, 8))
        
        projects = [p['name'] for p in top_projects]
        scores = [p['final_score'] for p in top_projects]
        
        plt.barh(projects, scores, color='skyblue')
        plt.xlabel('热度得分')
        plt.ylabel('项目名称')
        plt.title('推特热门项目排行榜')
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(self.config['charts_dir'], 'hot_projects_score.png')
        plt.savefig(chart_path)
    
    def generate_user_engagement_chart(self, top_projects):
        """生成用户参与度图表"""
        plt.figure(figsize=(12, 8))
        
        projects = [p['name'] for p in top_projects]
        users = [p['unique_users'] for p in top_projects]
        tweets = [p['tweet_count'] for p in top_projects]
        
        x = np.arange(len(projects))
        width = 0.35
        
        plt.bar(x - width/2, users, width, label='独立用户数')
        plt.bar(x + width/2, tweets, width, label='推文数')
        
        plt.xlabel('项目名称')
        plt.ylabel('数量')
        plt.title('推特项目用户参与度')
        plt.xticks(x, projects, rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(self.config['charts_dir'], 'user_engagement.png')
        plt.savefig(chart_path)

def main():
    """主函数"""
    logger.info("=== 推特热门项目筛选系统启动 ===")
    
    # 初始化分析管理器
    analysis_manager = AnalysisManager(CONFIG)
    
    # 运行分析
    hot_projects = analysis_manager.run_analysis()
    
    # 输出结果
    logger.info(f"分析完成，找到 {len(hot_projects)} 个热门项目")
    
    if hot_projects:
        logger.info("热门项目 TOP 10:")
        for i, project in enumerate(hot_projects[:10], 1):
            logger.info(f"{i}. {project['name']} - 得分: {project['final_score']:.2f}")
    
    logger.info("=== 推特热门项目筛选系统结束 ===")

if __name__ == "__main__":
    main()