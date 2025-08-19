# 推特热门项目筛选系统

一个基于推特数据分析的热门项目识别和评分系统，帮助用户快速掌握市场趋势和热点话题。

## 项目介绍

该系统通过分析推特数据集，自动识别并筛选出热门项目，计算其热度得分，并生成排行榜和可视化图表。系统基于多维度评分机制，考虑项目的提及频率、互动量、用户影响力和增长趋势等因素，提供全面的热度评估。

### 主要功能

- **数据处理**：高效处理大型CSV格式的推特数据
- **项目识别**：从推文文本中提取潜在项目名称和标签
- **热度评估**：基于多维度指标计算项目热度得分
- **结果可视化**：生成热门项目排行榜和用户参与度图表
- **数据导出**：以JSON格式导出分析结果

## 安装说明

### 前提条件

- Python 3.6+
- 推荐使用虚拟环境

### 依赖安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/twitter-hot-projects.git
cd twitter-hot-projects

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 依赖列表

以下是主要依赖包：

- pandas>=1.0.0
- numpy>=1.18.0
- matplotlib>=3.1.0
- tqdm>=4.45.0

## 使用方法

### 数据准备

将Twitter数据文件放在项目根目录下：

- `sample_tweets.csv`：推文数据
- `sample_followings.csv`：关注关系数据

### 运行分析

```bash
python twitter_hot_projects.py
```

### 查看结果

分析完成后，结果将保存在：

- `hot_projects.json`：热门项目数据（JSON格式）
- `charts/hot_projects_score.png`：热门项目排行榜图表
- `charts/user_engagement.png`：用户参与度图表
- `twitter_analysis.log`：详细的分析日志

## 配置说明

系统配置位于主程序文件的`CONFIG`字典中，您可以根据需要调整以下参数：

### 输入/输出配置

- `tweets_file`：推文数据文件路径
- `followings_file`：关注关系数据文件路径
- `results_file`：结果输出JSON文件路径
- `charts_dir`：图表保存目录

### 筛选参数

- `min_mentions`：最低提及次数（默认5次）
- `min_engagement`：最低互动量（默认10）
- `min_score`：最低最终分值（默认20分）

### 评分权重

- `mention_weight`：提及次数权重（默认0.3）
- `engagement_weight`：互动量权重（默认0.4）
- `influence_weight`：用户影响力权重（默认0.3）
- `trend_weight`：增长趋势权重（默认0.2）
- `trend_dampening`：下降趋势减缓系数（默认0.1）

## 开发者指南

### 项目结构

```
twitter-hot-projects/
├── twitter_hot_projects.py  # 主程序
├── sample_tweets.csv        # 推文数据样本
├── sample_followings.csv    # 关注关系数据样本
├── hot_projects.json        # 分析结果输出
├── README.md                # 项目说明
├── requirements.txt         # 依赖列表
└── charts/                  # 图表输出目录
    ├── hot_projects_score.png
    └── user_engagement.png
```

### 扩展开发

如需扩展系统功能，可以关注以下几个方面：

1. 在`ProjectIdentifier`类中增加更复杂的项目识别方法
2. 在`ScoreCalculator`类中调整或增加评分指标
3. 在`AnalysisManager`类中添加新的可视化和报告功能

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。

## 联系方式

如有问题或建议，请提交Issue或发送邮件至：your.email@example.com 