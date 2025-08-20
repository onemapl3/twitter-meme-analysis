#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meme识别系统 V2 - 重新设计
专注于识别真正的meme币，而不是主流项目
"""

import pandas as pd
import re
from collections import defaultdict
import json
from datetime import datetime

class MemeDetectorV2:
    def __init__(self):
        """初始化Meme检测器 V2"""
        
        # 重新定义meme关键词库 - 专注于真正的meme币
        self.meme_keywords = {
            # 动物meme币
            'animal_memes': [
                'doge', 'shib', 'shiba', 'pepe', 'floki', 'bonk', 'wojak', 'chad', 'virgin',
                'cat', 'kitten', 'puppy', 'monkey', 'ape', 'frog', 'bird', 'fish', 'turtle',
                'hamster', 'rabbit', 'fox', 'wolf', 'bear', 'bull', 'whale', 'shark'
            ],
            # 网络文化meme
            'internet_culture': [
                'wojak', 'chad', 'virgin', 'stacy', 'becky', 'karen', 'boomer', 'zoomer',
                'simp', 'incel', 'normie', 'weeb', 'otaku', 'gamer', 'nerd', 'geek',
                'hacker', 'script kiddie', 'lurker', 'troll', 'kek', 'lol', 'rofl'
            ],
            # 表情包和符号
            'emoji_memes': [
                'moon', 'rocket', 'diamond', 'gem', 'fire', 'lit', 'based', 'cringe',
                'sus', 'amogus', 'among us', 'reddit', '4chan', 'discord', 'telegram'
            ],
            # 新兴meme项目
            'emerging_memes': [
                'moon', 'rocket', 'mars', 'jupiter', 'saturn', 'pluto', 'galaxy',
                'star', 'planet', 'cosmos', 'universe', 'dimension', 'portal', 'gate'
            ]
        }
        
        # 主流项目黑名单 - 这些不是meme
        self.mainstream_blacklist = {
            'bitcoin', 'btc', 'ethereum', 'eth', 'cardano', 'ada', 'solana', 'sol',
            'polkadot', 'dot', 'chainlink', 'link', 'uniswap', 'uni', 'aave',
            'ai', 'artificial intelligence', 'machine learning', 'blockchain',
            'defi', 'decentralized finance', 'nft', 'non fungible token'
        }
        
        self.detected_memes = {}
        
    def load_data(self, tweets_file):
        """加载推文数据"""
        print("加载推文数据...")
        
        # 分块读取
        self.tweets_df = pd.read_csv(tweets_file, chunksize=10000)
        tweets_list = []
        for chunk in self.tweets_df:
            tweets_list.append(chunk)
        
        self.tweets_df = pd.concat(tweets_list, ignore_index=True)
        print(f"加载了 {len(self.tweets_df)} 条推文")
        
        # 数据清理
        self.tweets_df = self.tweets_df.dropna(subset=['text'])
        self.tweets_df['text'] = self.tweets_df['text'].astype(str)
        
    def detect_memes(self):
        """检测真正的Meme"""
        print("开始检测真正的Meme...")
        
        # 1. 识别潜在meme
        potential_memes = self._identify_potential_memes()
        
        # 2. 过滤主流项目
        filtered_memes = self._filter_mainstream_projects(potential_memes)
        
        # 3. 计算meme特征分数
        meme_scores = self._calculate_meme_scores(filtered_memes)
        
        # 4. 最终过滤和排序
        final_memes = self._final_filtering(meme_scores)
        
        self.detected_memes = final_memes
        return final_memes
    
    def _identify_potential_memes(self):
        """识别潜在meme"""
        print("识别潜在meme...")
        
        meme_counts = defaultdict(int)
        meme_contexts = defaultdict(list)
        meme_categories = defaultdict(set)
        
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
                        meme_categories[meme_name].add(category)
                        
                        # 记录上下文
                        context = text[max(0, text.find(keyword)-30):text.find(keyword)+len(keyword)+30]
                        meme_contexts[meme_name].append({
                            'user_id': user_id,
                            'context': context.strip(),
                            'timestamp': row.get('created_at', 'unknown'),
                            'category': category
                        })
        
        print(f"识别出 {len(meme_counts)} 个潜在meme")
        return {'counts': meme_counts, 'contexts': meme_contexts, 'categories': meme_categories}
    
    def _filter_mainstream_projects(self, potential_memes):
        """过滤主流项目"""
        print("过滤主流项目...")
        
        meme_counts = potential_memes['counts']
        meme_contexts = potential_memes['contexts']
        meme_categories = potential_memes['categories']
        
        filtered_memes = {}
        
        for meme_name, count in meme_counts.items():
            # 检查是否在黑名单中
            if meme_name.lower() in self.mainstream_blacklist:
                print(f"过滤主流项目: {meme_name}")
                continue
                
            filtered_memes[meme_name] = {
                'mention_count': count,
                'contexts': meme_contexts.get(meme_name, []),
                'categories': list(meme_categories.get(meme_name, [])),
                'total_contexts': len(meme_contexts.get(meme_name, []))
            }
        
        print(f"过滤后剩余 {len(filtered_memes)} 个meme")
        return filtered_memes
    
    def _calculate_meme_scores(self, filtered_memes):
        """计算meme特征分数"""
        print("计算meme特征分数...")
        
        meme_scores = {}
        
        for meme_name, stats in filtered_memes.items():
            score = 0
            
            # 1. 基础分数：提及次数
            base_score = min(stats['mention_count'] / 10, 50)  # 最高50分
            score += base_score
            
            # 2. 类别多样性分数：越多类别分数越高
            category_diversity = len(stats['categories'])
            diversity_score = min(category_diversity * 10, 20)  # 最高20分
            score += diversity_score
            
            # 3. 上下文丰富度分数
            context_richness = min(stats['total_contexts'] / 5, 15)  # 最高15分
            score += context_richness
            
            # 4. Meme特征加成
            meme_bonus = self._calculate_meme_bonus(meme_name, stats)
            score += meme_bonus
            
            meme_scores[meme_name] = {
                **stats,
                'total_score': round(score, 2),
                'base_score': round(base_score, 2),
                'diversity_score': diversity_score,
                'context_score': round(context_richness, 2),
                'meme_bonus': round(meme_bonus, 2)
            }
        
        return meme_scores
    
    def _calculate_meme_bonus(self, meme_name, stats):
        """计算meme特征加成"""
        bonus = 0
        meme_lower = meme_name.lower()
        
        # 动物名称加成
        if any(animal in meme_lower for animal in ['doge', 'shib', 'pepe', 'floki', 'bonk']):
            bonus += 25  # 经典meme币
        elif any(animal in meme_lower for animal in ['cat', 'dog', 'monkey', 'ape', 'frog']):
            bonus += 15  # 动物名称
        
        # 网络文化加成
        if any(culture in meme_lower for culture in ['wojak', 'chad', 'virgin', 'simp', 'incel']):
            bonus += 20  # 网络文化词汇
        
        # 表情包符号加成
        if any(emoji in meme_lower for emoji in ['moon', 'rocket', 'fire', 'based', 'cringe']):
            bonus += 10  # 表情包元素
        
        return bonus
    
    def _final_filtering(self, meme_scores):
        """最终过滤和排序"""
        print("执行最终过滤...")
        
        # 按总分排序
        sorted_memes = sorted(
            meme_scores.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        final_memes = {}
        
        for meme_name, stats in sorted_memes:
            # 过滤条件：总分太低或提及次数太少
            if stats['total_score'] < 20 or stats['mention_count'] < 5:
                continue
                
            final_memes[meme_name] = stats
        
        print(f"最终筛选出 {len(final_memes)} 个高质量meme")
        return final_memes
    
    def print_summary(self):
        """打印检测摘要"""
        if not self.detected_memes:
            print("未检测到任何meme")
            return
        
        print("\n=== Meme检测结果 V2 ===")
        print(f"检测到的meme数量: {len(self.detected_memes)}")
        
        # 按总分排序显示前10名
        sorted_memes = sorted(
            self.detected_memes.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        print("\n=== Top 10 Meme ===")
        for i, (meme_name, stats) in enumerate(sorted_memes[:10], 1):
            categories = ', '.join(stats['categories'])
            print(f"{i}. {meme_name} ({categories})")
            print(f"   总分: {stats['total_score']}, 提及次数: {stats['mention_count']}")
            print(f"   分数构成: 基础{stats['base_score']} + 多样性{stats['diversity_score']} + 上下文{stats['context_score']} + 加成{stats['meme_bonus']}")
            print()
    
    def save_results(self, filename='meme_detection_v2_results.json'):
        """保存检测结果"""
        print(f"保存结果到 {filename}...")
        
        # 准备保存数据
        save_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'detected_memes': self.detected_memes,
            'summary': {
                'total_memes': len(self.detected_memes),
                'detection_method': 'V2 - 专注于真正的meme币',
                'focus': '过滤主流项目，识别真正的meme币'
            }
        }
        
        # 提取meme分数和分类信息
        meme_scores = {}
        meme_categories = {}
        
        for meme_name, stats in self.detected_memes.items():
            meme_scores[meme_name] = stats['total_score']
            meme_categories[meme_name] = stats['categories']
        
        save_data['meme_scores'] = meme_scores
        save_data['meme_categories'] = meme_categories
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")

def main():
    """主函数"""
    print("=== Meme识别系统 V2 ===")
    print("重新设计：专注于真正的meme币")
    print()
    
    # 创建检测器
    detector = MemeDetectorV2()
    
    try:
        # 1. 加载数据
        detector.load_data('sample_tweets.csv')
        
        # 2. 检测Meme
        detected_memes = detector.detect_memes()
        
        # 3. 显示摘要
        detector.print_summary()
        
        # 4. 保存结果
        detector.save_results()
        
        print("\n=== Meme检测 V2 完成 ===")
        print("这次专注于识别真正的meme币，过滤主流项目")
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
