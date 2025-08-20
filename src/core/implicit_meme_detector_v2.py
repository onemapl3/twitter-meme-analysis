#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐性Meme识别系统 V2 - 重新设计
专注于识别还没火的meme币，而不是分析指标
"""

import pandas as pd
import re
from collections import defaultdict, Counter
import json
from datetime import datetime

class ImplicitMemeDetectorV2:
    def __init__(self):
        """初始化隐性Meme检测器 V2"""
        
        # 已知的主流meme币 - 这些不是隐性的
        self.known_memes = {
            'doge', 'shib', 'shiba', 'pepe', 'floki', 'bonk', 'wojak', 'chad', 'virgin',
            'cat', 'monkey', 'ape', 'frog', 'bird', 'fish', 'turtle', 'hamster', 'rabbit'
        }
        
        # 主流项目黑名单
        self.mainstream_blacklist = {
            'bitcoin', 'btc', 'ethereum', 'eth', 'cardano', 'ada', 'solana', 'sol',
            'polkadot', 'dot', 'chainlink', 'link', 'uniswap', 'uni', 'aave',
            'ai', 'blockchain', 'defi', 'nft'
        }
        
        # 新兴meme币特征词汇
        self.emerging_indicators = [
            'new', 'emerging', 'upcoming', 'launch', 'presale', 'fairlaunch',
            'stealth', 'hidden', 'undiscovered', 'gem', 'moon', 'rocket',
            'early', 'og', 'first', 'pioneer', 'innovative', 'revolutionary'
        ]
        
        # 社区讨论词汇
        self.community_words = [
            'community', 'holders', 'diamond hands', 'paper hands', 'hodl',
            'whale', 'shark', 'early', 'veteran', 'newbie', 'rookie'
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
        
        # 1. 挖掘潜在项目名称
        potential_projects = self._extract_potential_projects()
        
        # 2. 分析项目讨论热度
        project_analysis = self._analyze_project_discussion(potential_projects)
        
        # 3. 识别早期信号
        early_signals = self._identify_early_signals(project_analysis)
        
        # 4. 计算潜力分数
        final_memes = self._calculate_potential_scores(early_signals)
        
        self.potential_memes = final_memes
        return final_memes
    
    def _extract_potential_projects(self):
        """挖掘潜在项目名称"""
        print("挖掘潜在项目名称...")
        
        # 项目名称模式
        project_patterns = [
            r'\$[A-Za-z]+',  # $符号开头的项目
            r'#[A-Za-z]+',    # #标签项目
            r'@[A-Za-z0-9_]+', # @提及的项目
            r'\b[A-Z][a-z]+[A-Z][a-z]+\b',  # 驼峰命名的项目
            r'\b[A-Z]{2,}\b',  # 全大写项目
        ]
        
        potential_projects = defaultdict(int)
        project_contexts = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text']
            user_id = row['user_id']
            
            for pattern in project_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # 清理匹配结果
                    clean_match = self._clean_project_name(match)
                    if clean_match and len(clean_match) >= 2:
                        potential_projects[clean_match] += 1
                        
                        # 记录上下文
                        context = text[max(0, text.find(match)-50):text.find(match)+len(match)+50]
                        project_contexts[clean_match].append({
                            'user_id': user_id,
                            'original_match': match,
                            'context': context.strip(),
                            'timestamp': row.get('created_at', 'unknown')
                        })
        
        print(f"挖掘出 {len(potential_projects)} 个潜在项目")
        return {'projects': potential_projects, 'contexts': project_contexts}
    
    def _clean_project_name(self, name):
        """清理项目名称"""
        # 移除符号
        clean_name = re.sub(r'[^\w]', '', name)
        
        # 过滤太短或太长的名称
        if len(clean_name) < 2 or len(clean_name) > 20:
            return None
            
        # 过滤纯数字
        if clean_name.isdigit():
            return None
            
        # 过滤已知的主流项目
        if clean_name.lower() in self.mainstream_blacklist:
            return None
            
        # 过滤已知的meme币
        if clean_name.lower() in self.known_memes:
            return None
            
        return clean_name.lower()
    
    def _analyze_project_discussion(self, potential_projects):
        """分析项目讨论热度"""
        print("分析项目讨论热度...")
        
        projects = potential_projects['projects']
        contexts = potential_projects['contexts']
        
        project_analysis = {}
        
        for project_name, count in projects.items():
            if count < 3:  # 至少被讨论3次
                continue
                
            project_contexts = contexts.get(project_name, [])
            
            # 分析讨论特征
            analysis = {
                'mention_count': count,
                'unique_users': len(set(ctx['user_id'] for ctx in project_contexts)),
                'contexts': project_contexts[:5],  # 前5个上下文
                'total_contexts': len(project_contexts)
            }
            
            # 检查是否包含新兴指标词汇
            emerging_score = 0
            community_score = 0
            
            for ctx in project_contexts:
                text = ctx['context'].lower()
                
                # 新兴指标分数
                for word in self.emerging_indicators:
                    if word in text:
                        emerging_score += 1
                
                # 社区词汇分数
                for word in self.community_words:
                    if word in text:
                        community_score += 1
            
            analysis['emerging_score'] = emerging_score
            analysis['community_score'] = community_score
            
            project_analysis[project_name] = analysis
        
        print(f"分析了 {len(project_analysis)} 个项目的讨论热度")
        return project_analysis
    
    def _identify_early_signals(self, project_analysis):
        """识别早期信号"""
        print("识别早期信号...")
        
        early_signals = {}
        
        for project_name, analysis in project_analysis.items():
            # 早期信号判断条件
            is_early = (
                analysis['mention_count'] >= 3 and  # 有一定讨论量
                analysis['mention_count'] <= 50 and  # 但不太热门
                analysis['unique_users'] >= 2 and    # 多个用户讨论
                analysis['unique_users'] <= 20       # 但用户不太多
            )
            
            if is_early:
                early_signals[project_name] = analysis
        
        print(f"识别出 {len(early_signals)} 个早期信号项目")
        return early_signals
    
    def _calculate_potential_scores(self, early_signals):
        """计算潜力分数"""
        print("计算潜力分数...")
        
        final_memes = {}
        
        for project_name, analysis in early_signals.items():
            # 潜力分数计算
            base_score = min(analysis['mention_count'] * 2, 100)  # 基础分数
            user_diversity = min(analysis['unique_users'] * 5, 50)  # 用户多样性
            emerging_bonus = min(analysis['emerging_score'] * 10, 30)  # 新兴指标加成
            community_bonus = min(analysis['community_score'] * 5, 20)  # 社区词汇加成
            
            total_score = base_score + user_diversity + emerging_bonus + community_bonus
            
            final_memes[project_name] = {
                **analysis,
                'total_score': total_score,
                'score_breakdown': {
                    'base_score': base_score,
                    'user_diversity': user_diversity,
                    'emerging_bonus': emerging_bonus,
                    'community_bonus': community_bonus
                }
            }
        
        # 按总分排序
        sorted_memes = sorted(
            final_memes.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        # 只保留前20名
        top_memes = {}
        for project_name, data in sorted_memes[:20]:
            top_memes[project_name] = data
        
        print(f"筛选出 {len(top_memes)} 个高潜力隐性meme币")
        return top_memes
    
    def print_summary(self):
        """打印检测摘要"""
        if not self.potential_memes:
            print("未检测到任何潜在meme币")
            return
        
        print("\n=== 隐性Meme币检测结果 ===")
        print(f"检测到的潜在meme币数量: {len(self.potential_memes)}")
        
        # 按总分排序显示
        sorted_memes = sorted(
            self.potential_memes.items(), 
            key=lambda x: x[1]['total_score'], 
            reverse=True
        )
        
        print("\n=== Top 20 潜在Meme币 ===")
        for i, (project_name, data) in enumerate(sorted_memes, 1):
            print(f"{i:2d}. {project_name:15s} - 总分: {data['total_score']:3d}")
            print(f"    提及次数: {data['mention_count']:3d}, 用户数: {data['unique_users']:2d}")
            print(f"    新兴指标: {data['emerging_score']:2d}, 社区词汇: {data['community_score']:2d}")
            
            # 显示示例上下文
            if data['contexts']:
                sample_context = data['contexts'][0]['context'][:80]
                print(f"    示例: {sample_context}...")
            print()
    
    def save_results(self, filename='implicit_meme_detection_v2_results.json'):
        """保存检测结果"""
        print(f"保存结果到 {filename}...")
        
        save_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'potential_memes': self.potential_memes,
            'summary': {
                'total_projects': len(self.potential_memes),
                'detection_method': '挖掘还没火的meme币',
                'focus': '具体项目名称而非分析指标'
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")

def main():
    """主函数"""
    print("=== 隐性Meme识别系统 V2 ===")
    print("重新设计：专注于识别还没火的meme币")
    print()
    
    # 创建检测器
    detector = ImplicitMemeDetectorV2()
    
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
        
        print("\n=== 隐性Meme币检测完成 ===")
        print("这次专注于识别具体的、还没火的meme币项目")
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
