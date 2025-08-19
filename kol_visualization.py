#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOL网络可视化系统
实现KOL影响力地图、互动关系网络图和影响力传播路径图
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from collections import defaultdict
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class KOLVisualization:
    def __init__(self):
        """初始化KOL可视化系统"""
        self.kol_data = {}
        self.network_data = {}
        self.meme_data = {}
        self.figures = {}
        
    def load_data(self):
        """加载所有相关数据"""
        print("加载数据...")
        
        try:
            # 加载KOL数据
            with open('kol_analysis_results.json', 'r', encoding='utf-8') as f:
                self.kol_data = json.load(f)
            print("✓ 加载KOL分析结果")
            
            # 加载KOL增强档案
            with open('enhanced_kol_profiles.json', 'r', encoding='utf-8') as f:
                self.enhanced_profiles = json.load(f)
            print("✓ 加载KOL增强档案")
            
            # 加载显性meme数据
            with open('meme_detection_v2_results.json', 'r', encoding='utf-8') as f:
                self.meme_data['explicit'] = json.load(f)
            print("✓ 加载显性meme数据")
            
            # 加载隐性meme数据
            with open('implicit_meme_detection_v3_results.json', 'r', encoding='utf-8') as f:
                self.meme_data['implicit'] = json.load(f)
            print("✓ 加载隐性meme数据")
            
            # 加载关注关系数据
            self.followings_df = pd.read_csv('sample_followings.csv')
            print("✓ 加载关注关系数据")
            
        except FileNotFoundError as e:
            print(f"⚠️  部分数据文件缺失: {e}")
            print("将使用可用数据进行可视化")
        
        print("数据加载完成")
    
    def create_kol_influence_map(self):
        """创建KOL影响力地图"""
        print("创建KOL影响力地图...")
        
        if not self.kol_data or 'kol_report' not in self.kol_data:
            print("⚠️  KOL数据不可用，跳过影响力地图")
            return
        
        kol_users = self.kol_data['kol_report']['top_kols']
        
        # 提取影响力数据
        influence_data = []
        for user_info in kol_users:
            influence_data.append({
                'user_id': user_info.get('user_id', 'unknown'),
                'username': user_info.get('user_name', 'Unknown'),
                'influence_score': user_info.get('influence_score', 0),
                'follower_count': user_info.get('follower_count', 0),
                'engagement_rate': user_info.get('engagement_rate', 0),
                'kol_level': user_info.get('kol_level', 'Unknown')
            })
        
        if not influence_data:
            print("⚠️  没有KOL数据可可视化")
            return
        
        # 创建影响力分布图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('KOL影响力分析地图', fontsize=16, fontweight='bold')
        
        # 1. 影响力分数分布
        scores = [user['influence_score'] for user in influence_data]
        ax1.hist(scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('KOL影响力分数分布')
        ax1.set_xlabel('影响力分数')
        ax1.set_ylabel('KOL数量')
        ax1.grid(True, alpha=0.3)
        
        # 2. 粉丝数vs影响力分数散点图
        followers = [user['follower_count'] for user in influence_data]
        ax2.scatter(followers, scores, alpha=0.6, c=scores, cmap='viridis')
        ax2.set_title('粉丝数 vs 影响力分数')
        ax2.set_xlabel('粉丝数')
        ax2.set_ylabel('影响力分数')
        ax2.grid(True, alpha=0.3)
        
        # 3. KOL等级分布
        level_counts = defaultdict(int)
        for user in influence_data:
            level_counts[user['kol_level']] += 1
        
        levels = list(level_counts.keys())
        counts = list(level_counts.values())
        colors = ['gold', 'silver', 'bronze', 'lightblue']
        ax3.bar(levels, counts, color=colors[:len(levels)], alpha=0.8)
        ax3.set_title('KOL等级分布')
        ax3.set_xlabel('KOL等级')
        ax3.set_ylabel('数量')
        
        # 4. 互动率分布
        engagement_rates = [user['engagement_rate'] for user in influence_data if user['engagement_rate'] > 0]
        if engagement_rates:
            ax4.hist(engagement_rates, bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
            ax4.set_title('KOL互动率分布')
            ax4.set_xlabel('互动率')
            ax4.set_ylabel('KOL数量')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.figures['kol_influence_map'] = fig
        plt.savefig('kol_influence_map.png', dpi=300, bbox_inches='tight')
        print("✓ KOL影响力地图已保存")
    
    def create_interaction_network(self):
        """创建KOL互动关系网络图"""
        print("创建KOL互动关系网络图...")
        
        if not self.kol_data or 'kol_report' not in self.kol_data:
            print("⚠️  KOL数据不可用，跳过互动网络")
            return
        
        kol_users = self.kol_data['kol_report']['top_kols']
        
        # 创建网络图
        G = nx.Graph()
        
        # 添加KOL节点
        for user_info in kol_users:
            user_id = user_info.get('user_id', 'unknown')
            influence_score = user_info.get('influence_score', 0)
            kol_level = user_info.get('kol_level', 'Unknown')
            
            # 根据影响力分数设置节点大小
            node_size = max(100, influence_score * 2)
            
            # 根据KOL等级设置节点颜色
            color_map = {
                'Tier 1 (顶级KOL)': 'red',
                'Tier 2 (高级KOL)': 'orange', 
                'Tier 3 (中级KOL)': 'yellow',
                'Tier 4 (初级KOL)': 'lightblue'
            }
            node_color = color_map.get(kol_level, 'gray')
            
            G.add_node(user_id, 
                      size=node_size,
                      color=node_color,
                      influence_score=influence_score,
                      kol_level=kol_level,
                      username=user_info.get('user_name', 'Unknown'))
        
        # 添加关注关系边
        if hasattr(self, 'followings_df') and not self.followings_df.empty:
            for _, row in self.followings_df.iterrows():
                follower_id = str(row['user_id'])
                following_id = str(row['following_user_id'])
                
                if follower_id in kol_users and following_id in kol_users:
                    G.add_edge(follower_id, following_id)
        
        # 计算网络指标
        network_metrics = {
            '节点数': G.number_of_nodes(),
            '边数': G.number_of_edges(),
            '网络密度': nx.density(G),
            '平均聚类系数': nx.average_clustering(G) if G.number_of_nodes() > 1 else 0,
            '连通分量数': nx.number_connected_components(G)
        }
        
        print(f"网络指标: {network_metrics}")
        
        # 绘制网络图
        plt.figure(figsize=(16, 12))
        
        # 设置布局
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # 绘制节点
        node_sizes = [G.nodes[node]['size'] for node in G.nodes()]
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, 
                              node_size=node_sizes,
                              node_color=node_colors,
                              alpha=0.8)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray')
        
        # 添加标签（只显示重要节点）
        important_nodes = [node for node in G.nodes() 
                          if G.nodes[node]['influence_score'] > 50]
        
        labels = {node: G.nodes[node]['username'][:10] for node in important_nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        plt.title('KOL互动关系网络图', fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # 添加图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                      markersize=10, label='Tier 1 (顶级KOL)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
                      markersize=10, label='Tier 2 (高级KOL)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', 
                      markersize=10, label='Tier 3 (中级KOL)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                      markersize=10, label='Tier 4 (初级KOL)')
        ]
        plt.legend(handles=legend_elements, loc='upper left')
        
        self.figures['interaction_network'] = plt.gcf()
        plt.savefig('kol_interaction_network.png', dpi=300, bbox_inches='tight')
        print("✓ KOL互动关系网络图已保存")
    
    def create_meme_trend_dashboard(self):
        """创建Meme趋势仪表板"""
        print("创建Meme趋势仪表板...")
        
        # 创建综合仪表板
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Meme趋势分析仪表板', fontsize=16, fontweight='bold')
        
        # 1. 显性Meme热度分布
        if 'explicit' in self.meme_data and 'meme_scores' in self.meme_data['explicit']:
            explicit_memes = self.meme_data['explicit']['meme_scores']
            if explicit_memes:
                meme_names = list(explicit_memes.keys())[:10]  # 前10名
                meme_scores = [explicit_memes[name] for name in meme_names]
                
                ax1.barh(range(len(meme_names)), meme_scores, color='lightcoral', alpha=0.8)
                ax1.set_yticks(range(len(meme_names)))
                ax1.set_yticklabels(meme_names)
                ax1.set_title('显性Meme热度排名 (Top 10)')
                ax1.set_xlabel('热度分数')
                ax1.grid(True, alpha=0.3)
        
        # 2. 隐性Meme潜力分布
        if 'implicit' in self.meme_data and 'potential_memes' in self.meme_data['implicit']:
            implicit_memes = self.meme_data['implicit']['potential_memes']
            if implicit_memes:
                project_names = list(implicit_memes.keys())
                total_scores = [implicit_memes[name]['total_score'] for name in project_names]
                
                ax2.bar(range(len(project_names)), total_scores, color='lightgreen', alpha=0.8)
                ax2.set_title('隐性Meme潜力分数')
                ax2.set_xlabel('项目')
                ax2.set_ylabel('潜力分数')
                ax2.set_xticks(range(len(project_names)))
                ax2.set_xticklabels(project_names, rotation=45, ha='right')
                ax2.grid(True, alpha=0.3)
        
        # 3. Meme类型分布
        if 'explicit' in self.meme_data and 'meme_categories' in self.meme_data['explicit']:
            categories = self.meme_data['explicit']['meme_categories']
            if categories:
                # 统计每个分类的数量
                category_counts = defaultdict(int)
                for meme_name, meme_categories in categories.items():
                    if isinstance(meme_categories, list):
                        for cat in meme_categories:
                            category_counts[cat] += 1
                    else:
                        category_counts[meme_categories] += 1
                
                if category_counts:
                    cat_names = list(category_counts.keys())
                    cat_counts = list(category_counts.values())
                    
                    colors = plt.cm.Set3(np.linspace(0, 1, len(cat_names)))
                    ax3.pie(cat_counts, labels=cat_names, autopct='%1.1f%%', colors=colors)
                    ax3.set_title('Meme类型分布')
        
        # 4. 综合趋势分析
        # 这里可以添加时间序列分析或其他综合指标
        ax4.text(0.5, 0.5, 'Meme趋势综合分析\n(待开发)', 
                ha='center', va='center', transform=ax4.transAxes,
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax4.set_title('综合趋势分析')
        ax4.axis('off')
        
        plt.tight_layout()
        self.figures['meme_trend_dashboard'] = fig
        plt.savefig('meme_trend_dashboard.png', dpi=300, bbox_inches='tight')
        print("✓ Meme趋势仪表板已保存")
    
    def create_influence_propagation_path(self):
        """创建影响力传播路径图"""
        print("创建影响力传播路径图...")
        
        if not self.kol_data or 'kol_report' not in self.kol_data:
            print("⚠️  KOL数据不可用，跳过传播路径图")
            return
        
        kol_users = self.kol_data['kol_report']['top_kols']
        
        # 创建有向图（影响力传播方向）
        DG = nx.DiGraph()
        
        # 添加KOL节点
        for user_info in kol_users:
            user_id = user_info.get('user_id', 'unknown')
            influence_score = user_info.get('influence_score', 0)
            DG.add_node(user_id, 
                       influence_score=influence_score,
                       username=user_info.get('user_name', 'Unknown'))
        
        # 添加影响力传播边（基于关注关系）
        if hasattr(self, 'followings_df') and not self.followings_df.empty:
            for _, row in self.followings_df.iterrows():
                follower_id = str(row['user_id'])
                following_id = str(row['following_user_id'])
                
                # 查找用户的影响力分数
                follower_score = 0
                following_score = 0
                
                for user_info in kol_users:
                    if user_info.get('user_id') == follower_id:
                        follower_score = user_info.get('influence_score', 0)
                    if user_info.get('user_id') == following_id:
                        following_score = user_info.get('influence_score', 0)
                
                # 如果两个用户都是KOL，添加边
                if follower_score > 0 and following_score > 0:
                    # 计算影响力传播强度
                    propagation_strength = min(follower_score / following_score, 1.0)
                    DG.add_edge(following_id, follower_id, 
                              weight=propagation_strength)
        
        # 计算影响力传播指标
        propagation_metrics = {
            '节点数': DG.number_of_nodes(),
            '边数': DG.number_of_edges(),
            '平均入度': sum(dict(DG.in_degree()).values()) / DG.number_of_nodes() if DG.number_of_nodes() > 0 else 0,
            '平均出度': sum(dict(DG.out_degree()).values()) / DG.number_of_nodes() if DG.number_of_nodes() > 0 else 0
        }
        
        print(f"影响力传播指标: {propagation_metrics}")
        
        # 绘制影响力传播路径图
        plt.figure(figsize=(16, 12))
        
        # 设置布局
        pos = nx.spring_layout(DG, k=2, iterations=100)
        
        # 绘制节点（大小基于影响力分数）
        node_sizes = [max(100, DG.nodes[node]['influence_score'] * 3) for node in DG.nodes()]
        node_colors = [DG.nodes[node]['influence_score'] for node in DG.nodes()]
        
        nodes = nx.draw_networkx_nodes(DG, pos, 
                                     node_size=node_sizes,
                                     node_color=node_colors,
                                     cmap='viridis',
                                     alpha=0.8)
        
        # 绘制边（粗细基于传播强度）
        edge_weights = [DG[u][v]['weight'] for u, v in DG.edges()]
        edge_widths = [w * 3 for w in edge_weights]
        
        nx.draw_networkx_edges(DG, pos, 
                              width=edge_widths,
                              alpha=0.4,
                              edge_color='gray',
                              arrows=True,
                              arrowsize=15)
        
        # 添加标签（只显示重要节点）
        important_nodes = [node for node in DG.nodes() 
                          if DG.nodes[node]['influence_score'] > 50]
        
        labels = {node: DG.nodes[node]['username'][:8] for node in important_nodes}
        nx.draw_networkx_labels(DG, pos, labels, font_size=8, font_weight='bold')
        
        plt.title('KOL影响力传播路径图', fontsize=16, fontweight='bold')
        plt.colorbar(nodes, label='影响力分数')
        plt.axis('off')
        
        self.figures['influence_propagation'] = plt.gcf()
        plt.savefig('kol_influence_propagation.png', dpi=300, bbox_inches='tight')
        print("✓ KOL影响力传播路径图已保存")
    
    def generate_comprehensive_report(self):
        """生成综合可视化报告"""
        print("生成综合可视化报告...")
        
        # 创建综合报告页面
        fig = plt.figure(figsize=(20, 16))
        
        # 创建网格布局
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 标题
        fig.suptitle('KOL推特动态Meme信息捕捉项目 - 综合可视化报告', 
                     fontsize=20, fontweight='bold', y=0.98)
        
        # 1. KOL影响力分布 (左上)
        ax1 = fig.add_subplot(gs[0, :2])
        if self.kol_data and 'kol_report' in self.kol_data:
            kol_users = self.kol_data['kol_report']['top_kols']
            scores = [user['influence_score'] for user in kol_users]
            ax1.hist(scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_title('KOL影响力分数分布', fontweight='bold')
            ax1.set_xlabel('影响力分数')
            ax1.set_ylabel('KOL数量')
            ax1.grid(True, alpha=0.3)
        
        # 2. Meme热度对比 (右上)
        ax2 = fig.add_subplot(gs[0, 2:])
        if 'explicit' in self.meme_data and 'implicit' in self.meme_data:
            explicit_count = len(self.meme_data['explicit'].get('meme_scores', {}))
            implicit_count = len(self.meme_data['implicit'].get('potential_memes', {}))
            
            categories = ['显性Meme', '隐性Meme']
            counts = [explicit_count, implicit_count]
            colors = ['lightcoral', 'lightgreen']
            
            bars = ax2.bar(categories, counts, color=colors, alpha=0.8)
            ax2.set_title('Meme类型数量对比', fontweight='bold')
            ax2.set_ylabel('数量')
            
            # 添加数值标签
            for bar, count in zip(bars, counts):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         str(count), ha='center', va='bottom')
        
        # 3. 网络密度分析 (中左)
        ax3 = fig.add_subplot(gs[1, :2])
        if hasattr(self, 'followings_df') and not self.followings_df.empty:
            # 计算网络密度
            total_users = len(set(self.followings_df['user_id'].unique()) | 
                             set(self.followings_df['following_user_id'].unique()))
            total_connections = len(self.followings_df)
            max_connections = total_users * (total_users - 1)
            density = total_connections / max_connections if max_connections > 0 else 0
            
            metrics = ['用户总数', '连接数', '网络密度']
            values = [total_users, total_connections, f'{density:.4f}']
            colors = ['lightblue', 'lightgreen', 'lightcoral']
            
            bars = ax3.bar(metrics, [float(v) if isinstance(v, (int, float)) else 0.1 for v in values], 
                           color=colors, alpha=0.8)
            ax3.set_title('网络结构分析', fontweight='bold')
            ax3.set_ylabel('数值')
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                         str(value), ha='center', va='bottom')
        
        # 4. 时间趋势分析 (中右)
        ax4 = fig.add_subplot(gs[1, 2:])
        ax4.text(0.5, 0.5, '时间趋势分析\n(待开发)', 
                ha='center', va='center', transform=ax4.transAxes,
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax4.set_title('时间趋势分析', fontweight='bold')
        ax4.axis('off')
        
        # 5. 项目统计信息 (下左)
        ax5 = fig.add_subplot(gs[2:, :2])
        if 'implicit' in self.meme_data and 'potential_memes' in self.meme_data['implicit']:
            implicit_memes = self.meme_data['implicit']['potential_memes']
            if implicit_memes:
                project_names = list(implicit_memes.keys())[:8]  # 显示前8个
                total_scores = [implicit_memes[name]['total_score'] for name in project_names]
                
                bars = ax5.barh(range(len(project_names)), total_scores, color='lightgreen', alpha=0.8)
                ax5.set_yticks(range(len(project_names)))
                ax5.set_yticklabels(project_names)
                ax5.set_title('Top隐性Meme币潜力分数', fontweight='bold')
                ax5.set_xlabel('潜力分数')
                ax5.grid(True, alpha=0.3)
        
        # 6. 系统状态信息 (下右)
        ax6 = fig.add_subplot(gs[2:, 2:])
        
        # 创建状态信息表格
        status_data = [
            ['数据加载', '✓ 完成'],
            ['KOL识别', '✓ 完成'],
            ['显性Meme检测', '✓ 完成'],
            ['隐性Meme检测', '✓ 完成'],
            ['可视化系统', '✓ 运行中'],
            ['下一步', 'KOL行为分析']
        ]
        
        table = ax6.table(cellText=status_data,
                          colLabels=['项目状态', '状态'],
                          cellLoc='center',
                          loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        ax6.set_title('项目状态看板', fontweight='bold')
        ax6.axis('off')
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.02, 0.02, f'报告生成时间: {timestamp}', 
                fontsize=10, style='italic')
        
        plt.tight_layout()
        self.figures['comprehensive_report'] = fig
        plt.savefig('kol_comprehensive_report.png', dpi=300, bbox_inches='tight')
        print("✓ 综合可视化报告已保存")
    
    def run_all_visualizations(self):
        """运行所有可视化"""
        print("=== 开始运行KOL网络可视化系统 ===")
        
        # 1. 加载数据
        self.load_data()
        
        # 2. 创建各种可视化
        try:
            self.create_kol_influence_map()
            self.create_interaction_network()
            self.create_meme_trend_dashboard()
            self.create_influence_propagation_path()
            self.generate_comprehensive_report()
            
            print("\n=== 所有可视化完成 ===")
            print("生成的文件:")
            print("- kol_influence_map.png (KOL影响力地图)")
            print("- kol_interaction_network.png (互动关系网络图)")
            print("- meme_trend_dashboard.png (Meme趋势仪表板)")
            print("- kol_influence_propagation.png (影响力传播路径图)")
            print("- kol_comprehensive_report.png (综合可视化报告)")
            
        except Exception as e:
            print(f"可视化过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("=== KOL网络可视化系统 ===")
    
    # 创建可视化器
    visualizer = KOLVisualization()
    
    # 运行所有可视化
    visualizer.run_all_visualizations()
    
    print("\n=== 可视化系统运行完成 ===")

if __name__ == "__main__":
    main()
