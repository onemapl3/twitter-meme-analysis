#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOL档案增强系统 - 任务2实现
数据源扩展与整合
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import re
from collections import defaultdict
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class KOLProfileEnhancer:
    def __init__(self):
        """初始化KOL档案增强器"""
        self.enhanced_profiles = {}
        self.domain_keywords = {
            'crypto': ['bitcoin', 'ethereum', 'nft', 'defi', 'blockchain', 'crypto', 'btc', 'eth', 'token', 'wallet'],
            'tech': ['ai', 'machine learning', 'startup', 'tech', 'innovation', 'software', 'coding', 'programming'],
            'finance': ['trading', 'investment', 'stocks', 'finance', 'economy', 'market', 'portfolio', 'wealth'],
            'entertainment': ['gaming', 'art', 'music', 'film', 'celebrities', 'entertainment', 'culture'],
            'politics': ['politics', 'government', 'policy', 'election', 'democracy', 'society']
        }
        
    def enhance_kol_profiles(self, kol_data, tweets_df, followings_df):
        """增强KOL档案信息"""
        print("开始增强KOL档案...")
        
        for user_id, kol_info in kol_data.items():
            print(f"处理用户: {kol_info['user_name']}")
            
            # 获取用户推文
            user_tweets = tweets_df[tweets_df['user_id'] == user_id]
            
            # 1. 专业领域识别
            domain_info = self._identify_domain(user_tweets, kol_info, followings_df)
            
            # 2. 影响力时间序列
            influence_timeline = self._analyze_influence_timeline(user_tweets, kol_info)
            
            # 3. 内容特征提取
            content_features = self._extract_content_features(user_tweets)
            
            # 整合增强信息
            self.enhanced_profiles[user_id] = {
                **kol_info,
                'enhanced_domain': domain_info,
                'influence_timeline': influence_timeline,
                'content_features': content_features
            }
        
        print(f"完成 {len(self.enhanced_profiles)} 个KOL档案增强")
        return self.enhanced_profiles
    
    def _identify_domain(self, user_tweets, kol_info, followings_df):
        """专业领域识别算法"""
        domain_scores = defaultdict(float)
        
        # 1. 文本关键词分析
        text_score = self._analyze_text_keywords(user_tweets)
        for domain, score in text_score.items():
            domain_scores[domain] += score * 0.4  # 权重40%
        
        # 2. 关注用户领域分布分析
        network_score = self._analyze_following_domains(kol_info['user_id'], followings_df)
        for domain, score in network_score.items():
            domain_scores[domain] += score * 0.3  # 权重30%
        
        # 3. 推文主题聚类分析
        cluster_score = self._analyze_tweet_clusters(user_tweets)
        for domain, score in cluster_score.items():
            domain_scores[domain] += score * 0.3  # 权重30%
        
        # 确定主要领域
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])
        
        return {
            'primary_domain': primary_domain[0],
            'domain_scores': dict(domain_scores),
            'confidence': primary_domain[1]
        }
    
    def _analyze_text_keywords(self, user_tweets):
        """文本关键词分析"""
        domain_scores = defaultdict(float)
        
        if user_tweets.empty:
            return domain_scores
        
        # 合并所有推文文本
        all_text = ' '.join(user_tweets['text'].fillna('').astype(str))
        all_text = all_text.lower()
        
        # 计算每个领域的关键词出现频率
        for domain, keywords in self.domain_keywords.items():
            score = 0
            for keyword in keywords:
                # 使用正则表达式匹配完整单词
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, all_text))
                score += matches
            
            # 标准化分数
            if score > 0:
                domain_scores[domain] = min(score / 10, 1.0)  # 最高1.0分
        
        return domain_scores
    
    def _analyze_following_domains(self, user_id, followings_df):
        """关注用户领域分布分析"""
        domain_scores = defaultdict(float)
        
        # 获取用户关注的人
        following_users = followings_df[followings_df['user_id'] == user_id]['following_user_id'].unique()
        
        if len(following_users) == 0:
            return domain_scores
        
        # 分析关注用户的领域分布
        for following_id in following_users:
            # 这里简化处理，实际应该查询关注用户的领域信息
            # 暂时基于用户ID的哈希值分配领域
            domain_index = hash(following_id) % len(self.domain_keywords)
            domain = list(self.domain_keywords.keys())[domain_index]
            domain_scores[domain] += 1
        
        # 标准化分数
        total_following = len(following_users)
        for domain in domain_scores:
            domain_scores[domain] = domain_scores[domain] / total_following
        
        return domain_scores
    
    def _analyze_tweet_clusters(self, user_tweets):
        """推文主题聚类分析"""
        domain_scores = defaultdict(float)
        
        if len(user_tweets) < 5:  # 推文太少无法聚类
            return domain_scores
        
        try:
            # 文本向量化
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            text_vectors = vectorizer.fit_transform(user_tweets['text'].fillna(''))
            
            # K-means聚类
            n_clusters = min(3, len(user_tweets) // 2)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(text_vectors)
            
            # 分析每个聚类的主题
            for cluster_id in range(n_clusters):
                cluster_tweets = user_tweets[clusters == cluster_id]
                cluster_text = ' '.join(cluster_tweets['text'].fillna('').astype(str))
                
                # 计算聚类与各领域的相关性
                for domain, keywords in self.domain_keywords.items():
                    score = 0
                    for keyword in keywords:
                        pattern = r'\b' + re.escape(keyword) + r'\b'
                        matches = len(re.findall(pattern, cluster_text.lower()))
                        score += matches
                    
                    if score > 0:
                        domain_scores[domain] += score / n_clusters
            
            # 标准化分数
            if domain_scores:
                max_score = max(domain_scores.values())
                for domain in domain_scores:
                    domain_scores[domain] = min(domain_scores[domain] / max_score, 1.0)
                    
        except Exception as e:
            print(f"聚类分析失败: {e}")
        
        return domain_scores
    
    def _analyze_influence_timeline(self, user_tweets, kol_info):
        """影响力时间序列分析"""
        if user_tweets.empty:
            return {}
        
        # 按时间排序
        user_tweets = user_tweets.sort_values('created_at')
        
        # 时间窗口划分 (7天、30天、90天)
        time_windows = [7, 30, 90]
        timeline_data = {}
        
        for window_days in time_windows:
            window_data = self._calculate_window_influence(user_tweets, window_days)
            timeline_data[f'{window_days}d'] = window_data
        
        # 趋势分析
        trend_analysis = self._analyze_influence_trend(timeline_data)
        
        return {
            'windows': timeline_data,
            'trend': trend_analysis
        }
    
    def _calculate_window_influence(self, user_tweets, window_days):
        """计算时间窗口内的影响力"""
        if user_tweets.empty:
            return {}
        
        # 获取时间范围
        end_time = user_tweets['created_at'].max()
        start_time = end_time - timedelta(days=window_days)
        
        # 筛选时间窗口内的推文
        window_tweets = user_tweets[user_tweets['created_at'] >= start_time]
        
        if window_tweets.empty:
            return {
                'tweet_count': 0,
                'total_engagement': 0,
                'avg_engagement': 0,
                'influence_score': 0
            }
        
        # 计算影响力指标
        tweet_count = len(window_tweets)
        total_engagement = (window_tweets['likes'].sum() + 
                          window_tweets['retweets'].sum() + 
                          window_tweets['replies'].sum())
        avg_engagement = total_engagement / tweet_count if tweet_count > 0 else 0
        
        # 影响力分数计算
        influence_score = self._calculate_window_influence_score(
            tweet_count, total_engagement, avg_engagement, user_tweets.iloc[0] if not user_tweets.empty else {}
        )
        
        return {
            'tweet_count': tweet_count,
            'total_engagement': total_engagement,
            'avg_engagement': avg_engagement,
            'influence_score': influence_score
        }
    
    def _calculate_window_influence_score(self, tweet_count, total_engagement, avg_engagement, kol_info):
        """计算时间窗口影响力分数"""
        # 基础影响力 = f(推文数量, 互动量, 用户基础影响力)
        base_influence = (tweet_count * 0.3 + 
                         total_engagement * 0.4 + 
                         kol_info.get('influence_score', 0) * 0.3)
        
        # 时间衰减因子 (越近期的数据权重越高)
        time_decay = 1.0  # 这里简化处理，实际应该基于时间差计算
        
        return round(base_influence * time_decay, 2)
    
    def _analyze_influence_trend(self, timeline_data):
        """分析影响力趋势"""
        if not timeline_data:
            return {}
        
        # 提取7天和30天的数据进行比较
        week_data = timeline_data.get('7d', {})
        month_data = timeline_data.get('30d', {})
        
        if not week_data or not month_data:
            return {'trend': 'insufficient_data'}
        
        # 计算趋势
        week_influence = week_data.get('influence_score', 0)
        month_influence = month_data.get('influence_score', 0)
        
        if month_influence == 0:
            trend = 'stable'
        else:
            change_rate = (week_influence - month_influence) / month_influence
            if change_rate > 0.1:
                trend = 'increasing'
            elif change_rate < -0.1:
                trend = 'decreasing'
            else:
                trend = 'stable'
        
        return {
            'trend': trend,
            'week_influence': week_influence,
            'month_influence': month_influence,
            'change_rate': round((week_influence - month_influence) / month_influence, 3) if month_influence > 0 else 0
        }
    
    def _extract_content_features(self, user_tweets):
        """内容特征提取"""
        if user_tweets.empty:
            return {}
        
        # 语言风格分析
        language_style = self._analyze_language_style(user_tweets)
        
        # 内容主题分布
        topic_distribution = self._analyze_topic_distribution(user_tweets)
        
        # 互动模式分析
        interaction_patterns = self._analyze_interaction_patterns(user_tweets)
        
        return {
            'language_style': language_style,
            'topic_distribution': topic_distribution,
            'interaction_patterns': interaction_patterns
        }
    
    def _analyze_language_style(self, user_tweets):
        """语言风格分析"""
        if user_tweets.empty:
            return {}
        
        # 计算推文长度统计
        tweet_lengths = user_tweets['text'].str.len()
        
        # 检测技术性词汇
        technical_terms = ['api', 'algorithm', 'database', 'framework', 'protocol']
        technical_count = sum(user_tweets['text'].str.contains('|'.join(technical_terms), case=False, na=False))
        
        # 检测表情符号使用
        emoji_pattern = r'[😀-🙏🌀-🗿]'
        emoji_count = sum(user_tweets['text'].str.count(emoji_pattern))
        
        return {
            'avg_length': round(tweet_lengths.mean(), 1),
            'length_variance': round(tweet_lengths.var(), 1),
            'technical_ratio': round(technical_count / len(user_tweets), 3),
            'emoji_ratio': round(emoji_count / len(user_tweets), 3),
            'style_type': 'technical' if technical_count > len(user_tweets) * 0.3 else 'casual'
        }
    
    def _analyze_topic_distribution(self, user_tweets):
        """内容主题分布分析"""
        if user_tweets.empty:
            return {}
        
        # 简单的主题关键词统计
        topic_keywords = {
            'business': ['business', 'company', 'startup', 'entrepreneur'],
            'technology': ['tech', 'software', 'app', 'platform'],
            'finance': ['money', 'investment', 'trading', 'profit'],
            'social': ['people', 'community', 'social', 'friends']
        }
        
        topic_counts = defaultdict(int)
        total_tweets = len(user_tweets)
        
        for topic, keywords in topic_keywords.items():
            count = sum(user_tweets['text'].str.contains('|'.join(keywords), case=False, na=False))
            topic_counts[topic] = round(count / total_tweets, 3)
        
        return dict(topic_counts)
    
    def _analyze_interaction_patterns(self, user_tweets):
        """互动模式分析"""
        if user_tweets.empty:
            return {}
        
        # 计算各种互动率
        total_tweets = len(user_tweets)
        reply_rate = (user_tweets['is_reply'].sum() / total_tweets) if total_tweets > 0 else 0
        quote_rate = (user_tweets['is_quote'].sum() / total_tweets) if total_tweets > 0 else 0
        retweet_rate = (user_tweets['is_retweet'].sum() / total_tweets) if total_tweets > 0 else 0
        
        # 计算平均互动量
        avg_likes = user_tweets['likes'].mean()
        avg_retweets = user_tweets['retweets'].mean()
        avg_replies = user_tweets['replies'].mean()
        
        return {
            'reply_rate': round(reply_rate, 3),
            'quote_rate': round(quote_rate, 3),
            'retweet_rate': round(retweet_rate, 3),
            'avg_likes': round(avg_likes, 1),
            'avg_retweets': round(avg_retweets, 1),
            'avg_replies': round(avg_replies, 1),
            'interaction_type': 'reactive' if reply_rate > 0.5 else 'proactive'
        }
    
    def save_enhanced_profiles(self, filename='enhanced_kol_profiles.json'):
        """保存增强后的KOL档案"""
        print(f"保存增强档案到 {filename}...")
        
        save_data = {
            'enhancement_timestamp': datetime.now().isoformat(),
            'total_profiles': len(self.enhanced_profiles),
            'enhanced_profiles': {}
        }
        
        for user_id, profile in self.enhanced_profiles.items():
            save_data['enhanced_profiles'][user_id] = {
                'user_name': profile['user_name'],
                'influence_score': profile['influence_score'],
                'enhanced_domain': profile['enhanced_domain'],
                'influence_timeline': profile['influence_timeline'],
                'content_features': profile['content_features']
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"增强档案已保存到 {filename}")

def main():
    """主函数"""
    print("=== KOL档案增强系统 ===")
    print("任务2: 数据源扩展与整合")
    print()
    
    # 加载之前的KOL分析结果
    try:
        with open('kol_analysis_results.json', 'r', encoding='utf-8') as f:
            kol_results = json.load(f)
        
        # 创建增强器
        enhancer = KOLProfileEnhancer()
        
        # 加载数据
        print("加载数据...")
        tweets_df = pd.read_csv('sample_tweets.csv')
        followings_df = pd.read_csv('sample_followings.csv')
        
        # 数据预处理
        tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'], unit='s')
        tweets_df['user_id'] = tweets_df['user_id'].astype(str)
        followings_df['user_id'] = followings_df['user_id'].astype(str)
        followings_df['following_user_id'] = followings_df['following_user_id'].astype(str)
        
        # 获取KOL数据
        kol_data = {}
        for kol in kol_results.get('top_kols', [])[:20]:  # 处理前20个KOL
            user_id = kol['user_id']
            kol_data[user_id] = kol
        
        # 增强KOL档案
        enhanced_profiles = enhancer.enhance_kol_profiles(kol_data, tweets_df, followings_df)
        
        # 保存结果
        enhancer.save_enhanced_profiles()
        
        print("\n=== 档案增强完成 ===")
        print(f"处理KOL数量: {len(enhanced_profiles)}")
        
        # 显示示例结果
        if enhanced_profiles:
            sample_user = list(enhanced_profiles.keys())[0]
            sample_profile = enhanced_profiles[sample_user]
            print(f"\n示例 - {sample_profile['user_name']}:")
            print(f"主要领域: {sample_profile['enhanced_domain']['primary_domain']}")
            print(f"影响力趋势: {sample_profile['influence_timeline']['trend']['trend']}")
            print(f"语言风格: {sample_profile['content_features']['language_style']['style_type']}")
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
