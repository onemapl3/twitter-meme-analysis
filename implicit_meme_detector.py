#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐性Meme识别系统 - 任务4实现
识别通过上下文、语言模式、情感表达暗示的meme信息
"""

import pandas as pd
import re
from collections import defaultdict, Counter
import json
from datetime import datetime
import numpy as np

class ImplicitMemeDetector:
    def __init__(self):
        """初始化隐性Meme检测器"""
        
        # 语言模式关键词 - 暗示meme的趋势
        self.pattern_keywords = {
            'trending_indicators': [
                'trending', 'viral', 'blowing up', 'mooning', 'pumping', 'fomo', 'fud',
                'next big thing', 'hidden gem', 'undervalued', 'moon shot', 'rocket',
                'to the moon', 'moon mission', 'space travel', 'galaxy brain'
            ],
            'community_signals': [
                'community', 'fam', 'family', 'holders', 'diamond hands', 'paper hands',
                'hodl', 'hodler', 'strong hands', 'weak hands', 'whale', 'shark',
                'early', 'og', 'veteran', 'newbie', 'rookie', 'pro'
            ],
            'emotional_expressions': [
                'based', 'cringe', 'sus', 'lit', 'fire', 'savage', 'epic', 'legendary',
                'insane', 'crazy', 'wild', 'nuts', 'bonkers', 'mental', 'psycho'
            ],
            'timing_indicators': [
                'early', 'late', 'missed', 'opportunity', 'timing', 'perfect time',
                'now or never', 'last chance', 'final call', 'deadline', 'countdown'
            ]
        }
        
        # 情感词汇库
        self.emotion_words = {
            'positive': ['love', 'amazing', 'incredible', 'fantastic', 'brilliant', 'genius', 'perfect'],
            'negative': ['hate', 'terrible', 'awful', 'horrible', 'disaster', 'scam', 'rug'],
            'excitement': ['wow', 'omg', 'holy', 'damn', 'shit', 'fuck', 'crazy'],
            'fear': ['scared', 'worried', 'nervous', 'anxious', 'panic', 'fear', 'dread']
        }
        
        # 上下文暗示模式
        self.context_patterns = {
            'price_movement': [r'\$[0-9]+', r'price', r'value', r'market cap', r'volume'],
            'social_activity': [r'followers', r'engagement', r'viral', r'trending', r'popular'],
            'time_references': [r'today', r'yesterday', r'this week', r'this month', r'recently'],
            'comparison_words': [r'better than', r'worse than', r'similar to', r'unlike', r'compared to']
        }
        
        self.implicit_memes = {}
        
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
        """检测隐性Meme"""
        print("开始检测隐性Meme...")
        
        # 1. 语言模式分析
        pattern_analysis = self._analyze_language_patterns()
        
        # 2. 情感分析
        emotion_analysis = self._analyze_emotions()
        
        # 3. 趋势暗示检测
        trend_analysis = self._detect_trend_implications()
        
        # 4. 上下文暗示分析
        context_analysis = self._analyze_context_implications()
        
        # 5. 综合评分和筛选
        implicit_memes = self._combine_analyses(
            pattern_analysis, emotion_analysis, trend_analysis, context_analysis
        )
        
        self.implicit_memes = implicit_memes
        return implicit_memes
    
    def _analyze_language_patterns(self):
        """语言模式分析"""
        print("执行语言模式分析...")
        
        pattern_scores = defaultdict(int)
        pattern_contexts = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text'].lower()
            user_id = row['user_id']
            
            # 分析各种语言模式
            for pattern_type, keywords in self.pattern_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        pattern_scores[pattern_type] += 1
                        
                        # 记录上下文
                        context = text[max(0, text.find(keyword)-40):text.find(keyword)+len(keyword)+40]
                        pattern_contexts[pattern_type].append({
                            'user_id': user_id,
                            'keyword': keyword,
                            'context': context.strip(),
                            'timestamp': row.get('created_at', 'unknown')
                        })
        
        print(f"语言模式分析完成，发现 {len(pattern_scores)} 种模式")
        return {'scores': pattern_scores, 'contexts': pattern_contexts}
    
    def _analyze_emotions(self):
        """情感分析"""
        print("执行情感分析...")
        
        emotion_scores = defaultdict(int)
        emotion_contexts = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text'].lower()
            user_id = row['user_id']
            
            # 分析各种情感
            for emotion_type, words in self.emotion_words.items():
                for word in words:
                    if word in text:
                        emotion_scores[emotion_type] += 1
                        
                        # 记录情感上下文
                        context = text[max(0, text.find(word)-30):text.find(word)+len(word)+30]
                        emotion_contexts[emotion_type].append({
                            'user_id': user_id,
                            'emotion_word': word,
                            'context': context.strip(),
                            'timestamp': row.get('created_at', 'unknown')
                        })
        
        print(f"情感分析完成，发现 {len(emotion_scores)} 种情感类型")
        return {'scores': emotion_scores, 'contexts': emotion_contexts}
    
    def _detect_trend_implications(self):
        """趋势暗示检测"""
        print("执行趋势暗示检测...")
        
        trend_indicators = defaultdict(int)
        trend_contexts = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text'].lower()
            user_id = row['user_id']
            
            # 检测趋势暗示词汇
            trend_words = [
                'trending', 'viral', 'blowing up', 'mooning', 'pumping', 'fomo',
                'next big thing', 'hidden gem', 'undervalued', 'moon shot'
            ]
            
            for word in trend_words:
                if word in text:
                    trend_indicators[word] += 1
                    
                    # 记录趋势上下文
                    context = text[max(0, text.find(word)-50):text.find(word)+len(word)+50]
                    trend_contexts[word].append({
                        'user_id': user_id,
                        'trend_word': word,
                        'context': context.strip(),
                        'timestamp': row.get('created_at', 'unknown')
                    })
        
        print(f"趋势暗示检测完成，发现 {len(trend_indicators)} 个趋势指标")
        return {'indicators': trend_indicators, 'contexts': trend_contexts}
    
    def _analyze_context_implications(self):
        """上下文暗示分析"""
        print("执行上下文暗示分析...")
        
        context_scores = defaultdict(int)
        context_examples = defaultdict(list)
        
        for idx, row in self.tweets_df.iterrows():
            text = row['text'].lower()
            user_id = row['user_id']
            
            # 分析各种上下文模式
            for context_type, patterns in self.context_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        context_scores[context_type] += len(matches)
                        
                        # 记录上下文示例
                        context_examples[context_type].append({
                            'user_id': user_id,
                            'pattern': pattern,
                            'matches': matches,
                            'full_text': text[:100],  # 前100个字符
                            'timestamp': row.get('created_at', 'unknown')
                        })
        
        print(f"上下文暗示分析完成，发现 {len(context_scores)} 种上下文模式")
        return {'scores': context_scores, 'examples': context_examples}
    
    def _combine_analyses(self, pattern_analysis, emotion_analysis, trend_analysis, context_analysis):
        """综合分析和评分"""
        print("综合分析和评分...")
        
        # 计算综合分数
        combined_scores = {}
        
        # 1. 语言模式分数
        for pattern_type, score in pattern_analysis['scores'].items():
            combined_scores[f"pattern_{pattern_type}"] = {
                'type': 'language_pattern',
                'score': score,
                'contexts': pattern_analysis['contexts'].get(pattern_type, [])[:3]
            }
        
        # 2. 情感分析分数
        for emotion_type, score in emotion_analysis['scores'].items():
            combined_scores[f"emotion_{emotion_type}"] = {
                'type': 'emotion',
                'score': score,
                'contexts': emotion_analysis['contexts'].get(emotion_type, [])[:3]
            }
        
        # 3. 趋势暗示分数
        for trend_word, score in trend_analysis['indicators'].items():
            combined_scores[f"trend_{trend_word}"] = {
                'type': 'trend_indicator',
                'score': score,
                'contexts': trend_analysis['contexts'].get(trend_word, [])[:3]
            }
        
        # 4. 上下文暗示分数
        for context_type, score in context_analysis['scores'].items():
            combined_scores[f"context_{context_type}"] = {
                'type': 'context_implication',
                'score': score,
                'examples': context_analysis['examples'].get(context_type, [])[:3]
            }
        
        # 按分数排序
        sorted_scores = sorted(
            combined_scores.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        # 筛选高分项目
        high_score_items = {}
        for item_name, item_data in sorted_scores:
            if item_data['score'] >= 5:  # 至少5次出现
                high_score_items[item_name] = item_data
        
        print(f"综合评分完成，筛选出 {len(high_score_items)} 个高分隐性meme指标")
        return high_score_items
    
    def print_summary(self):
        """打印检测摘要"""
        if not self.implicit_memes:
            print("未检测到任何隐性meme指标")
            return
        
        print("\n=== 隐性Meme检测结果 ===")
        print(f"检测到的隐性meme指标数量: {len(self.implicit_memes)}")
        
        # 按分数排序显示前15名
        sorted_items = sorted(
            self.implicit_memes.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        print("\n=== Top 15 隐性Meme指标 ===")
        for i, (item_name, item_data) in enumerate(sorted_items[:15], 1):
            print(f"{i}. {item_name} ({item_data['type']}) - 分数: {item_data['score']}")
            
            # 显示示例上下文
            if 'contexts' in item_data and item_data['contexts']:
                sample_context = item_data['contexts'][0]
                if 'context' in sample_context:
                    print(f"   示例: {sample_context['context'][:80]}...")
                elif 'full_text' in sample_context:
                    print(f"   示例: {sample_context['full_text'][:80]}...")
            print()
    
    def save_results(self, filename='implicit_meme_detection_results.json'):
        """保存检测结果"""
        print(f"保存结果到 {filename}...")
        
        save_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'implicit_memes': self.implicit_memes,
            'summary': {
                'total_indicators': len(self.implicit_memes),
                'pattern_types': len([k for k, v in self.implicit_memes.items() if v['type'] == 'language_pattern']),
                'emotion_types': len([k for k, v in self.implicit_memes.items() if v['type'] == 'emotion']),
                'trend_indicators': len([k for k, v in self.implicit_memes.items() if v['type'] == 'trend_indicator']),
                'context_implications': len([k for k, v in self.implicit_memes.items() if v['type'] == 'context_implication'])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")

def main():
    """主函数"""
    print("=== 隐性Meme识别系统 ===")
    print("任务4: 隐性Meme识别")
    print()
    
    # 创建检测器
    detector = ImplicitMemeDetector()
    
    try:
        # 1. 加载数据
        detector.load_data('sample_tweets.csv')
        
        # 2. 检测隐性Meme
        implicit_memes = detector.detect_implicit_memes()
        
        # 3. 显示摘要
        detector.print_summary()
        
        # 4. 保存结果
        detector.save_results()
        
        print("\n=== 隐性Meme检测完成 ===")
        print("成功识别通过语言模式、情感表达、趋势暗示等方式体现的meme信息")
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
