#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐性Meme识别系统 V3 - 最终优化版
专注于识别带$符号且具有meme币特征的项目
"""

import pandas as pd
import re
from collections import defaultdict, Counter
import json
from datetime import datetime

class ImplicitMemeDetectorV3:
    def __init__(self):
        """初始化隐性Meme检测器 V3"""
        
        # 已知的主流meme币 - 这些不是隐性的
        self.known_memes = {
            'doge', 'shib', 'shiba', 'pepe', 'floki', 'bonk', 'wojak', 'chad', 'virgin',
            'cat', 'monkey', 'ape', 'frog', 'bird', 'fish', 'turtle', 'hamster', 'rabbit'
        }
        
        # 主流项目黑名单
        self.mainstream_blacklist = {
            'bitcoin', 'btc', 'ethereum', 'eth', 'cardano', 'ada', 'solana', 'sol',
            'polkadot', 'dot', 'chainlink', 'link', 'uniswap', 'uni', 'aave',
            'ai', 'blockchain', 'defi', 'nft', 'usdc', 'usdt', 'busd', 'dai'
        }
        
        # 通用词汇黑名单 - 这些明显不是meme币
        self.generic_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them',
            'it', 'to', 'on', 'in', 'at', 'for', 'of', 'with', 'by', 'from',
            'breaking', 'news', 'update', 'announcement', 'launch', 'release',
            'tge', 'ido', 'ico', 'presale', 'fairlaunch', 'stealth'
        }
        
        # Meme币特征词汇 - 暗示真正的meme币
        self.meme_indicators = [
            'moon', 'rocket', 'mars', 'jupiter', 'galaxy', 'star', 'planet',
            'diamond', 'gem', 'gold', 'silver', 'platinum', 'emerald',
            'fire', 'lit', 'based', 'cringe', 'sus', 'amogus', 'among us',
            'wojak', 'chad', 'virgin', 'simp', 'incel', 'normie', 'weeb',
            'doge', 'shib', 'pepe', 'floki', 'bonk', 'wojak', 'chad', 'virgin'
        ]
        
        # 社区讨论词汇
        self.community_words = [
            'community', 'holders', 'diamond hands', 'paper hands', 'hodl',
            'whale', 'shark', 'early', 'veteran', 'newbie', 'rookie', 'og',
            'fam', 'family', 'team', 'crew', 'gang', 'squad'
        ]
        
        self.potential_memes = {}
        
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
        
    def detect_implicit_memes(self):
        """检测隐性Meme币"""
        print("开始检测隐性Meme币...")
        
        # 1. 识别带$符号的项目
        dollar_projects = self._extract_dollar_projects()
        
        # 2. 分析项目特征和语境
        project_analysis = self._analyze_project_features(dollar_projects)
        
        # 3. 识别真正的meme币
        meme_projects = self._identify_real_memes(project_analysis)
        
        # 4. 计算潜力分数
        final_memes = self._calculate_meme_potential(meme_projects)
        
        self.potential_memes = final_memes
        return final_memes
    
    def _extract_dollar_projects(self):
        """提取带$符号的项目"""
        print("提取带$符号的项目...")
        
        dollar_projects = defaultdict(int)
        project_contexts = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text']
            user_id = row['user_id']
            
            # 专门识别$符号开头的项目
            dollar_pattern = r'\$([A-Za-z][A-Za-z0-9]*)'
            matches = re.findall(dollar_pattern, text)
            
            for match in matches:
                project_name = match.lower()
                
                # 基础过滤
                if self._is_valid_meme_candidate(project_name):
                    dollar_projects[project_name] += 1
                    
                    # 记录上下文
                    context = text[max(0, text.find(f'${match}')-60):text.find(f'${match}')+len(match)+60]
                    project_contexts[project_name].append({
                        'user_id': user_id,
                        'full_match': f'${match}',
                        'context': context.strip(),
                        'timestamp': row.get('created_at', 'unknown')
                    })
        
        print(f"提取出 {len(dollar_projects)} 个带$符号的项目")
        return {'projects': dollar_projects, 'contexts': project_contexts}
    
    def _is_valid_meme_candidate(self, project_name):
        """判断是否为有效的meme币候选"""
        # 过滤太短或太长的名称
        if len(project_name) < 2 or len(project_name) > 15:
            return False
            
        # 过滤纯数字
        if project_name.isdigit():
            return False
            
        # 过滤已知的主流项目
        if project_name in self.mainstream_blacklist:
            return False
            
        # 过滤已知的meme币
        if project_name in self.known_memes:
            return False
            
        # 过滤通用词汇
        if project_name in self.generic_words:
            return False
            
        # 过滤明显的缩写
        if len(project_name) <= 3 and project_name.isupper():
            return False
            
        return True
    
    def _analyze_project_features(self, dollar_projects):
        """分析项目特征和语境"""
        print("分析项目特征和语境...")
        
        projects = dollar_projects['projects']
        contexts = dollar_projects['contexts']
        
        project_analysis = {}
        
        for project_name, count in projects.items():
            if count < 3:  # 至少被讨论3次
                continue
                
            project_contexts = contexts.get(project_name, [])
            
            # 分析特征
            analysis = {
                'mention_count': count,
                'unique_users': len(set(ctx['user_id'] for ctx in project_contexts)),
                'contexts': project_contexts[:5],
                'total_contexts': len(project_contexts)
            }
            
            # 计算meme特征分数
            meme_score = 0
            community_score = 0
            
            for ctx in project_contexts:
                text = ctx['context'].lower()
                
                # Meme特征分数
                for word in self.meme_indicators:
                    if word in text:
                        meme_score += 1
                
                # 社区词汇分数
                for word in self.community_words:
                    if word in text:
                        community_score += 1
            
            analysis['meme_score'] = meme_score
            analysis['community_score'] = community_score
            
            # 计算语境质量分数
            context_quality = self._calculate_context_quality(project_contexts)
            analysis['context_quality'] = context_quality
            
            project_analysis[project_name] = analysis
        
        print(f"分析了 {len(project_analysis)} 个项目的特征")
        return project_analysis
    
    def _calculate_context_quality(self, project_contexts):
        """计算语境质量分数"""
        quality_score = 0
        
        for ctx in project_contexts:
            text = ctx['context'].lower()
            
            # 检查是否在正确的meme币讨论语境中
            meme_context_indicators = [
                'price', 'value', 'market', 'trading', 'buy', 'sell', 'hold',
                'moon', 'rocket', 'pump', 'dump', 'fomo', 'fud', 'gem',
                'community', 'holders', 'whale', 'early', 'og'
            ]
            
            for indicator in meme_context_indicators:
                if indicator in text:
                    quality_score += 1
        
        return quality_score
    
    def _identify_real_memes(self, project_analysis):
        """识别真正的meme币"""
        print("识别真正的meme币...")
        
        real_memes = {}
        
        for project_name, analysis in project_analysis.items():
            # 判断是否为真正的meme币
            is_real_meme = (
                analysis['mention_count'] >= 3 and      # 有一定讨论量
                analysis['mention_count'] <= 100 and    # 但不太热门
                analysis['unique_users'] >= 2 and       # 多个用户讨论
                analysis['unique_users'] <= 30 and      # 但用户不太多
                analysis['meme_score'] >= 2 and         # 有明显的meme特征
                analysis['context_quality'] >= 3        # 语境质量较高
            )
            
            if is_real_meme:
                real_memes[project_name] = analysis
        
        print(f"识别出 {len(real_memes)} 个真正的meme币")
        return real_memes
    
    def _calculate_meme_potential(self, meme_projects):
        """计算meme币潜力分数"""
        print("计算meme币潜力分数...")
        
        final_memes = {}
        
        for project_name, analysis in meme_projects.items():
            # 潜力分数计算
            base_score = min(analysis['mention_count'] * 2, 100)      # 基础分数
            user_diversity = min(analysis['unique_users'] * 5, 50)    # 用户多样性
            meme_feature = min(analysis['meme_score'] * 15, 45)       # meme特征分数
            community_feature = min(analysis['community_score'] * 10, 30)  # 社区特征
            context_quality = min(analysis['context_quality'] * 5, 25)     # 语境质量
            
            total_score = base_score + user_diversity + meme_feature + community_feature + context_quality
            
            final_memes[project_name] = {
                **analysis,
                'total_score': total_score,
                'score_breakdown': {
                    'base_score': base_score,
                    'user_diversity': user_diversity,
                    'meme_feature': meme_feature,
                    'community_feature': community_feature,
                    'context_quality': context_quality
                }
            }
        
        # 按总分排序，只保留前15名
        sorted_memes = sorted(
            final_memes.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        top_memes = {}
        for project_name, data in sorted_memes[:15]:
            top_memes[project_name] = data
        
        print(f"筛选出 {len(top_memes)} 个高潜力meme币")
        return top_memes
    
    def print_summary(self):
        """打印检测摘要"""
        if not self.potential_memes:
            print("未检测到任何潜在meme币")
            return
        
        print("\n=== 隐性Meme币检测结果 V3 ===")
        print(f"检测到的潜在meme币数量: {len(self.potential_memes)}")
        
        # 按总分排序显示
        sorted_memes = sorted(
            self.potential_memes.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        print("\n=== Top 15 潜在Meme币 ===")
        for i, (project_name, data) in enumerate(sorted_memes, 1):
            print(f"{i:2d}. ${project_name:15s} - 总分: {data['total_score']:3d}")
            print(f"    提及次数: {data['mention_count']:3d}, 用户数: {data['unique_users']:2d}")
            print(f"    Meme特征: {data['meme_score']:2d}, 社区特征: {data['community_score']:2d}, 语境质量: {data['context_quality']:2d}")
            
            # 显示示例上下文
            if data['contexts']:
                sample_context = data['contexts'][0]['context'][:80]
                print(f"    示例: {sample_context}...")
            print()
    
    def save_results(self, filename='implicit_meme_detection_v3_results.json'):
        """保存检测结果"""
        print(f"保存结果到 {filename}...")
        
        save_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'potential_memes': self.potential_memes,
            'summary': {
                'total_projects': len(self.potential_memes),
                'detection_method': '带$符号的meme币识别',
                'focus': '真正的meme币项目，过滤通用词汇和公司名'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")

def main():
    """主函数"""
    print("=== 隐性Meme识别系统 V3 ===")
    print("最终优化：专注于识别带$符号且具有meme币特征的项目")
    print()
    
    # 创建检测器
    detector = ImplicitMemeDetectorV3()
    
    try:
        # 1. 加载数据
        from config.paths import TWEETS_FILE
        detector.load_data(str(TWEETS_FILE))
        
        # 2. 检测隐性Meme币
        potential_memes = detector.detect_implicit_memes()
        
        # 3. 显示摘要
        detector.print_summary()
        
        # 4. 保存结果
        detector.save_results()
        
        print("\n=== 隐性Meme币检测完成 V3 ===")
        print("这次专注于识别真正的meme币项目，过滤通用词汇和公司名")
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
