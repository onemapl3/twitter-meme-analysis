#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Meme检测系统
增加更多meme币种类，提供完整项目信息，改进检测算法
"""

import pandas as pd
import re
import json
from collections import defaultdict, Counter
from datetime import datetime
import requests
import time

class EnhancedMemeDetector:
    def __init__(self):
        """初始化增强版Meme检测器"""
        
        # 扩展的meme币数据库
        self.meme_database = {
            # 经典动物meme币
            'doge': {
                'symbol': 'DOGE',
                'name': 'Dogecoin',
                'category': 'animal_meme',
                'founded': '2013',
                'description': '基于柴犬meme的原创meme币',
                'social': {'twitter': '@dogecoin', 'website': 'dogecoin.com'}
            },
            'shib': {
                'symbol': 'SHIB',
                'name': 'Shiba Inu',
                'category': 'animal_meme',
                'founded': '2020',
                'description': 'Dogecoin杀手，柴犬主题',
                'social': {'twitter': '@Shibtoken', 'website': 'shibatoken.com'}
            },
            'pepe': {
                'symbol': 'PEPE',
                'name': 'Pepe',
                'category': 'internet_culture',
                'founded': '2023',
                'description': '基于Pepe青蛙meme的代币',
                'social': {'twitter': '@pepecoineth', 'website': 'pepe.vip'}
            },
            'floki': {
                'symbol': 'FLOKI',
                'name': 'Floki Inu',
                'category': 'animal_meme',
                'founded': '2021',
                'description': '埃隆马斯克的狗狗主题meme币',
                'social': {'twitter': '@RealFlokiInu', 'website': 'floki.com'}
            },
            'bonk': {
                'symbol': 'BONK',
                'name': 'Bonk',
                'category': 'animal_meme',
                'founded': '2022',
                'description': 'Solana生态的柴犬meme币',
                'social': {'twitter': '@bonk_inu', 'website': 'bonkcoin.com'}
            },
            
            # 新兴meme币
            'wojak': {
                'symbol': 'WOJAK',
                'name': 'Wojak',
                'category': 'internet_culture',
                'founded': '2023',
                'description': '基于Wojak meme形象的代币',
                'social': {'twitter': '@WojakCoin', 'website': 'wojak.finance'}
            },
            'chad': {
                'symbol': 'CHAD',
                'name': 'Chad',
                'category': 'internet_culture',
                'founded': '2023',
                'description': '基于Chad meme的代币',
                'social': {'twitter': '@ChadCoinBSC', 'website': 'chadcoin.io'}
            },
            'mog': {
                'symbol': 'MOG',
                'name': 'Mog Coin',
                'category': 'animal_meme',
                'founded': '2023',
                'description': '猫咪主题meme币',
                'social': {'twitter': '@MogCoinEth', 'website': 'mogcoin.org'}
            },
            'wif': {
                'symbol': 'WIF',
                'name': 'Dogwifhat',
                'category': 'animal_meme',
                'founded': '2023',
                'description': '戴帽子的狗狗meme币',
                'social': {'twitter': '@dogwifhat', 'website': 'dogwifhat.com'}
            },
            'popcat': {
                'symbol': 'POPCAT',
                'name': 'Popcat',
                'category': 'animal_meme',
                'founded': '2023',
                'description': '基于Popcat meme的代币',
                'social': {'twitter': '@PopcatSol', 'website': 'popcat.click'}
            },
            
            # AI和科技主题meme币
            'goat': {
                'symbol': 'GOAT',
                'name': 'Goatseus Maximus',
                'category': 'ai_meme',
                'founded': '2024',
                'description': 'AI生成的meme币',
                'social': {'twitter': '@GoatseusMaximus', 'website': 'goat.ai'}
            },
            'act': {
                'symbol': 'ACT',
                'name': 'Act I The AI Prophecy',
                'category': 'ai_meme',
                'founded': '2024',
                'description': 'AI主题的叙事meme币',
                'social': {'twitter': '@ActTheAI', 'website': 'act.ai'}
            },
            
            # 社区驱动meme币
            'book': {
                'symbol': 'BOOK',
                'name': 'Book of Meme',
                'category': 'community_meme',
                'founded': '2024',
                'description': 'meme文化百科全书',
                'social': {'twitter': '@BookOfMeme', 'website': 'bookofmeme.com'}
            },
            'neiro': {
                'symbol': 'NEIRO',
                'name': 'Neiro',
                'category': 'animal_meme',
                'founded': '2024',
                'description': 'Doge继承者，新柴犬meme币',
                'social': {'twitter': '@NeiroEthereum', 'website': 'neiro.dog'}
            },
            
            # 最新热门meme币
            'pnut': {
                'symbol': 'PNUT',
                'name': 'Peanut the Squirrel',
                'category': 'animal_meme',
                'founded': '2024',
                'description': '花生松鼠meme币',
                'social': {'twitter': '@PnutSolana', 'website': 'pnut.meme'}
            },
            'chillguy': {
                'symbol': 'CHILLGUY',
                'name': 'Chill Guy',
                'category': 'internet_culture',
                'founded': '2024',
                'description': '淡定哥meme币',
                'social': {'twitter': '@ChillGuyMeme', 'website': 'chillguy.fun'}
            }
        }
        
        # 扩展搜索模式
        self.search_patterns = {
            # 直接代币符号
            'token_symbols': r'\$([A-Z]{2,10})\b',
            # meme币名称
            'meme_names': r'\b(' + '|'.join(self.meme_database.keys()) + r')\b',
            # 新项目模式
            'new_projects': r'\$([a-zA-Z][a-zA-Z0-9]{1,15})\b',
            # 社区词汇
            'community_signals': r'\b(gem|moon|rocket|diamond|hands|hodl|ape|fomo|fud)\b',
            # 价格相关
            'price_signals': r'\b(pump|dump|x100|x1000|ATH|ATL|bullish|bearish)\b'
        }
        
        self.detected_memes = {}
        
    def load_data(self, tweets_file):
        """加载推文数据"""
        print("加载推文数据...")
        
        # 分块读取
        chunks = []
        for chunk in pd.read_csv(tweets_file, chunksize=10000):
            chunks.append(chunk)
        
        self.tweets_df = pd.concat(chunks, ignore_index=True)
        print(f"加载了 {len(self.tweets_df)} 条推文")
        
        # 数据清理
        self.tweets_df = self.tweets_df.dropna(subset=['text'])
        self.tweets_df['text'] = self.tweets_df['text'].astype(str)
        
    def detect_enhanced_memes(self):
        """增强版meme检测"""
        print("开始增强版meme检测...")
        
        # 1. 检测已知meme币
        known_memes = self._detect_known_memes()
        
        # 2. 发现潜在新meme币
        potential_memes = self._discover_potential_memes()
        
        # 3. 合并结果并评分
        all_memes = self._merge_and_score(known_memes, potential_memes)
        
        # 4. 获取项目详细信息
        enhanced_memes = self._enhance_with_project_info(all_memes)
        
        self.detected_memes = enhanced_memes
        return enhanced_memes
    
    def _detect_known_memes(self):
        """检测已知meme币"""
        print("检测已知meme币...")
        
        known_results = {}
        
        for meme_key, meme_info in self.meme_database.items():
            mentions = []
            contexts = []
            
            # 搜索meme名称和符号
            search_terms = [meme_key, meme_info['symbol'].lower(), meme_info['name'].lower()]
            
            for _, row in self.tweets_df.iterrows():
                text = row['text'].lower()
                
                for term in search_terms:
                    if term in text:
                        mentions.append({
                            'user_id': row['user_id'],
                            'text': row['text'][:200],
                            'timestamp': row.get('created_at', 'unknown'),
                            'matched_term': term
                        })
                        contexts.append(text)
                        break
            
            if mentions:
                # 计算热度分数
                mention_count = len(mentions)
                unique_users = len(set(m['user_id'] for m in mentions))
                
                # 分析上下文情感
                positive_signals = sum(1 for ctx in contexts if any(word in ctx for word in ['moon', 'rocket', 'gem', 'bullish', 'pump']))
                negative_signals = sum(1 for ctx in contexts if any(word in ctx for word in ['dump', 'bearish', 'fud', 'rug']))
                
                sentiment_score = (positive_signals - negative_signals) / len(contexts) if contexts else 0
                
                # 综合评分
                total_score = (
                    mention_count * 0.4 +
                    unique_users * 0.3 +
                    sentiment_score * 100 * 0.3
                )
                
                known_results[meme_key] = {
                    **meme_info,
                    'mention_count': mention_count,
                    'unique_users': unique_users,
                    'sentiment_score': sentiment_score,
                    'total_score': total_score,
                    'sample_mentions': mentions[:5],
                    'detection_type': 'known_meme'
                }
        
        print(f"检测到 {len(known_results)} 个已知meme币")
        return known_results
    
    def _discover_potential_memes(self):
        """发现潜在新meme币"""
        print("发现潜在新meme币...")
        
        potential_results = {}
        token_mentions = defaultdict(list)
        
        # 使用正则表达式查找$符号代币
        for _, row in self.tweets_df.iterrows():
            text = row['text']
            
            # 查找$符号代币
            matches = re.findall(self.search_patterns['token_symbols'], text)
            for match in matches:
                if len(match) >= 2 and len(match) <= 10:  # 合理的代币符号长度
                    token_mentions[match.upper()].append({
                        'user_id': row['user_id'],
                        'text': text[:200],
                        'timestamp': row.get('created_at', 'unknown')
                    })
        
        # 过滤和评分
        for token, mentions in token_mentions.items():
            mention_count = len(mentions)
            unique_users = len(set(m['user_id'] for m in mentions))
            
            # 只考虑有一定讨论量的代币
            if mention_count >= 3 and unique_users >= 2:
                # 检查是否是已知主流币
                mainstream_tokens = {'BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'LINK', 'UNI', 'AAVE', 'USDT', 'USDC'}
                if token not in mainstream_tokens and token not in [info['symbol'] for info in self.meme_database.values()]:
                    
                    # 分析上下文
                    contexts = [m['text'].lower() for m in mentions]
                    
                    # meme特征检测
                    meme_signals = sum(1 for ctx in contexts if any(word in ctx for word in [
                        'meme', 'moon', 'rocket', 'gem', 'ape', 'diamond', 'hands', 'hodl'
                    ]))
                    
                    # 社区活跃度
                    community_signals = sum(1 for ctx in contexts if any(word in ctx for word in [
                        'community', 'holders', 'family', 'team', 'squad', 'gang'
                    ]))
                    
                    # 计算潜力分数
                    potential_score = (
                        mention_count * 2 +
                        unique_users * 5 +
                        meme_signals * 10 +
                        community_signals * 8
                    )
                    
                    if potential_score >= 20:  # 设置阈值
                        potential_results[token.lower()] = {
                            'symbol': token,
                            'name': f'Unknown Token ({token})',
                            'category': 'potential_meme',
                            'founded': '2024',
                            'description': f'新发现的潜在meme币 ${token}',
                            'social': {'twitter': 'Unknown', 'website': 'Unknown'},
                            'mention_count': mention_count,
                            'unique_users': unique_users,
                            'meme_signals': meme_signals,
                            'community_signals': community_signals,
                            'total_score': potential_score,
                            'sample_mentions': mentions[:5],
                            'detection_type': 'potential_meme'
                        }
        
        print(f"发现 {len(potential_results)} 个潜在新meme币")
        return potential_results
    
    def _merge_and_score(self, known_memes, potential_memes):
        """合并结果并重新评分"""
        print("合并结果并重新评分...")
        
        all_memes = {**known_memes, **potential_memes}
        
        # 按总分排序
        sorted_memes = sorted(all_memes.items(), key=lambda x: x[1]['total_score'], reverse=True)
        
        # 只保留前30名
        return dict(sorted_memes[:30])
    
    def _enhance_with_project_info(self, memes):
        """增强项目信息"""
        print("增强项目信息...")
        
        enhanced = {}
        
        for meme_key, meme_data in memes.items():
            # 为已知meme币添加更多信息
            if meme_data['detection_type'] == 'known_meme':
                enhanced[meme_key] = {
                    **meme_data,
                    'market_cap': 'Unknown',  # 可以集成CoinGecko API
                    'price_change_24h': 'Unknown',
                    'volume_24h': 'Unknown',
                    'rank': 'Unknown'
                }
            else:
                # 为潜在meme币尝试获取更多信息
                enhanced[meme_key] = {
                    **meme_data,
                    'market_cap': 'New/Unknown',
                    'price_change_24h': 'Unknown',
                    'volume_24h': 'Unknown',
                    'rank': 'Unranked'
                }
        
        return enhanced
    
    def print_enhanced_summary(self):
        """打印增强版摘要"""
        if not self.detected_memes:
            print("未检测到任何meme币")
            return
        
        print(f"\n=== 增强版Meme币检测结果 ===")
        print(f"检测到的meme币总数: {len(self.detected_memes)}")
        
        # 按类型分组显示
        known_memes = {k: v for k, v in self.detected_memes.items() if v['detection_type'] == 'known_meme'}
        potential_memes = {k: v for k, v in self.detected_memes.items() if v['detection_type'] == 'potential_meme'}
        
        print(f"\n=== 已知Meme币 ({len(known_memes)}个) ===")
        for i, (meme_key, data) in enumerate(known_memes.items(), 1):
            print(f"{i:2d}. {data['name']} (${data['symbol']})")
            print(f"    类型: {data['category']} | 成立: {data['founded']}")
            print(f"    提及: {data['mention_count']}次 | 用户: {data['unique_users']}人 | 总分: {data['total_score']:.1f}")
            print(f"    社交: {data['social']['twitter']} | {data['social']['website']}")
            print(f"    描述: {data['description']}")
            print()
        
        print(f"\n=== 潜在新Meme币 ({len(potential_memes)}个) ===")
        for i, (meme_key, data) in enumerate(potential_memes.items(), 1):
            print(f"{i:2d}. ${data['symbol']}")
            print(f"    提及: {data['mention_count']}次 | 用户: {data['unique_users']}人")
            print(f"    Meme信号: {data['meme_signals']} | 社区信号: {data['community_signals']}")
            print(f"    潜力分数: {data['total_score']:.1f}")
            if data['sample_mentions']:
                print(f"    示例: {data['sample_mentions'][0]['text'][:100]}...")
            print()
    
    def save_enhanced_results(self, filename='enhanced_meme_detection_results.json'):
        """保存增强版结果"""
        print(f"保存结果到 {filename}...")
        
        save_data = {
            'detection_timestamp': datetime.now().isoformat(),
            'detected_memes': self.detected_memes,
            'summary': {
                'total_memes': len(self.detected_memes),
                'known_memes': len([m for m in self.detected_memes.values() if m['detection_type'] == 'known_meme']),
                'potential_memes': len([m for m in self.detected_memes.values() if m['detection_type'] == 'potential_meme']),
                'detection_method': '增强版检测 - 已知meme币 + 潜在发现',
                'features': ['项目信息', '社交媒体', '情感分析', '社区信号']
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到 {filename}")

def main():
    """主函数"""
    print("=== 增强版Meme检测系统 ===")
    print("更多币种 + 项目信息 + 美观图表")
    print()
    
    # 创建检测器
    detector = EnhancedMemeDetector()
    
    try:
        # 1. 加载数据
        from config.paths import TWEETS_FILE
        detector.load_data(str(TWEETS_FILE))
        
        # 2. 检测meme币
        detected_memes = detector.detect_enhanced_memes()
        
        # 3. 显示摘要
        detector.print_enhanced_summary()
        
        # 4. 保存结果
        detector.save_enhanced_results()
        
        print("\n=== 增强版Meme检测完成 ===")
        print("已生成更完整的meme币数据库")
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
