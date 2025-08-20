#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter数据采集定时任务调度器
实现每天一次的数据采集，集成到现有系统
"""

import schedule
import time
import logging
import json
from datetime import datetime
from twitter_data_collector import TwitterDataCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterDataScheduler:
    """Twitter数据采集调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.collector = None
        self.kol_users = self._load_kol_users()
        self.setup_collector()
    
    def _load_kol_users(self) -> list:
        """从现有数据中加载KOL用户列表"""
        try:
            # 尝试从enhanced_kol_profiles.json加载KOL用户
            with open('enhanced_kol_profiles.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                kol_users = []
                
                # 提取KOL用户ID
                if 'kol_profiles' in data:
                    for profile in data['kol_profiles']:
                        if 'user_id' in profile:
                            kol_users.append(profile['user_id'])
                
                logger.info(f"从现有数据加载了 {len(kol_users)} 个KOL用户")
                return kol_users
                
        except FileNotFoundError:
            logger.warning("未找到enhanced_kol_profiles.json，使用默认KOL用户列表")
            # 默认KOL用户列表（用于测试）
            return ["user_001", "user_002", "user_003", "user_004", "user_005"]
        except Exception as e:
            logger.error(f"加载KOL用户失败: {e}")
            return ["user_001", "user_002", "user_003", "user_004", "user_005"]
    
    def setup_collector(self):
        """设置数据采集器"""
        try:
            self.collector = TwitterDataCollector()
            logger.info("数据采集器设置成功")
        except Exception as e:
            logger.error(f"设置数据采集器失败: {e}")
            raise
    
    def daily_collection_task(self):
        """每日数据采集任务"""
        logger.info("开始执行每日数据采集任务")
        
        try:
            start_time = time.time()
            
            # 执行数据采集
            tweets_count, users_count = self.collector.collect_kol_tweets(self.kol_users)
            
            # 获取采集统计
            stats = self.collector.get_collection_stats()
            
            # 记录任务完成信息
            end_time = time.time()
            execution_time = end_time - start_time
            
            task_result = {
                "task_name": "daily_collection",
                "execution_time": execution_time,
                "tweets_collected": tweets_count,
                "users_updated": users_count,
                "total_tweets": stats["total_tweets"],
                "total_users": stats["total_users"],
                "total_kols": stats["total_kols"],
                "today_tweets": stats["today_tweets"],
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            # 保存任务结果
            self._save_task_result(task_result)
            
            logger.info(f"每日采集任务完成: 采集 {tweets_count} 条推文，更新 {users_count} 个用户")
            logger.info(f"任务执行时间: {execution_time:.2f} 秒")
            
            return task_result
            
        except Exception as e:
            logger.error(f"每日采集任务失败: {e}")
            
            # 记录失败信息
            task_result = {
                "task_name": "daily_collection",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_task_result(task_result)
            return task_result
    
    def weekly_cleanup_task(self):
        """每周数据清理任务"""
        logger.info("开始执行每周数据清理任务")
        
        try:
            start_time = time.time()
            
            # 清理30天前的旧数据
            self.collector.cleanup_old_data(days=30)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            task_result = {
                "task_name": "weekly_cleanup",
                "execution_time": execution_time,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_task_result(task_result)
            
            logger.info(f"每周清理任务完成，执行时间: {execution_time:.2f} 秒")
            
        except Exception as e:
            logger.error(f"每周清理任务失败: {e}")
            
            task_result = {
                "task_name": "weekly_cleanup",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_task_result(task_result)
    
    def _save_task_result(self, task_result: dict):
        """保存任务执行结果"""
        try:
            # 加载现有任务结果
            results_file = 'task_execution_results.json'
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            except FileNotFoundError:
                results = []
            
            # 添加新结果
            results.append(task_result)
            
            # 只保留最近100条记录
            if len(results) > 100:
                results = results[-100:]
            
            # 保存结果
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"保存任务结果失败: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每天凌晨2点执行数据采集
        schedule.every().day.at("02:00").do(self.daily_collection_task)
        
        # 每周日凌晨3点执行数据清理
        schedule.every().sunday.at("03:00").do(self.weekly_cleanup_task)
        
        logger.info("定时任务设置完成:")
        logger.info("- 每日数据采集: 02:00")
        logger.info("- 每周数据清理: 周日 03:00")
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("启动Twitter数据采集调度器")
        
        # 设置定时任务
        self.setup_schedule()
        
        # 运行调度器
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭调度器...")
        except Exception as e:
            logger.error(f"调度器运行错误: {e}")
        finally:
            self.cleanup()
    
    def run_once(self):
        """立即执行一次采集任务（用于测试）"""
        logger.info("执行一次性采集任务")
        return self.daily_collection_task()
    
    def cleanup(self):
        """清理资源"""
        if self.collector:
            self.collector.close()
        logger.info("调度器已关闭")

def main():
    """主函数"""
    scheduler = TwitterDataScheduler()
    
    try:
        # 检查命令行参数
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "--run-once":
            # 执行一次性任务
            scheduler.run_once()
        else:
            # 运行调度器
            scheduler.run_scheduler()
            
    except Exception as e:
        logger.error(f"调度器运行失败: {e}")
    finally:
        scheduler.cleanup()

if __name__ == "__main__":
    main()

