# Twitter数据采集系统 - 使用说明

## 🎯 系统概述

这是一个专为单机MVP设计的Twitter数据采集系统，实现小范围、低频率的数据采集，适合分析KOL推文动态和meme信息捕捉。

### ✨ 核心特性

- **小范围采集**: 每天一次，只采集KOL相关推文
- **智能去重**: 基于数据哈希的重复数据过滤
- **PostgreSQL存储**: 专业的数据处理能力
- **定时任务**: 自动化数据采集和清理
- **性能优化**: 控制数据量，避免处理瓶颈

## 🏗️ 系统架构

```
Twitter API → 数据采集器 → PostgreSQL → 分析引擎 → Web界面
    ↓              ↓           ↓          ↓         ↓
  原始推文     结构化数据    持久化存储    业务分析    可视化展示
```

## 📋 系统要求

### 硬件要求
- **存储空间**: 至少20GB可用空间
- **内存**: 建议4GB以上
- **CPU**: 支持Python 3.8+

### 软件要求
- **操作系统**: Windows/macOS/Linux
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **依赖包**: 见requirements_twitter.txt

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements_twitter.txt

# 安装PostgreSQL（如果未安装）
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# 下载并安装PostgreSQL官方安装包
```

### 2. 数据库配置

```bash
# 创建数据库
sudo -u postgres psql
CREATE DATABASE twitter_data;
CREATE USER twitter_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE twitter_data TO twitter_user;
\q
```

### 3. 配置文件设置

编辑`collector_config.json`文件：

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "twitter_data",
    "user": "twitter_user",
    "password": "your_password"
  },
  "twitter_api": {
    "bearer_token": "YOUR_TWITTER_BEARER_TOKEN",
    "base_url": "https://api.twitter.com/2",
    "rate_limit": 450,
    "rate_limit_window": 900
  },
  "collection": {
    "max_tweets_per_run": 5000,
    "max_users_per_run": 1000,
    "time_window_hours": 24,
    "kol_priority": true,
    "meme_keywords": ["doge", "shib", "pepe", "moon", "pump", "fomo"]
  }
}
```

### 4. 运行系统

```bash
# 测试运行（一次性采集）
python twitter_scheduler.py --run-once

# 启动定时任务调度器
python twitter_scheduler.py
```

## 📊 数据采集策略

### 采集频率
- **主要采集**: 每天凌晨2:00
- **数据清理**: 每周日凌晨3:00
- **手动采集**: 支持命令行参数`--run-once`

### 数据范围
- **优先级1**: KOL用户推文（必采集）
- **优先级2**: KOL转发和引用的推文
- **优先级3**: 包含meme关键词的推文
- **优先级4**: 其他相关推文（可选）

### 数据量控制
- **每日推文**: 控制在1-5万条
- **处理时间**: 目标<30分钟
- **存储规模**: 数据库控制在8GB以内

## 🗄️ 数据存储

### 数据库表结构

#### tweets表（推文数据）
- `tweet_id`: 推文唯一标识
- `text`: 推文内容
- `user_id`: 用户ID
- `created_at`: 创建时间
- `hashtags`: 话题标签（JSONB）
- `mentions`: 提及用户（JSONB）
- `data_hash`: 数据哈希（去重用）

#### users表（用户数据）
- `user_id`: 用户唯一标识
- `username`: 用户名
- `is_kol`: 是否为KOL
- `kol_score`: KOL影响力分数
- `kol_tier`: KOL等级

### 索引优化
- 用户ID索引：快速查询用户推文
- 时间索引：按时间范围查询
- 话题标签索引：全文搜索支持
- KOL索引：快速筛选KOL用户

## 🔧 系统配置

### 环境变量（可选）
```bash
# .env文件
TWITTER_BEARER_TOKEN=your_token_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=twitter_data
DB_USER=twitter_user
DB_PASSWORD=your_password
```

### 高级配置
```json
{
  "collection": {
    "max_tweets_per_run": 5000,        // 每次运行最大推文数
    "time_window_hours": 24,           // 采集时间窗口
    "kol_priority": true,              // KOL优先采集
    "meme_keywords": ["doge", "shib"], // meme关键词
    "retry_attempts": 3,               // 重试次数
    "retry_delay": 5                   // 重试延迟（秒）
  }
}
```

## 📈 监控和维护

### 日志文件
- `twitter_collector.log`: 采集器运行日志
- `twitter_scheduler.log`: 调度器运行日志

### 任务执行记录
- `task_execution_results.json`: 任务执行结果
- 包含执行时间、成功状态、错误信息等

### 系统健康检查
```bash
# 检查数据库连接
python -c "from twitter_data_collector import TwitterDataCollector; c = TwitterDataCollector(); print('数据库连接正常')"

# 检查采集统计
python -c "from twitter_data_collector import TwitterDataCollector; c = TwitterDataCollector(); print(c.get_collection_stats())"
```

## 🚨 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql

# 检查数据库配置
psql -h localhost -U twitter_user -d twitter_data
```

#### 2. Twitter API限制
- 检查Bearer Token是否有效
- 确认API调用频率未超限
- 查看API错误响应

#### 3. 存储空间不足
```bash
# 检查磁盘空间
df -h

# 清理旧数据
python -c "from twitter_data_collector import TwitterDataCollector; c = TwitterDataCollector(); c.cleanup_old_data(days=7)"
```

### 性能优化建议

1. **数据库优化**
   - 定期执行VACUUM和ANALYZE
   - 监控慢查询日志
   - 适当调整PostgreSQL配置

2. **采集策略优化**
   - 根据系统性能调整采集频率
   - 优化KOL用户列表
   - 实现智能数据采样

3. **存储优化**
   - 定期清理过期数据
   - 压缩历史数据
   - 实现数据分区

## 🔮 未来扩展

### 短期目标
- [ ] 集成真实Twitter API
- [ ] 实现数据质量监控
- [ ] 添加数据导出功能

### 中期目标
- [ ] 支持多数据源
- [ ] 实现实时数据流
- [ ] 添加机器学习分析

### 长期目标
- [ ] 分布式部署支持
- [ ] 云原生架构
- [ ] 企业级功能

## 📞 技术支持

### 联系方式
- **项目维护**: 算法测试项目组
- **技术支持**: 通过项目仓库提交Issue

### 贡献指南
1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request

---

**🎯 现在您有了一个完整的Twitter数据采集系统！这个系统专为单机MVP设计，支持小范围、低频率的数据采集，完全满足您的需求。**
