#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meme币分析API服务器
提供RESTful接口，支持实时数据查询和交互
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
import pandas as pd
from collections import defaultdict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

class MemeDataService:
    """Meme数据服务类"""
    
    def __init__(self):
        self.data_cache = {}
        self.last_update = None
        self.load_data()
    
    def load_data(self):
        """加载所有数据文件"""
        try:
            # 加载增强版meme数据
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from config.paths import MEME_DETECTION_FILE
            if os.path.exists(MEME_DETECTION_FILE):
                with open(MEME_DETECTION_FILE, 'r', encoding='utf-8') as f:
                    self.data_cache['meme_data'] = json.load(f)
                logger.info("✓ 加载meme数据成功")
            
            # 加载KOL数据
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            from config.paths import KOL_ANALYSIS_FILE
            if os.path.exists(KOL_ANALYSIS_FILE):
                with open(KOL_ANALYSIS_FILE, 'r', encoding='utf-8') as f:
                    self.data_cache['kol_data'] = json.load(f)
                logger.info("✓ 加载KOL数据成功")
            
            # 加载KOL增强档案
            from config.paths import KOL_PROFILES_FILE
            if os.path.exists(KOL_PROFILES_FILE):
                with open(KOL_PROFILES_FILE, 'r', encoding='utf-8') as f:
                    self.data_cache['kol_profiles'] = json.load(f)
                logger.info("✓ 加载KOL档案成功")
            
            self.last_update = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
    
    def get_meme_overview(self):
        """获取meme币概览数据"""
        if 'meme_data' not in self.data_cache:
            return {"error": "数据不可用"}
        
        meme_data = self.data_cache['meme_data']
        memes = meme_data['detected_memes']
        
        # 统计概览
        overview = {
            "total_memes": len(memes),
            "known_memes": len([m for m in memes.values() if m.get('detection_type') == 'known_meme']),
            "potential_memes": len([m for m in memes.values() if m.get('detection_type') == 'potential_meme']),
            "total_mentions": sum(m.get('mention_count', 0) for m in memes.values()),
            "total_users": sum(m.get('unique_users', 0) for m in memes.values()),
            "last_update": self.last_update
        }
        
        return overview
    
    def get_meme_list(self, limit=50, offset=0, category=None, sort_by='total_score'):
        """获取meme币列表"""
        if 'meme_data' not in self.data_cache:
            return {"error": "数据不可用"}
        
        memes = self.data_cache['meme_data']['detected_memes']
        
        # 过滤 - 改进空分类参数处理
        if category and category.strip() != '':
            memes = {k: v for k, v in memes.items() if v.get('category') == category}
        
        # 排序
        sorted_memes = sorted(memes.items(), key=lambda x: x[1].get(sort_by, 0), reverse=True)
        
        # 分页
        paginated_memes = sorted_memes[offset:offset + limit]
        
        # 格式化输出
        result = []
        for meme_key, data in paginated_memes:
            meme_info = {
                "id": meme_key,
                "symbol": data.get('symbol', meme_key.upper()),
                "name": data.get('name', 'Unknown'),
                "category": data.get('category', 'unknown'),
                "total_score": data.get('total_score', 0),
                "mention_count": data.get('mention_count', 0),
                "unique_users": data.get('unique_users', 0),
                "founded": data.get('founded', 'Unknown'),
                "description": data.get('description', ''),
                "social": data.get('social', {}),
                "detection_type": data.get('detection_type', 'unknown')
            }
            result.append(meme_info)
        
        return {
            "data": result,
            "pagination": {
                "total": len(memes),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(memes)
            }
        }
    
    def get_meme_detail(self, meme_id):
        """获取单个meme币详细信息"""
        if 'meme_data' not in self.data_cache:
            return {"error": "数据不可用"}
        
        memes = self.data_cache['meme_data']['detected_memes']
        
        if meme_id not in memes:
            return {"error": "Meme币不存在"}
        
        data = memes[meme_id]
        
        # 获取相关推文上下文
        sample_mentions = data.get('sample_mentions', [])
        
        # 构建详细信息
        detail = {
            "id": meme_id,
            "symbol": data.get('symbol', meme_id.upper()),
            "name": data.get('name', 'Unknown'),
            "category": data.get('category', 'unknown'),
            "founded": data.get('founded', 'Unknown'),
            "description": data.get('description', ''),
            "social": data.get('social', {}),
            "metrics": {
                "total_score": data.get('total_score', 0),
                "mention_count": data.get('mention_count', 0),
                "unique_users": data.get('unique_users', 0),
                "sentiment_score": data.get('sentiment_score', 0),
                "meme_signals": data.get('meme_signals', 0),
                "community_signals": data.get('community_signals', 0)
            },
            "sample_mentions": sample_mentions,
            "detection_type": data.get('detection_type', 'unknown'),
            "last_update": self.last_update
        }
        
        return detail
    
    def get_meme_categories(self):
        """获取meme币分类统计"""
        if 'meme_data' not in self.data_cache:
            return {"error": "数据不可用"}
        
        memes = self.data_cache['meme_data']['detected_memes']
        
        category_stats = defaultdict(lambda: {
            "count": 0,
            "total_score": 0,
            "total_mentions": 0,
            "total_users": 0
        })
        
        for data in memes.values():
            category = data.get('category', 'unknown')
            category_stats[category]["count"] += 1
            category_stats[category]["total_score"] += data.get('total_score', 0)
            category_stats[category]["total_mentions"] += data.get('mention_count', 0)
            category_stats[category]["total_users"] += data.get('unique_users', 0)
        
        # 计算平均值
        for category in category_stats:
            count = category_stats[category]["count"]
            if count > 0:
                category_stats[category]["avg_score"] = category_stats[category]["total_score"] / count
                category_stats[category]["avg_mentions"] = category_stats[category]["total_mentions"] / count
                category_stats[category]["avg_users"] = category_stats[category]["total_users"] / count
        
        return dict(category_stats)
    
    def get_kol_overview(self):
        """获取KOL概览数据"""
        if 'kol_data' not in self.data_cache:
            return {"error": "KOL数据不可用"}
        
        kol_data = self.data_cache['kol_data']
        kol_report = kol_data.get('kol_report', {})
        
        overview = {
            "total_kols": kol_report.get('summary', {}).get('total_kols', 0),
            "total_users": kol_report.get('summary', {}).get('total_users', 0),
            "kol_percentage": kol_report.get('summary', {}).get('kol_percentage', 0),
            "last_update": self.last_update
        }
        
        return overview
    
    def get_kol_list(self, limit=50, offset=0, level=None):
        """获取KOL列表"""
        if 'kol_data' not in self.data_cache:
            return {"error": "KOL数据不可用"}
        
        kol_data = self.data_cache['kol_data']
        kol_users = kol_data.get('kol_report', {}).get('top_kols', [])
        
        # 过滤
        if level:
            kol_users = [k for k in kol_users if level in k.get('kol_level', '')]
        
        # 分页
        paginated_kols = kol_users[offset:offset + limit]
        
        # 格式化输出
        result = []
        for kol in paginated_kols:
            kol_info = {
                "user_id": kol.get('user_id', ''),
                "user_name": kol.get('user_name', ''),
                "influence_score": kol.get('influence_score', 0),
                "follower_count": kol.get('follower_count', 0),
                "engagement_rate": kol.get('engagement_rate', 0),
                "kol_level": kol.get('kol_level', ''),
                "category": kol.get('category', 'general')
            }
            result.append(kol_info)
        
        return {
            "data": result,
            "pagination": {
                "total": len(kol_users),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(kol_users)
            }
        }
    
    def search_memes(self, query, limit=20):
        """搜索meme币"""
        if 'meme_data' not in self.data_cache:
            return {"error": "数据不可用"}
        
        memes = self.data_cache['meme_data']['detected_memes']
        query = query.lower()
        
        results = []
        for meme_key, data in memes.items():
            # 搜索符号、名称、描述
            if (query in meme_key.lower() or 
                query in data.get('symbol', '').lower() or
                query in data.get('name', '').lower() or
                query in data.get('description', '').lower()):
                
                meme_info = {
                    "id": meme_key,
                    "symbol": data.get('symbol', meme_key.upper()),
                    "name": data.get('name', 'Unknown'),
                    "category": data.get('category', 'unknown'),
                    "total_score": data.get('total_score', 0),
                    "mention_count": data.get('mention_count', 0),
                    "description": data.get('description', '')[:100] + "..." if len(data.get('description', '')) > 100 else data.get('description', '')
                }
                results.append(meme_info)
        
        # 按分数排序
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        return {
            "query": query,
            "results": results[:limit],
            "total_found": len(results)
        }

# 创建数据服务实例
data_service = MemeDataService()

# API路由
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """调试页面"""
    return render_template('debug_filter.html')

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/memes/overview')
def get_meme_overview():
    """获取meme币概览"""
    return jsonify(data_service.get_meme_overview())

@app.route('/api/memes')
def get_meme_list():
    """获取meme币列表"""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    category = request.args.get('category')
    sort_by = request.args.get('sort_by', 'total_score')
    
    return jsonify(data_service.get_meme_list(limit, offset, category, sort_by))

@app.route('/api/memes/<meme_id>')
def get_meme_detail(meme_id):
    """获取meme币详情"""
    return jsonify(data_service.get_meme_detail(meme_id))

@app.route('/api/memes/categories')
def get_meme_categories():
    """获取meme币分类统计"""
    return jsonify(data_service.get_meme_categories())

@app.route('/api/kol/overview')
def get_kol_overview():
    """获取KOL概览"""
    return jsonify(data_service.get_kol_overview())

@app.route('/api/kol')
def get_kol_list():
    """获取KOL列表"""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    level = request.args.get('level')
    
    return jsonify(data_service.get_kol_list(limit, offset, level))

@app.route('/api/search')
def search_memes():
    """搜索meme币"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({"error": "查询参数不能为空"})
    
    return jsonify(data_service.search_memes(query, limit))

@app.route('/api/export/<data_type>')
def export_data(data_type):
    """导出数据"""
    if data_type == 'memes':
        if 'meme_data' in data_service.data_cache:
            return jsonify(data_service.data_cache['meme_data'])
        else:
            return jsonify({"error": "数据不可用"})
    
    elif data_type == 'kol':
        if 'kol_data' in data_service.data_cache:
            return jsonify(data_service.data_cache['kol_data'])
        else:
            return jsonify({"error": "数据不可用"})
    
    else:
        return jsonify({"error": "不支持的数据类型"})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "接口不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    print("=== Meme币分析API服务器 ===")
    print("启动服务器...")
    
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5001, debug=True)
