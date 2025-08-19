#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础Meme识别系统 - 任务3实现
显性Meme识别 - 简化版设计
"""

import pandas as pd
import re
from collections import Counter, defaultdict
import json
from datetime import datetime

class BasicMemeDetector:
    def __init__(self):
        """初始化基础Meme检测器"""
        # 基础meme关键词 - 第一版：简单直接
        self.meme_keywords = {
            'crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'nft', 'defi', 'blockchain', 'crypto'],
            'tech': ['ai', 'machine learning', 'startup', 'tech', 'innovation'],
            'finance': ['trading', 'investment', 'stocks', 'finance'],
            'gaming': ['gaming', 'game', 'player', 'streamer']
        }
        
        # 停用词 - 过滤明显无关的通用词汇
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them'
        }
        
        self.detected_memes = {}
        
    def load_data(self, tweets_file):
        """加载推文数据"""
        print("加载推文数据...")
        
        # 分块读取，避免内存问题
        self.tweets_df = pd.read_csv(tweets_file, chunksize=10000)
        tweets_list = []
        for chunk in self.tweets_df:
            tweets_list.append(chunk)
        
        self.tweets_df = pd.concat(tweets_list, ignore_index=True)
        print(f"加载了 {len(self.tweets_df)} 条推文")
        
        # 基础数据清理
        self.tweets_df = self.tweets_df.dropna(subset=['text'])
        self.tweets_df['text'] = self.tweets_df['text'].astype(str)
        
    def detect_memes(self):
        """检测Meme - 基础版本"""
        print("开始检测Meme...")
        
        # 1. 关键词匹配 - 核心算法
        meme_counts = self._keyword_matching()
        
        # 2. 频率统计
        meme_stats = self._frequency_analysis(meme_counts)
        
        # 3. 基础过滤
        filtered_memes = self._basic_filtering(meme_stats)
        
        self.detected_memes = filtered_memes
        return filtered_memes
    
    def _keyword_matching(self):
        """关键词匹配算法 - 第一版：简单直接"""
        print("执行关键词匹配...")
        
        meme_counts = defaultdict(int)
        meme_contexts = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text'].lower()
            user_id = row['user_id']
            
            # 遍历所有meme关键词
            for category, keywords in self.meme_keywords.items():
                for keyword in keywords:
                    # 使用正则表达式匹配完整单词
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    matches = re.findall(pattern, text)
                    
                    if matches:
                        meme_name = keyword
                        meme_counts[meme_name] += len(matches)
                        
                        # 记录上下文（前20个字符）
                        context = text[max(0, text.find(keyword)-20):text.find(keyword)+len(keyword)+20]
                        meme_contexts[meme_name].append({
                            'user_id': user_id,
                            'context': context.strip(),
                            'timestamp': row.get('created_at', 'unknown')
                        })
        
        print(f"关键词匹配完成，发现 {len(meme_counts)} 个潜在meme")
        return {'counts': meme_counts, 'contexts': meme_contexts}
    
    def _frequency_analysis(self, meme_data):
        """频率统计分析"""
        print("执行频率分析...")
        
        meme_counts = meme_data['counts']
        meme_contexts = meme_data['contexts']
        
        # 计算基础统计信息
        total_tweets = len(self.tweets_df)
        meme_stats = {}
        
        for meme_name, count in meme_counts.items():
            # 计算提及频率
            frequency = count / total_tweets if total_tweets > 0 else 0
            
            # 获取上下文样本
            contexts = meme_contexts.get(meme_name, [])
            sample_contexts = contexts[:5]  # 只取前5个样本
            
            meme_stats[meme_name] = {
                'mention_count': count,
                'frequency': round(frequency, 6),
                'sample_contexts': sample_contexts,
                'total_contexts': len(contexts)
            }
        
        return meme_stats
    
    def _basic_filtering(self, meme_stats):
        """基础过滤 - 去除明显无关的词汇"""
        print("执行基础过滤...")
        
        filtered_memes = {}
        
        for meme_name, stats in meme_stats.items():
            # 过滤条件1：提及次数太少
            if stats['mention_count'] < 3:
                continue
                
            # 过滤条件2：频率太低
            if stats['frequency'] < 0.0001:  # 少于0.01%的推文提及
                continue
                
            # 过滤条件3：是停用词
            if meme_name.lower() in self.stop_words:
                continue
            
            filtered_memes[meme_name] = stats
        
        print(f"过滤后剩余 {len(filtered_memes)} 个meme")
        return filtered_memes
    
    def generate_report(self):
        """生成Meme检测报告"""
        print("生成检测报告...")
        
        if not self.detected_memes:
            return {}
        
        # 按提及次数排序
        sorted_memes = sorted(
            self.detected_memes.items(), 
            key=lambda x: x[1]['mention_count'], 
            reverse=True
        )
        
        report = {
            'detection_timestamp': datetime.now().isoformat(),
            'total_memes_detected': len(self.detected_memes),
            'total_tweets_analyzed': len(self.tweets_df),
            'top_memes': [],
            'category_summary': defaultdict(int)
        }
        
        # 生成top meme列表
        for meme_name, stats in sorted_memes[:20]:  # 前20名
            # 确定meme类别
            category = self._categorize_meme(meme_name)
            
            meme_info = {
                'name': meme_name,
                'category': category,
                'mention_count': stats['mention_count'],
                'frequency': stats['frequency'],
                'sample_contexts': stats['sample_contexts']
            }
            
            report['top_memes'].append(meme_info)
            report['category_summary'][category] += 1
        
        return report
    
    def _categorize_meme(self, meme_name):
        """简单的meme分类"""
        meme_lower = meme_name.lower()
        
        for category, keywords in self.meme_keywords.items():
            if meme_lower in keywords:
                return category
        
        return 'other'
    
    def save_results(self, filename='basic_meme_detection_results.json'):
        """保存检测结果"""
        print(f"保存结果到 {filename}...")
        
        save_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'detected_memes': self.detected_memes,
            'report': self.generate_report()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")
    
    def print_summary(self):
        """打印检测摘要"""
        if not self.detected_memes:
            print("未检测到任何meme")
            return
        
        print("\n=== 基础Meme检测结果 ===")
        print(f"检测到的meme数量: {len(self.detected_memes)}")
        
        # 按提及次数排序显示前10名
        sorted_memes = sorted(
            self.detected_memes.items(), 
            key=lambda x: x[1]['mention_count'], 
            reverse=True
        )
        
        print("\n=== Top 10 Meme ===")
        for i, (meme_name, stats) in enumerate(sorted_memes[:10], 1):
            category = self._categorize_meme(meme_name)
            print(f"{i}. {meme_name} ({category}) - 提及次数: {stats['mention_count']}, 频率: {stats['frequency']:.6f}")

def main():
    """主函数"""
    print("=== 基础Meme识别系统 ===")
    print("任务3: 显性Meme识别 - 简化版")
    print()
    
    # 创建检测器
    detector = BasicMemeDetector()
    
    try:
        # 1. 加载数据
        detector.load_data('sample_tweets.csv')
        
        # 2. 检测Meme
        detected_memes = detector.detect_memes()
        
        # 3. 生成报告
        report = detector.generate_report()
        
        # 4. 保存结果
        detector.save_results()
        
        # 5. 显示摘要
        detector.print_summary()
        
        print("\n=== 基础Meme检测完成 ===")
        print("这是第一版：基础关键词匹配")
        print("后续可以添加：上下文过滤、精度优化等功能")
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
