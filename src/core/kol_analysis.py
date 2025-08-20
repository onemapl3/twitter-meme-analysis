#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOL推特动态Meme信息捕捉系统
阶段1: KOL识别与分类系统

算法实现详解:
1. KOL识别算法: 基于多维度影响力评分
2. 网络分析算法: 构建用户关注关系网络
3. Mock数据生成算法: 补充缺失的用户信息
4. 性能优化算法: 分块处理和用户数量限制
"""

import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict, Counter
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class KOLAnalyzer:
    def __init__(self):
        """
        初始化KOL分析器
        
        算法设计:
        - kol_data: 存储识别出的KOL信息
        - user_network: 构建用户关注关系网络图
        - kol_categories: 定义KOL专业领域分类关键词
        """
        self.kol_data = {}
        self.user_network = nx.DiGraph()
        
        # KOL专业领域分类关键词映射表
        # 算法原理: 基于关键词匹配进行领域分类
        self.kol_categories = {
            'crypto': ['bitcoin', 'ethereum', 'nft', 'defi', 'crypto', 'blockchain'],
            'tech': ['ai', 'machine learning', 'startup', 'tech', 'innovation'],
            'finance': ['trading', 'investment', 'stocks', 'finance', 'economy'],
            'entertainment': ['gaming', 'art', 'music', 'film', 'celebrities'],
            'politics': ['politics', 'government', 'policy', 'election']
        }
        
    def load_data(self, tweets_file, followings_file):
        """
        加载推特数据和关注关系数据
        
        算法步骤:
        1. 分块读取大型CSV文件 (避免内存溢出)
        2. 数据预处理和清洗
        3. 数据类型标准化
        
        性能优化: 使用chunksize=10000进行分块读取
        """
        print("正在加载数据...")
        
        # 分块读取推文数据 - 性能优化算法
        # 算法原理: 避免一次性加载大文件导致内存溢出
        # 每次只加载10K行数据，然后合并
        self.tweets_df = pd.read_csv(tweets_file, chunksize=10000)
        self.tweets_data = []
        for chunk in self.tweets_df:
            self.tweets_data.append(chunk)
        self.tweets_df = pd.concat(self.tweets_data, ignore_index=True)
        
        # 读取关注关系数据
        self.followings_df = pd.read_csv(followings_file)
        
        print(f"推文数据: {len(self.tweets_df)} 条记录")
        print(f"关注关系数据: {len(self.followings_df)} 条记录")
        
        # 数据预处理
        self._preprocess_data()
        
    def _preprocess_data(self):
        """
        数据预处理算法
        
        算法步骤:
        1. 数据清洗: 去除缺失值
        2. 时间格式转换: Unix时间戳转datetime
        3. 数据类型统一: 用户ID转为字符串类型
        """
        print("正在预处理数据...")
        
        # 数据清洗: 去除关键字段缺失的记录
        self.tweets_df = self.tweets_df.dropna(subset=['user_id', 'text'])
        
        # 时间格式转换算法
        # 输入: Unix时间戳 (如1742013962)
        # 输出: 可读的datetime对象
        self.tweets_df['created_at'] = pd.to_datetime(self.tweets_df['created_at'], unit='s')
        
        # 数据清洗: 去除关注关系中的缺失值
        self.followings_df = self.followings_df.dropna(subset=['user_id', 'following_user_id'])
        
        # 数据类型统一算法
        # 将用户ID转换为字符串类型，确保一致性
        self.tweets_df['user_id'] = self.tweets_df['user_id'].astype(str)
        self.followings_df['user_id'] = self.followings_df['user_id'].astype(str)
        self.followings_df['following_user_id'] = self.followings_df['following_user_id'].astype(str)
        
        print("数据预处理完成")
        
    def generate_mock_kol_data(self):
        """
        Mock数据生成算法
        
        算法目标: 为缺失的用户信息生成合理的模拟数据
        
        算法步骤:
        1. 从现有推文数据提取用户统计信息
        2. 生成缺失的粉丝数、关注数等数据
        3. 计算用户互动率和覆盖度指标
        
        设计原理: 使用真实数据计算指标，用随机数补充缺失数据
        """
        print("正在生成KOL mock数据...")
        
        # 从现有数据中提取用户信息
        # 性能优化: 限制用户数量为100，平衡精度和性能
        unique_users = self.tweets_df['user_id'].unique()
        user_stats = {}
        
        for user_id in unique_users[:100]:  # 限制用户数量以提高性能
            user_tweets = self.tweets_df[self.tweets_df['user_id'] == user_id]
            
            # 计算用户统计信息 - 基于真实推文数据
            total_views = user_tweets['views'].sum()
            total_likes = user_tweets['likes'].sum()
            total_retweets = user_tweets['retweets'].sum()
            total_replies = user_tweets['replies'].sum()
            tweet_count = len(user_tweets)
            
            # 计算影响力指标 - 核心算法
            # 算法公式: 互动率 = (点赞+转发+回复) / 推文数量
            engagement_rate = (total_likes + total_retweets + total_replies) / max(tweet_count, 1)
            
            # 算法公式: 覆盖度 = 总浏览量 / 推文数量
            reach_score = total_views / max(tweet_count, 1)
            
            # Mock数据生成算法
            user_stats[user_id] = {
                'user_name': user_tweets.iloc[0]['user_name'] if not user_tweets.empty else f"user_{user_id}",
                
                # Mock粉丝数生成算法
                # 范围: 1K-1M，覆盖从普通用户到网红用户
                'follower_count': np.random.randint(1000, 1000000),
                
                # Mock关注数生成算法  
                # 范围: 100-10K，通常关注数远小于粉丝数
                'following_count': np.random.randint(100, 10000),
                
                # 真实数据 (基于推文统计)
                'tweet_count': tweet_count,
                'total_views': total_views,
                'total_likes': total_likes,
                'total_retweets': total_retweets,
                'total_replies': total_replies,
                'engagement_rate': engagement_rate,
                'reach_score': reach_score,
                
                # Mock账户年龄生成算法
                # 范围: 30-1000天，确保账户有一定历史但不过于"古老"
                'account_age_days': np.random.randint(30, 1000),
                
                # Mock认证状态生成算法
                # 概率分布: 认证用户10%，非认证用户90%
                'verified': np.random.choice([True, False], p=[0.1, 0.9]),
                
                # 最后活跃时间 (基于真实推文数据)
                'last_active': user_tweets['created_at'].max() if not user_tweets.empty else datetime.now()
            }
        
        self.user_stats = user_stats
        print(f"生成了 {len(user_stats)} 个用户的mock数据")
        
    def identify_kols(self, min_followers=10000, min_engagement=0.1):
        """
        KOL识别算法 - 核心算法
        
        算法目标: 基于多维度指标识别关键意见领袖
        
        算法步骤:
        1. 应用KOL识别标准
        2. 计算综合影响力分数
        3. 进行专业领域分类
        4. 确定KOL级别
        
        识别标准:
        - 粉丝数 >= 10,000
        - 互动率 >= 0.1
        - 推文数量 >= 10
        """
        print("正在识别KOL用户...")
        
        if not hasattr(self, 'user_stats'):
            self.generate_mock_kol_data()
        
        kols = {}
        for user_id, stats in self.user_stats.items():
            # KOL识别标准算法
            # 算法逻辑: 必须同时满足所有条件
            is_kol = (
                stats['follower_count'] >= min_followers and  # 粉丝数门槛
                stats['engagement_rate'] >= min_engagement and  # 互动率门槛
                stats['tweet_count'] >= 10  # 活跃度门槛
            )
            
            if is_kol:
                # 计算KOL影响力分数 - 核心评分算法
                influence_score = self._calculate_influence_score(stats)
                
                # 分类KOL - 专业领域识别算法
                category = self._categorize_kol(stats)
                
                # 确定KOL级别 - 级别判定算法
                kol_level = self._determine_kol_level(influence_score)
                
                kols[user_id] = {
                    **stats,
                    'influence_score': influence_score,
                    'category': category,
                    'kol_level': kol_level
                }
        
        self.kol_data = kols
        print(f"识别出 {len(kols)} 个KOL用户")
        
        return kols
    
    def _calculate_influence_score(self, stats):
        """
        影响力评分算法 - 核心算法
        
        算法公式: 影响力分数 = 粉丝数得分 + 互动率得分 + 覆盖度得分 + 活跃度得分
        
        详细计算步骤:
        1. 粉丝数得分 (最高40分): min(粉丝数/1M, 1.0) × 40
        2. 互动率得分 (最高30分): min(互动率×100, 30)
        3. 覆盖度得分 (最高20分): min(覆盖度/10K, 20)  
        4. 活跃度得分 (最高10分): min(推文数/1K, 10)
        
        最终分数 = 基础分数 × 认证加成 (认证用户×1.2)
        """
        # 1. 粉丝数得分计算 (最高40分)
        # 算法公式: min(粉丝数 / 1,000,000, 1.0) × 40
        follower_score = min(stats['follower_count'] / 1000000, 1.0) * 40
        
        # 2. 互动率得分计算 (最高30分)
        # 算法公式: min(互动率 × 100, 30)
        engagement_score = min(stats['engagement_rate'] * 100, 30)
        
        # 3. 覆盖度得分计算 (最高20分)
        # 算法公式: min(覆盖度 / 10,000, 20)
        reach_score = min(stats['reach_score'] / 10000, 20)
        
        # 4. 活跃度得分计算 (最高10分)
        # 算法公式: min(推文数 / 1,000, 10)
        activity_score = min(stats['tweet_count'] / 1000, 10)
        
        # 加权计算 - 基础分数
        total_score = follower_score + engagement_score + reach_score + activity_score
        
        # 认证用户加成算法
        # 算法逻辑: 认证用户获得20%的分数加成
        if stats['verified']:
            total_score *= 1.2
            
        return round(total_score, 2)
    
    def _categorize_kol(self, stats):
        """
        KOL分类算法
        
        算法目标: 根据用户特征将其分类到不同专业领域
        
        分类规则:
        IF 用户名包含关键词 THEN 分类 = 对应领域
        ELSE 分类 = 'general'
        
        关键词映射表:
        - crypto: ['crypto', 'btc', 'eth', 'nft', 'defi', 'blockchain']
        - tech: ['tech', 'ai', 'startup', 'innovation', 'software']
        - finance: ['trading', 'finance', 'invest', 'stocks', 'economy']
        - entertainment: ['gaming', 'art', 'music', 'film', 'celebrities']
        """
        # 基于用户名和推文内容进行分类
        user_name = stats['user_name'].lower()
        
        # 简单的基于用户名的分类算法
        # 算法逻辑: 遍历关键词列表，检查用户名是否包含
        if any(keyword in user_name for keyword in ['crypto', 'btc', 'eth', 'nft']):
            return 'crypto'
        elif any(keyword in user_name for keyword in ['tech', 'ai', 'startup']):
            return 'tech'
        elif any(keyword in user_name for keyword in ['trading', 'finance', 'invest']):
            return 'finance'
        elif any(keyword in user_name for keyword in ['gaming', 'art', 'music']):
            return 'entertainment'
        else:
            return 'general'
    
    def _determine_kol_level(self, influence_score):
        """
        KOL级别判定算法
        
        算法目标: 根据影响力分数确定KOL的级别
        
        级别划分规则:
        IF 影响力分数 >= 80 THEN 级别 = 'Tier 1 (顶级KOL)'
        ELIF 影响力分数 >= 60 THEN 级别 = 'Tier 2 (高级KOL)'
        ELIF 影响力分数 >= 40 THEN 级别 = 'Tier 3 (中级KOL)'
        ELSE 级别 = 'Tier 4 (初级KOL)'
        """
        if influence_score >= 80:
            return 'Tier 1 (顶级KOL)'
        elif influence_score >= 60:
            return 'Tier 2 (高级KOL)'
        elif influence_score >= 40:
            return 'Tier 3 (中级KOL)'
        else:
            return 'Tier 4 (初级KOL)'
    
    def build_user_network(self):
        """
        网络构建算法
        
        算法目标: 构建用户关注关系网络图
        
        算法步骤:
        1. 节点添加: 为每个用户创建一个节点，节点属性包含用户统计信息
        2. 边添加: 根据关注关系数据添加有向边 (用户A → 关注用户B)
        
        网络类型: 有向图 (Directed Graph)
        - 节点: 用户
        - 边: 关注关系 (A关注B)
        """
        print("正在构建用户网络...")
        
        # 添加节点 - 每个用户作为一个节点
        for user_id in self.user_stats.keys():
            # 节点属性包含完整的用户统计信息
            self.user_network.add_node(user_id, **self.user_stats[user_id])
        
        # 添加边 - 关注关系
        for _, row in self.followings_df.iterrows():
            # 只添加两个用户都在分析范围内的边
            if row['user_id'] in self.user_stats and row['following_user_id'] in self.user_stats:
                # 有向边: 用户A关注用户B
                self.user_network.add_edge(row['user_id'], row['following_user_id'])
        
        print(f"网络构建完成: {self.user_network.number_of_nodes()} 个节点, {self.user_network.number_of_edges()} 条边")
        
    def analyze_network_metrics(self):
        """
        网络指标分析算法
        
        算法目标: 计算网络的各种中心性指标和整体特征
        
        计算的指标:
        1. 度中心性 (Degree Centrality): 节点的连接数
        2. 接近中心性 (Closeness Centrality): 节点到其他节点的平均距离
        3. 介数中心性 (Betweenness Centrality): 节点作为"桥梁"的重要性
        4. 网络密度: 实际连接数与最大可能连接数的比例
        5. 平均聚类系数: 网络的局部聚集程度
        """
        print("正在分析网络指标...")
        
        if not self.user_network.nodes():
            self.build_user_network()
        
        network_metrics = {}
        
        # 计算中心性指标 - 网络分析核心算法
        if len(self.user_network.nodes()) > 1:
            # 1. 度中心性计算
            # 算法公式: 度中心性 = 节点的连接数 / (总节点数 - 1)
            degree_centrality = nx.degree_centrality(self.user_network)
            
            # 2. 接近中心性计算
            # 算法公式: 接近中心性 = (总节点数 - 1) / 到所有其他节点的最短路径长度之和
            closeness_centrality = nx.closeness_centrality(self.user_network)
            
            # 3. 介数中心性计算
            # 算法公式: 介数中心性 = 该节点作为"桥梁"的次数 / 所有最短路径的总数
            betweenness_centrality = nx.betweenness_centrality(self.user_network)
            
            # 更新用户统计信息 - 将网络指标添加到用户档案中
            for user_id in self.user_network.nodes():
                if user_id in self.user_stats:
                    self.user_stats[user_id].update({
                        'degree_centrality': degree_centrality.get(user_id, 0),
                        'closeness_centrality': closeness_centrality.get(user_id, 0),
                        'betweenness_centrality': betweenness_centrality.get(user_id, 0)
                    })
            
            # 计算整体网络指标
            network_metrics = {
                'total_nodes': self.user_network.number_of_nodes(),
                'total_edges': self.user_network.number_of_edges(),
                
                # 网络密度计算
                # 算法公式: 网络密度 = 实际边数 / 最大可能边数
                'density': nx.density(self.user_network),
                
                # 平均聚类系数计算
                # 含义: 衡量网络的局部聚集程度
                'avg_clustering': nx.average_clustering(self.user_network),
                
                # 平均最短路径长度计算
                # 含义: 网络中任意两个节点的平均距离
                'avg_shortest_path': nx.average_shortest_path_length(self.user_network) if nx.is_connected(self.user_network.to_undirected()) else float('inf')
            }
        
        self.network_metrics = network_metrics
        return network_metrics
    
    def generate_kol_report(self):
        """
        KOL分析报告生成算法
        
        算法目标: 生成完整的KOL分析报告
        
        报告内容:
        1. 总体统计摘要
        2. 顶级KOL排名
        3. 分类分布统计
        4. 级别分布统计
        """
        print("正在生成KOL分析报告...")
        
        if not self.kol_data:
            self.identify_kols()
        
        # 按影响力分数排序 - 排序算法
        # 算法逻辑: 按影响力分数降序排列
        sorted_kols = sorted(self.kol_data.items(), key=lambda x: x[1]['influence_score'], reverse=True)
        
        report = {
            'summary': {
                'total_kols': len(self.kol_data),
                'total_users': len(self.user_stats),
                'kol_percentage': len(self.kol_data) / len(self.user_stats) * 100
            },
            'top_kols': [],
            'category_distribution': defaultdict(int),
            'level_distribution': defaultdict(int)
        }
        
        # 顶级KOL信息提取 - 取前20名
        for user_id, stats in sorted_kols[:20]:
            report['top_kols'].append({
                'user_id': user_id,
                'user_name': stats['user_name'],
                'influence_score': stats['influence_score'],
                'follower_count': stats['follower_count'],
                'category': stats['category'],
                'kol_level': stats['kol_level'],
                'engagement_rate': stats['engagement_rate']
            })
            
            # 统计分布信息
            report['category_distribution'][stats['category']] += 1
            report['level_distribution'][stats['kol_level']] += 1
        
        self.kol_report = report
        return report
    
    def visualize_kol_network(self, top_kols=50):
        """
        KOL网络可视化算法
        
        算法目标: 生成KOL网络的图形化表示
        
        可视化内容:
        1. 节点: 代表KOL用户，大小反映影响力分数
        2. 边: 代表关注关系
        3. 颜色: 反映专业领域分类
        4. 标签: 显示用户名
        """
        print("正在生成KOL网络可视化...")
        
        if not self.kol_data:
            self.identify_kols()
        
        # 选择顶级KOL进行可视化 - 限制数量避免图形过于复杂
        top_kol_ids = list(self.kol_data.keys())[:top_kols]
        
        # 创建子图 - 只包含顶级KOL
        subgraph = self.user_network.subgraph(top_kol_ids)
        
        plt.figure(figsize=(15, 12))
        
        # 设置节点大小和颜色 - 可视化算法
        # 节点大小: 影响力分数 × 10 (确保节点大小差异明显)
        node_sizes = [self.kol_data[node]['influence_score'] * 10 for node in subgraph.nodes()]
        
        # 节点颜色: 基于专业领域的哈希值 (确保同类领域颜色相近)
        node_colors = [hash(self.kol_data[node]['category']) % 20 for node in subgraph.nodes()]
        
        # 绘制网络图 - 使用spring布局算法
        # 布局算法: spring_layout，模拟物理弹簧力，自动调整节点位置
        pos = nx.spring_layout(subgraph, k=3, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(subgraph, pos, 
                              node_size=node_sizes, 
                              node_color=node_colors,
                              alpha=0.7,
                              cmap=plt.cm.Set3)
        
        # 绘制边 (关注关系)
        nx.draw_networkx_edges(subgraph, pos, alpha=0.2, edge_color='gray')
        
        # 添加标签 - 显示用户名 (限制长度避免重叠)
        labels = {node: self.kol_data[node]['user_name'][:10] for node in subgraph.nodes()}
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=8)
        
        plt.title(f'KOL网络图 (Top {len(top_kol_ids)} KOLs)', fontsize=16)
        plt.axis('off')
        
        # 保存图表
        plt.savefig('kol_network.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("KOL网络图已保存为 kol_network.png")
    
    def save_results(self, filename='kol_analysis_results.json'):
        """
        结果保存算法
        
        算法目标: 将分析结果保存为JSON格式文件
        
        保存内容:
        1. 分析时间戳
        2. KOL分析报告
        3. 网络指标
        4. 顶级KOL详细信息
        """
        print(f"正在保存结果到 {filename}...")
        
        # 准备保存的数据
        save_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'kol_report': self.kol_report if hasattr(self, 'kol_report') else None,
            'network_metrics': self.network_metrics if hasattr(self, 'network_metrics') else None,
            'top_kols': []
        }
        
        # 保存顶级KOL信息 (前50名)
        if self.kol_data:
            for user_id, stats in list(self.kol_data.items())[:50]:
                save_data['top_kols'].append({
                    'user_id': user_id,
                    'user_name': stats['user_name'],
                    'influence_score': stats['influence_score'],
                    'category': stats['category'],
                    'kol_level': stats['kol_level'],
                    'follower_count': stats['follower_count'],
                    'engagement_rate': stats['engagement_rate']
                })
        
        # 保存到文件 - JSON格式，支持中文
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")

def main():
    """
    主函数 - 算法执行流程
    
    执行步骤:
    1. 创建KOL分析器实例
    2. 加载和预处理数据
    3. 生成mock数据
    4. 识别KOL用户
    5. 构建和分析网络
    6. 生成报告和可视化
    7. 保存结果
    """
    print("=== KOL推特动态Meme信息捕捉系统 ===")
    print("阶段1: KOL识别与分类系统")
    print()
    
    # 创建KOL分析器
    analyzer = KOLAnalyzer()
    
    try:
        # 1. 数据加载阶段
        from config.paths import TWEETS_FILE, FOLLOWINGS_FILE
        analyzer.load_data(str(TWEETS_FILE), str(FOLLOWINGS_FILE))
        
        # 2. Mock数据生成阶段
        analyzer.generate_mock_kol_data()
        
        # 3. KOL识别阶段
        kols = analyzer.identify_kols()
        
        # 4. 网络构建阶段
        analyzer.build_user_network()
        
        # 5. 网络分析阶段
        network_metrics = analyzer.analyze_network_metrics()
        
        # 6. 报告生成阶段
        report = analyzer.generate_kol_report()
        
        # 7. 可视化生成阶段
        analyzer.visualize_kol_network()
        
        # 8. 结果保存阶段
        analyzer.save_results()
        
        # 输出摘要 - 算法执行结果展示
        print("\n=== 分析完成 ===")
        print(f"总用户数: {report['summary']['total_users']}")
        print(f"识别KOL数: {report['summary']['total_kols']}")
        print(f"KOL占比: {report['summary']['kol_percentage']:.2f}%")
        
        print("\n=== 顶级KOL (Top 10) ===")
        for i, kol in enumerate(report['top_kols'][:10], 1):
            print(f"{i}. {kol['user_name']} - 影响力分数: {kol['influence_score']}, 类别: {kol['category']}, 级别: {kol['kol_level']}")
        
        print("\n=== 网络指标 ===")
        for key, value in network_metrics.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
