# 🚀 Meme币分析平台 - API接口文档

## 项目概述

这是一个基于Twitter数据分析的智能meme币发现系统，提供完整的后端API接口和现代化Web前端界面。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端Web界面    │    │   Flask API     │    │   数据文件      │
│  (HTML+JS)     │◄──►│   服务器        │◄──►│  (JSON格式)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 快速开始

### 1. 启动API服务器

```bash
# 安装依赖
pip install flask flask-cors

# 启动服务器
python meme_api_server.py
```

服务器将在 `http://localhost:5001` 启动

### 2. 访问Web界面

打开浏览器访问：`http://localhost:5001`

## 📊 API接口文档

### 基础信息

- **基础URL**: `http://localhost:5001`
- **数据格式**: JSON
- **字符编码**: UTF-8

### 接口列表

#### 1. 健康检查
```
GET /api/health
```
**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-20T00:12:38.717307",
  "version": "1.0.0"
}
```

#### 2. Meme币概览
```
GET /api/memes/overview
```
**响应示例**:
```json
{
  "total_memes": 22,
  "known_memes": 14,
  "potential_memes": 8,
  "total_mentions": 1653,
  "total_users": 219,
  "last_update": "2025-08-20T00:12:38.619265"
}
```

#### 3. Meme币列表
```
GET /api/memes?limit={limit}&offset={offset}&category={category}&sort_by={sort_by}
```

**参数说明**:
- `limit`: 每页数量 (默认: 50)
- `offset`: 偏移量 (默认: 0)
- `category`: 分类筛选 (可选)
- `sort_by`: 排序方式 (total_score, mention_count, unique_users)

**响应示例**:
```json
{
  "data": [
    {
      "id": "act",
      "symbol": "ACT",
      "name": "Act I The AI Prophecy",
      "category": "ai_meme",
      "total_score": 392.45,
      "mention_count": 935,
      "unique_users": 63,
      "founded": "2024",
      "description": "AI主题的叙事meme币",
      "social": {
        "twitter": "@ActTheAI",
        "website": "act.ai"
      },
      "detection_type": "known_meme"
    }
  ],
  "pagination": {
    "total": 22,
    "limit": 5,
    "offset": 0,
    "has_more": true
  }
}
```

#### 4. Meme币详情
```
GET /api/memes/{meme_id}
```

**响应示例**:
```json
{
  "id": "act",
  "symbol": "ACT",
  "name": "Act I The AI Prophecy",
  "category": "ai_meme",
  "founded": "2024",
  "description": "AI主题的叙事meme币",
  "social": {
    "twitter": "@ActTheAI",
    "website": "act.ai"
  },
  "metrics": {
    "total_score": 392.45,
    "mention_count": 935,
    "unique_users": 63,
    "sentiment_score": 0.42,
    "meme_signals": 0,
    "community_signals": 0
  },
  "sample_mentions": [...],
  "detection_type": "known_meme",
  "last_update": "2025-08-20T00:12:38.619265"
}
```

#### 5. 分类统计
```
GET /api/memes/categories
```

**响应示例**:
```json
{
  "ai_meme": {
    "count": 2,
    "total_score": 442.65,
    "total_mentions": 1047,
    "total_users": 81,
    "avg_score": 221.33,
    "avg_mentions": 523.5,
    "avg_users": 40.5
  }
}
```

#### 6. KOL概览
```
GET /api/kol/overview
```

#### 7. KOL列表
```
GET /api/kol?limit={limit}&offset={offset}&level={level}
```

#### 8. 搜索功能
```
GET /api/search?q={query}&limit={limit}
```

**参数说明**:
- `q`: 搜索关键词
- `limit`: 结果数量限制 (默认: 20)

#### 9. 数据导出
```
GET /api/export/{data_type}
```

**支持的数据类型**:
- `memes`: 导出所有meme币数据
- `kol`: 导出KOL数据

## 🌐 Web前端功能

### 主要特性

1. **响应式设计**: 支持桌面和移动设备
2. **实时搜索**: 支持关键词搜索meme币
3. **智能筛选**: 按分类、排序方式筛选
4. **分页浏览**: 支持大量数据的分页显示
5. **数据可视化**: 图表展示分类分布和热度分析
6. **现代化UI**: 使用Bootstrap和自定义CSS

### 页面结构

- **概览统计**: 显示市场整体数据
- **搜索筛选**: 搜索和筛选功能
- **Meme币列表**: 分页显示所有meme币
- **数据分析**: 图表分析功能

## 🔧 技术栈

### 后端
- **Flask**: Web框架
- **Flask-CORS**: 跨域支持
- **JSON**: 数据格式

### 前端
- **HTML5**: 页面结构
- **CSS3**: 样式设计
- **JavaScript**: 交互逻辑
- **Bootstrap 5**: UI组件库
- **Chart.js**: 图表库
- **Font Awesome**: 图标库

## 📁 项目文件结构

```
algorithm-test/
├── meme_api_server.py          # Flask API服务器
├── templates/
│   └── index.html             # 前端HTML模板
├── enhanced_meme_detector.py   # 增强版meme检测器
├── modern_visualization.py     # 现代化可视化系统
├── enhanced_meme_detection_results.json  # meme检测结果
├── kol_analysis_results.json   # KOL分析结果
└── README_API.md              # 本文档
```

## 🚀 部署说明

### 开发环境
```bash
python meme_api_server.py
```

### 生产环境
```bash
# 使用Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 meme_api_server:app

# 或使用uWSGI
pip install uwsgi
uwsgi --http :5001 --module meme_api_server:app
```

## 🔍 使用示例

### 1. 获取Top 10 Meme币
```bash
curl "http://localhost:5001/api/memes?limit=10&sort_by=total_score"
```

### 2. 搜索特定meme币
```bash
curl "http://localhost:5001/api/search?q=doge&limit=5"
```

### 3. 按分类筛选
```bash
curl "http://localhost:5001/api/memes?category=ai_meme&limit=20"
```

### 4. 导出所有数据
```bash
curl "http://localhost:5001/api/export/memes" > memes_data.json
```

## 📊 数据字段说明

### Meme币数据结构
- `id`: 唯一标识符
- `symbol`: 代币符号 (如 $ACT)
- `name`: 项目名称
- `category`: 分类 (ai_meme, animal_meme, internet_culture等)
- `total_score`: 综合热度分数
- `mention_count`: 提及次数
- `unique_users`: 参与用户数
- `founded`: 成立时间
- `description`: 项目描述
- `social`: 社交媒体信息
- `detection_type`: 检测类型 (known_meme, potential_meme)

## 🔮 未来扩展

1. **实时数据更新**: 集成Twitter API实时获取数据
2. **价格数据**: 集成CoinGecko等价格API
3. **用户认证**: 添加用户登录和权限管理
4. **移动应用**: 开发React Native移动应用
5. **机器学习**: 集成ML模型预测meme币趋势

## 📞 技术支持

如有问题或建议，请查看项目代码或联系开发团队。

---

**🎯 现在您有了一个完整的、可交互的Meme币分析平台！**
