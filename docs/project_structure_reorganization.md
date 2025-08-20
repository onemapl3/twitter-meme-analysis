# 📁 项目目录结构重组方案

## 🎯 重组目标

### 当前问题
- 项目根目录文件过多，缺乏组织
- 分析结果文件、配置文件、脚本文件混在一起
- 文件命名不够规范，难以理解项目结构

### 重组目标
- 创建清晰的目录层次结构
- 按功能模块分类组织文件
- 提高项目的可维护性和可读性
- 为新用户提供清晰的项目导航

## 🏗️ 新的目录结构

```
twitter-meme-analyzer/
├── 📁 src/                          # 源代码目录
│   ├── 📁 core/                     # 核心分析模块
│   │   ├── kol_analysis.py          # KOL分析引擎
│   │   ├── enhanced_meme_detector.py # 增强meme检测器
│   │   ├── implicit_meme_detector.py # 隐性meme检测器
│   │   └── kol_profile_enhancer.py  # KOL档案增强器
│   ├── 📁 web/                      # Web界面模块
│   │   ├── meme_api_server.py       # Flask API服务器
│   │   ├── templates/                # HTML模板
│   │   └── modern_visualization.py  # 可视化组件
│   ├── 📁 data_collection/          # 数据采集模块
│   │   ├── twitter_data_collector.py # Twitter数据采集器
│   │   ├── twitter_scheduler.py     # 定时任务调度器
│   │   └── data_pipeline_integration.py # 数据管道集成
│   ├── 📁 visualization/            # 可视化模块
│   │   ├── kol_visualization.py     # KOL可视化
│   │   └── modern_visualization.py  # 现代化可视化
│   └── 📁 utils/                    # 工具模块
│       ├── setup_database.py        # 数据库设置
│       └── test_*.py                # 测试脚本
├── 📁 config/                       # 配置文件目录
│   ├── collector_config.json        # 采集配置
│   ├── env_example.txt              # 环境变量示例
│   └── requirements_twitter.txt     # 依赖列表
├── 📁 data/                         # 数据目录
│   ├── 📁 raw/                      # 原始数据
│   │   ├── sample_tweets.csv        # 推文数据
│   │   └── sample_followings.csv    # 关注关系数据
│   ├── 📁 processed/                # 处理后的数据
│   │   ├── enhanced_kol_profiles.json
│   │   ├── enhanced_meme_detection_results.json
│   │   └── kol_analysis_results.json
│   └── 📁 intermediate/             # 中间数据
│       ├── basic_meme_detection_results.json
│       └── implicit_meme_detection_*.json
├── 📁 output/                       # 输出结果目录
│   ├── 📁 charts/                   # 图表输出
│   │   ├── hot_projects_score.png
│   │   ├── user_engagement.png
│   │   └── kol_*.png               # KOL相关图表
│   ├── 📁 reports/                  # 分析报告
│   └── 📁 logs/                     # 日志文件
├── 📁 docs/                         # 文档目录
│   ├── README.md                    # 项目说明
│   ├── README_API.md                # API接口说明
│   ├── README_Twitter_Collector.md  # 数据采集说明
│   ├── PRD.md                       # 产品需求文档
│   └── project_structure_reorganization.md # 本文档
├── 📁 scripts/                      # 脚本目录
│   ├── quick_start.py               # 快速启动脚本
│   └── setup_*.py                   # 设置脚本
├── 📁 tests/                        # 测试目录
│   ├── test_database_connection.py  # 数据库连接测试
│   ├── test_twitter_api.py          # Twitter API测试
│   └── test_*.py                    # 其他测试
├── .cursor/                          # Cursor配置
│   └── scratchpad.md                # 项目进度跟踪
├── .gitignore                        # Git忽略文件
└── README.md                         # 项目根目录说明
```

## 🔄 重组实施步骤

### 阶段1: 创建新目录结构
```bash
# 创建主要目录
mkdir -p src/{core,web,data_collection,visualization,utils}
mkdir -p config
mkdir -p data/{raw,processed,intermediate}
mkdir -p output/{charts,reports,logs}
mkdir -p docs
mkdir -p scripts
mkdir -p tests
```

### 阶段2: 移动源代码文件
```bash
# 移动核心分析模块
mv kol_analysis.py src/core/
mv enhanced_meme_detector.py src/core/
mv implicit_meme_detector*.py src/core/
mv kol_profile_enhancer.py src/core/

# 移动Web界面模块
mv meme_api_server.py src/web/
mv templates/ src/web/
mv modern_visualization.py src/web/

# 移动数据采集模块
mv twitter_data_collector.py src/data_collection/
mv twitter_scheduler.py src/data_collection/
mv data_pipeline_integration.py src/data_collection/

# 移动可视化模块
mv kol_visualization.py src/visualization/

# 移动工具模块
mv setup_database.py src/utils/
mv test_*.py src/utils/
```

### 阶段3: 移动配置文件
```bash
# 移动配置文件
mv collector_config.json config/
mv env_example.txt config/
mv requirements_twitter.txt config/
```

### 阶段4: 移动数据文件
```bash
# 移动原始数据
mv sample_*.csv data/raw/

# 移动处理后的数据
mv enhanced_*.json data/processed/
mv kol_analysis_results.json data/processed/

# 移动中间数据
mv basic_meme_detection_results.json data/intermediate/
mv implicit_meme_detection_*.json data/intermediate/
```

### 阶段5: 移动输出文件
```bash
# 移动图表输出
mv charts/* output/charts/

# 移动日志文件
mv *.log output/logs/ 2>/dev/null || true
```

### 阶段6: 移动文档文件
```bash
# 移动文档
mv README_*.md docs/
mv PRD.md docs/
```

### 阶段7: 移动脚本文件
```bash
# 移动脚本
mv quick_start.py scripts/
mv setup_*.py scripts/ 2>/dev/null || true
```

## 🔧 代码路径更新

### 需要更新的导入路径
由于文件位置发生变化，需要更新以下文件中的导入路径：

1. **相对导入更新**
   ```python
   # 原来的导入
   from kol_analysis import KOLAnalyzer
   
   # 更新后的导入
   from src.core.kol_analysis import KOLAnalyzer
   ```

2. **文件路径更新**
   ```python
   # 原来的路径
   with open('enhanced_kol_profiles.json', 'r') as f:
   
   # 更新后的路径
   with open('data/processed/enhanced_kol_profiles.json', 'r') as f:
   ```

### 创建路径配置文件
创建 `config/paths.py` 文件统一管理路径：

```python
# config/paths.py
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
INTERMEDIATE_DATA_DIR = DATA_DIR / "intermediate"

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORTS_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = OUTPUT_DIR / "logs"

# 配置文件目录
CONFIG_DIR = PROJECT_ROOT / "config"

# 确保目录存在
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, INTERMEDIATE_DATA_DIR, 
                 CHARTS_DIR, REPORTS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
```

## 📋 重组检查清单

### 重组前检查
- [ ] 备份所有重要文件
- [ ] 确认Git状态，提交或暂存当前更改
- [ ] 测试所有功能模块正常工作

### 重组中检查
- [ ] 创建新目录结构
- [ ] 移动文件到对应目录
- [ ] 更新代码中的导入路径
- [ ] 更新文件路径引用

### 重组后检查
- [ ] 验证所有文件已正确移动
- [ ] 测试所有功能模块仍能正常工作
- [ ] 更新README中的项目结构说明
- [ ] 提交重组后的项目结构

## 🎯 预期收益

### 短期收益
- 项目结构更清晰，易于理解
- 文件组织更合理，便于维护
- 新用户能快速理解项目架构

### 长期收益
- 提高开发效率
- 降低维护成本
- 为项目扩展奠定良好基础
- 提高代码质量和可读性

## ⚠️ 注意事项

### 风险控制
1. **备份重要文件**: 重组前务必备份所有重要文件
2. **逐步实施**: 分阶段实施重组，避免一次性改动过多
3. **测试验证**: 每个阶段完成后都要测试功能正常性

### 兼容性考虑
1. **路径更新**: 确保所有代码中的文件路径都已更新
2. **导入更新**: 确保所有模块导入路径都已更新
3. **配置文件**: 更新配置文件中的相对路径引用

---

**执行者状态**: 重组方案制定完成，等待规划者确认
**下一步**: 根据规划者反馈开始实施重组
**预计时间**: 2-3小时完成完整重组
