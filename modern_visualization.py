#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化Meme币可视化系统
美观的图表设计 + 完整项目信息展示
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置现代化样式
plt.style.use('default')
sns.set_palette("husl")

# 设置中文字体和现代化样式
plt.rcParams.update({
    'font.sans-serif': ['Arial Unicode MS', 'SimHei', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'figure.facecolor': '#f8f9fa',
    'axes.facecolor': '#ffffff',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': True,
    'axes.spines.bottom': True,
    'axes.linewidth': 1.2,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.8,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10
})

class ModernMemeVisualization:
    def __init__(self):
        """初始化现代化可视化系统"""
        self.meme_data = {}
        self.color_palette = {
            'ai_meme': '#FF6B6B',
            'animal_meme': '#4ECDC4', 
            'internet_culture': '#45B7D1',
            'community_meme': '#96CEB4',
            'potential_meme': '#FECA57'
        }
        
    def load_data(self):
        """加载增强版meme数据"""
        print("加载增强版meme数据...")
        
        try:
            with open('enhanced_meme_detection_results.json', 'r', encoding='utf-8') as f:
                self.meme_data = json.load(f)
            print(f"✓ 加载了 {len(self.meme_data['detected_memes'])} 个meme币数据")
        except FileNotFoundError:
            print("⚠️  增强版数据文件不存在，请先运行 enhanced_meme_detector.py")
            return False
        
        return True
    
    def create_meme_overview_dashboard(self):
        """创建Meme币概览仪表板"""
        print("创建Meme币概览仪表板...")
        
        if not self.meme_data:
            print("⚠️  数据不可用")
            return
        
        memes = self.meme_data['detected_memes']
        
        # 创建大型仪表板
        fig = plt.figure(figsize=(20, 16))
        fig.patch.set_facecolor('#f8f9fa')
        
        # 创建网格布局
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 主标题
        fig.suptitle('🚀 Meme币市场全景分析仪表板', 
                     fontsize=24, fontweight='bold', y=0.97, color='#2c3e50')
        
        # 1. Top Meme币排行榜 (左上大区域)
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        self._create_top_memes_ranking(ax1, memes)
        
        # 2. 类型分布饼图 (右上)
        ax2 = fig.add_subplot(gs[0, 2])
        self._create_category_pie_chart(ax2, memes)
        
        # 3. 活跃度热力图 (右上)
        ax3 = fig.add_subplot(gs[0, 3])
        self._create_activity_heatmap(ax3, memes)
        
        # 4. 用户参与度分析 (右中)
        ax4 = fig.add_subplot(gs[1, 2:])
        self._create_engagement_analysis(ax4, memes)
        
        # 5. 潜在meme币雷达图 (左下)
        ax5 = fig.add_subplot(gs[2, 0:2])
        self._create_potential_memes_chart(ax5, memes)
        
        # 6. 社交媒体影响力 (右下)
        ax6 = fig.add_subplot(gs[2:, 2:])
        self._create_social_influence_matrix(ax6, memes)
        
        # 7. 项目信息表格 (底部)
        ax7 = fig.add_subplot(gs[3, 0:2])
        self._create_project_info_table(ax7, memes)
        
        # 添加时间戳和统计信息
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.02, 0.02, f'📊 数据更新时间: {timestamp}', 
                fontsize=10, style='italic', color='#7f8c8d')
        
        fig.text(0.98, 0.02, f'📈 共检测到 {len(memes)} 个meme币项目', 
                fontsize=10, style='italic', color='#7f8c8d', ha='right')
        
        plt.tight_layout()
        plt.savefig('modern_meme_dashboard.png', dpi=300, bbox_inches='tight', 
                   facecolor='#f8f9fa', edgecolor='none')
        print("✓ 现代化Meme币仪表板已保存")
        
    def _create_top_memes_ranking(self, ax, memes):
        """创建Top Meme币排行榜"""
        # 按总分排序，取前12名
        sorted_memes = sorted(memes.items(), key=lambda x: x[1]['total_score'], reverse=True)[:12]
        
        names = []
        scores = []
        colors = []
        
        for meme_key, data in sorted_memes:
            name = f"${data['symbol']}"
            names.append(name)
            scores.append(data['total_score'])
            colors.append(self.color_palette.get(data['category'], '#95a5a6'))
        
        # 创建水平条形图
        bars = ax.barh(range(len(names)), scores, color=colors, alpha=0.8, height=0.7)
        
        # 美化图表
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=11, fontweight='bold')
        ax.set_xlabel('热度分数', fontsize=12, fontweight='bold')
        ax.set_title('🏆 Top 12 热门Meme币排行榜', fontsize=16, fontweight='bold', pad=20)
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(bar.get_width() + max(scores)*0.01, bar.get_y() + bar.get_height()/2,
                   f'{score:.1f}', va='center', ha='left', fontweight='bold', fontsize=10)
        
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_xlim(0, max(scores) * 1.15)
        
    def _create_category_pie_chart(self, ax, memes):
        """创建类型分布饼图"""
        category_counts = {}
        for data in memes.values():
            category = data['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # 中文标签映射
        category_labels = {
            'ai_meme': 'AI主题',
            'animal_meme': '动物主题',
            'internet_culture': '网络文化',
            'community_meme': '社区驱动',
            'potential_meme': '潜在项目'
        }
        
        labels = [category_labels.get(cat, cat) for cat in category_counts.keys()]
        sizes = list(category_counts.values())
        colors = [self.color_palette.get(cat, '#95a5a6') for cat in category_counts.keys()]
        
        # 创建饼图
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 9})
        
        ax.set_title('📊 Meme币类型分布', fontsize=14, fontweight='bold', pad=20)
        
    def _create_activity_heatmap(self, ax, memes):
        """创建活跃度热力图"""
        # 创建活跃度矩阵数据
        activity_data = []
        labels = []
        
        sorted_memes = sorted(memes.items(), key=lambda x: x[1]['total_score'], reverse=True)[:8]
        
        for meme_key, data in sorted_memes:
            activity_row = [
                data.get('mention_count', 0) / 100,  # 标准化
                data.get('unique_users', 0) / 10,
                data.get('total_score', 0) / 100
            ]
            activity_data.append(activity_row)
            labels.append(f"${data['symbol']}")
        
        # 创建热力图
        im = ax.imshow(activity_data, cmap='YlOrRd', aspect='auto', alpha=0.8)
        
        # 设置标签
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(['提及次数', '用户数', '总分'], rotation=45, fontsize=9)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title('🔥 活跃度热力图', fontsize=12, fontweight='bold', pad=15)
        
        # 添加数值标签
        for i in range(len(activity_data)):
            for j in range(len(activity_data[0])):
                text = ax.text(j, i, f'{activity_data[i][j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
    
    def _create_engagement_analysis(self, ax, memes):
        """创建用户参与度分析"""
        mention_counts = []
        user_counts = []
        labels = []
        colors = []
        
        for meme_key, data in memes.items():
            if data.get('mention_count', 0) > 0:  # 只显示有数据的
                mention_counts.append(data.get('mention_count', 0))
                user_counts.append(data.get('unique_users', 0))
                labels.append(f"${data['symbol']}")
                colors.append(self.color_palette.get(data['category'], '#95a5a6'))
        
        # 创建散点图
        scatter = ax.scatter(mention_counts, user_counts, c=colors, s=100, alpha=0.7, edgecolors='white', linewidth=2)
        
        # 添加标签（只显示重要的点）
        for i, (x, y, label) in enumerate(zip(mention_counts, user_counts, labels)):
            if x > 50 or y > 10:  # 只标注重要的点
                ax.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points',
                           fontsize=9, fontweight='bold', alpha=0.8)
        
        ax.set_xlabel('提及次数', fontsize=12, fontweight='bold')
        ax.set_ylabel('独立用户数', fontsize=12, fontweight='bold')
        ax.set_title('👥 用户参与度分析', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
    def _create_potential_memes_chart(self, ax, memes):
        """创建潜在meme币图表"""
        potential_memes = {k: v for k, v in memes.items() if v.get('detection_type') == 'potential_meme'}
        
        if not potential_memes:
            ax.text(0.5, 0.5, '暂无潜在meme币数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14, color='#7f8c8d')
            ax.set_title('🔍 潜在Meme币发现', fontsize=14, fontweight='bold')
            return
        
        # 按分数排序
        sorted_potential = sorted(potential_memes.items(), key=lambda x: x[1]['total_score'], reverse=True)
        
        names = [f"${data['symbol']}" for _, data in sorted_potential[:8]]
        scores = [data['total_score'] for _, data in sorted_potential[:8]]
        
        # 创建条形图
        bars = ax.bar(range(len(names)), scores, color=self.color_palette['potential_meme'], 
                     alpha=0.8, edgecolor='white', linewidth=2)
        
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10, fontweight='bold')
        ax.set_ylabel('潜力分数', fontsize=12, fontweight='bold')
        ax.set_title('🔍 潜在Meme币发现', fontsize=14, fontweight='bold', pad=20)
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(scores)*0.01,
                   f'{score:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        ax.grid(True, alpha=0.3, axis='y')
        
    def _create_social_influence_matrix(self, ax, memes):
        """创建社交媒体影响力矩阵"""
        # 选择有完整社交信息的已知meme币
        known_memes = {k: v for k, v in memes.items() if v.get('detection_type') == 'known_meme'}
        
        if len(known_memes) < 3:
            ax.text(0.5, 0.5, '社交媒体数据收集中...', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14, color='#7f8c8d')
            ax.set_title('📱 社交媒体影响力', fontsize=14, fontweight='bold')
            return
        
        # 创建项目信息表格
        table_data = []
        sorted_known = sorted(known_memes.items(), key=lambda x: x[1]['total_score'], reverse=True)[:8]
        
        for meme_key, data in sorted_known:
            row = [
                f"${data['symbol']}",
                data['name'][:20] + "..." if len(data['name']) > 20 else data['name'],
                data['category'].replace('_', ' ').title(),
                f"{data.get('mention_count', 0)}",
                f"{data.get('unique_users', 0)}",
                data['social']['twitter'] if data['social']['twitter'] != 'Unknown' else 'N/A'
            ]
            table_data.append(row)
        
        # 创建表格
        table = ax.table(cellText=table_data,
                        colLabels=['代币', '项目名', '类型', '提及', '用户', 'Twitter'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.12, 0.25, 0.15, 0.08, 0.08, 0.15])
        
        # 美化表格
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # 设置表格样式
        for i in range(len(table_data) + 1):
            for j in range(6):
                cell = table[(i, j)]
                if i == 0:  # 标题行
                    cell.set_facecolor('#34495e')
                    cell.set_text_props(weight='bold', color='white')
                else:  # 数据行
                    if i % 2 == 0:
                        cell.set_facecolor('#ecf0f1')
                    else:
                        cell.set_facecolor('#ffffff')
                    cell.set_text_props(color='#2c3e50')
        
        ax.set_title('📋 项目详细信息', fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        
    def _create_project_info_table(self, ax, memes):
        """创建项目信息汇总"""
        # 统计信息
        total_memes = len(memes)
        known_memes = len([m for m in memes.values() if m.get('detection_type') == 'known_meme'])
        potential_memes = len([m for m in memes.values() if m.get('detection_type') == 'potential_meme'])
        total_mentions = sum(m.get('mention_count', 0) for m in memes.values())
        total_users = sum(m.get('unique_users', 0) for m in memes.values())
        
        # 创建统计信息表格
        stats_data = [
            ['📊 总meme币数量', f'{total_memes}个'],
            ['✅ 已知项目', f'{known_memes}个'],
            ['🔍 潜在发现', f'{potential_memes}个'],
            ['💬 总提及次数', f'{total_mentions:,}次'],
            ['👥 参与用户数', f'{total_users:,}人'],
            ['📈 平均热度', f'{total_mentions/total_memes:.1f}次/项目']
        ]
        
        table = ax.table(cellText=stats_data,
                        colLabels=['指标', '数值'],
                        cellLoc='left',
                        loc='center',
                        colWidths=[0.6, 0.4])
        
        # 美化表格
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.5)
        
        # 设置样式
        for i in range(len(stats_data) + 1):
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # 标题行
                    cell.set_facecolor('#3498db')
                    cell.set_text_props(weight='bold', color='white')
                else:  # 数据行
                    cell.set_facecolor('#ecf0f1')
                    cell.set_text_props(color='#2c3e50', weight='bold' if j == 1 else 'normal')
        
        ax.set_title('📈 市场统计概览', fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
    
    def create_individual_meme_cards(self):
        """创建个别meme币详情卡片"""
        print("创建个别meme币详情卡片...")
        
        if not self.meme_data:
            print("⚠️  数据不可用")
            return
        
        memes = self.meme_data['detected_memes']
        
        # 选择前6个最热门的meme币
        sorted_memes = sorted(memes.items(), key=lambda x: x[1]['total_score'], reverse=True)[:6]
        
        # 创建2x3网格
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.patch.set_facecolor('#f8f9fa')
        fig.suptitle('🎯 热门Meme币详情卡片', fontsize=20, fontweight='bold', y=0.95)
        
        for idx, (meme_key, data) in enumerate(sorted_memes):
            row, col = idx // 3, idx % 3
            ax = axes[row, col]
            
            self._create_meme_card(ax, meme_key, data)
        
        plt.tight_layout()
        plt.savefig('meme_detail_cards.png', dpi=300, bbox_inches='tight',
                   facecolor='#f8f9fa', edgecolor='none')
        print("✓ Meme币详情卡片已保存")
    
    def _create_meme_card(self, ax, meme_key, data):
        """创建单个meme币卡片"""
        # 设置背景色
        ax.set_facecolor('#ffffff')
        
        # 获取颜色
        color = self.color_palette.get(data['category'], '#95a5a6')
        
        # 创建标题区域
        ax.text(0.5, 0.9, f"${data['symbol']}", ha='center', va='center',
               transform=ax.transAxes, fontsize=18, fontweight='bold', color=color)
        
        ax.text(0.5, 0.82, data['name'], ha='center', va='center',
               transform=ax.transAxes, fontsize=12, color='#2c3e50')
        
        # 添加类型标签
        category_name = data['category'].replace('_', ' ').title()
        ax.text(0.5, 0.75, f"🏷️ {category_name}", ha='center', va='center',
               transform=ax.transAxes, fontsize=10, color='#7f8c8d')
        
        # 添加关键指标
        metrics = [
            f"📊 热度分数: {data.get('total_score', 0):.1f}",
            f"💬 提及次数: {data.get('mention_count', 0)}",
            f"👥 用户参与: {data.get('unique_users', 0)}人",
            f"📅 成立时间: {data.get('founded', 'Unknown')}"
        ]
        
        for i, metric in enumerate(metrics):
            ax.text(0.05, 0.65 - i*0.08, metric, ha='left', va='center',
                   transform=ax.transAxes, fontsize=10, color='#2c3e50')
        
        # 添加描述
        description = data.get('description', 'No description available')
        if len(description) > 60:
            description = description[:60] + "..."
        
        ax.text(0.05, 0.25, f"📝 {description}", ha='left', va='top',
               transform=ax.transAxes, fontsize=9, color='#7f8c8d', wrap=True)
        
        # 添加社交媒体信息
        if data.get('social', {}).get('twitter', 'Unknown') != 'Unknown':
            ax.text(0.05, 0.1, f"🐦 {data['social']['twitter']}", ha='left', va='center',
                   transform=ax.transAxes, fontsize=9, color='#1da1f2')
        
        # 移除坐标轴
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # 添加边框
        for spine in ax.spines.values():
            spine.set_edgecolor(color)
            spine.set_linewidth(2)
    
    def run_all_visualizations(self):
        """运行所有现代化可视化"""
        print("=== 开始运行现代化可视化系统 ===")
        
        if not self.load_data():
            return
        
        try:
            # 创建主仪表板
            self.create_meme_overview_dashboard()
            
            # 创建详情卡片
            self.create_individual_meme_cards()
            
            print("\n=== 现代化可视化完成 ===")
            print("生成的文件:")
            print("- modern_meme_dashboard.png (现代化综合仪表板)")
            print("- meme_detail_cards.png (Meme币详情卡片)")
            print("\n🎨 图表采用现代化设计，信息更加完整！")
            
        except Exception as e:
            print(f"可视化过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("=== 现代化Meme币可视化系统 ===")
    print("美观设计 + 完整信息 + 专业图表")
    
    # 创建可视化器
    visualizer = ModernMemeVisualization()
    
    # 运行所有可视化
    visualizer.run_all_visualizations()

if __name__ == "__main__":
    main()
