"""
数据集注册管理模块

提供数据集的注册、查询、更新等功能
支持通过数据库存储注册信息
"""

import logging
from typing import Any, Dict, List, Optional, Type

from core import (
    RawDatasetBase,
    PreprocessorBase,
    PartitionerBase,
    DatasetManagerBase,
)
from .models import DatasetRegistration, PartitionStrategy, PartitionResult
from .db_connection import get_db, DatabaseConnection

logger = logging.getLogger(__name__)


class DatasetRegistry:
    """
    数据集注册中心
    
    管理所有已注册数据集的元数据
    支持从数据库加载注册信息
    """
    
    _instance = None
    _datasets: Dict[str, DatasetRegistration] = {}
    _db: Optional[DatabaseConnection] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        初始化注册中心
        
        Args:
            db_connection: 数据库连接，如果为None则使用内存存储
        """
        if db_connection is not None:
            self._db = db_connection
        elif self._db is None:
            try:
                self._db = get_db()
            except Exception as e:
                logger.warning(f"数据库连接失败，使用内存模式: {e}")
                self._db = None
    
    def register(self, registration: DatasetRegistration) -> bool:
        """
        注册数据集
        
        Args:
            registration: 数据集注册信息
            
        Returns:
            是否注册成功
        """
        if not registration.is_valid():
            logger.error(f"数据集注册信息无效: {registration.name}")
            return False
        
        try:
            # 保存到内存
            self._datasets[registration.name] = registration
            
            # 保存到数据库
            if self._db:
                data = registration.to_db_dict()
                
                # 检查是否已存在
                existing = self._db.fetchone(
                    "SELECT id FROM dataset_registrations WHERE name = %s",
                    (registration.name,)
                )
                
                if existing:
                    # 更新
                    self._db.update(
                        "dataset_registrations",
                        data,
                        "name = %s",
                        (registration.name,)
                    )
                    logger.info(f"数据集 '{registration.name}' 已更新")
                else:
                    # 插入
                    self._db.insert("dataset_registrations", data)
                    logger.info(f"数据集 '{registration.name}' 已注册")
            
            return True
            
        except Exception as e:
            logger.error(f"注册数据集失败: {e}")
            return False
    
    def unregister(self, dataset_name: str) -> bool:
        """
        注销数据集
        
        Args:
            dataset_name: 数据集名称
            
        Returns:
            是否注销成功
        """
        try:
            # 从内存中移除
            if dataset_name in self._datasets:
                del self._datasets[dataset_name]
            
            # 从数据库中删除或标记为 deprecated
            if self._db:
                # 软删除：标记为 deprecated
                self._db.execute(
                    "UPDATE dataset_registrations SET status = 'deprecated' WHERE name = %s",
                    (dataset_name,)
                )
                # 或者硬删除
                # self._db.execute(
                #     "DELETE FROM dataset_registrations WHERE name = %s",
                #     (dataset_name,)
                # )
            
            logger.info(f"数据集 '{dataset_name}' 已注销")
            return True
            
        except Exception as e:
            logger.error(f"注销数据集失败: {e}")
            return False
    
    def get(self, dataset_name: str) -> Optional[DatasetRegistration]:
        """
        获取数据集注册信息
        
        Args:
            dataset_name: 数据集名称
            
        Returns:
            数据集注册信息，不存在则返回None
        """
        # 先从内存中查找
        if dataset_name in self._datasets:
            return self._datasets[dataset_name]
        
        # 从数据库中查找
        if self._db:
            try:
                row = self._db.fetchone(
                    "SELECT * FROM dataset_registrations WHERE name = %s AND status = 'active'",
                    (dataset_name,)
                )
                
                if row:
                    registration = DatasetRegistration.from_db_row(row)
                    # 缓存到内存
                    self._datasets[dataset_name] = registration
                    return registration
                    
            except Exception as e:
                logger.error(f"从数据库获取数据集信息失败: {e}")
        
        return None
    
    def list_datasets(
        self,
        data_type: Optional[str] = None,
        task_type: Optional[str] = None,
        status: str = "active"
    ) -> List[DatasetRegistration]:
        """
        列出所有数据集
        
        Args:
            data_type: 按数据类型筛选
            task_type: 按任务类型筛选
            status: 按状态筛选
            
        Returns:
            数据集注册信息列表
        """
        results = []
        
        try:
            if self._db:
                # 构建查询
                conditions = ["status = %s"]
                params = [status]
                
                if data_type:
                    conditions.append("data_type = %s")
                    params.append(data_type)
                
                if task_type:
                    conditions.append("task_type = %s")
                    params.append(task_type)
                
                where_clause = " AND ".join(conditions)
                sql = f"SELECT * FROM dataset_registrations WHERE {where_clause} ORDER BY name"
                
                rows = self._db.fetchall(sql, tuple(params))
                
                for row in rows:
                    registration = DatasetRegistration.from_db_row(row)
                    results.append(registration)
                    # 更新内存缓存
                    self._datasets[registration.name] = registration
            else:
                # 内存模式
                for name, reg in self._datasets.items():
                    if status and reg.status != status:
                        continue
                    if data_type and reg.data_type != data_type:
                        continue
                    if task_type and reg.task_type != task_type:
                        continue
                    results.append(reg)
                
                results.sort(key=lambda x: x.name)
                
        except Exception as e:
            logger.error(f"列出数据集失败: {e}")
        
        return results
    
    def update(self, dataset_name: str, updates: Dict[str, Any]) -> bool:
        """
        更新数据集注册信息
        
        Args:
            dataset_name: 数据集名称
            updates: 要更新的字段
            
        Returns:
            是否更新成功
        """
        try:
            # 更新内存
            if dataset_name in self._datasets:
                reg = self._datasets[dataset_name]
                for key, value in updates.items():
                    if hasattr(reg, key):
                        setattr(reg, key, value)
            
            # 更新数据库
            if self._db:
                self._db.update(
                    "dataset_registrations",
                    updates,
                    "name = %s",
                    (dataset_name,)
                )
            
            logger.info(f"数据集 '{dataset_name}' 已更新")
            return True
            
        except Exception as e:
            logger.error(f"更新数据集失败: {e}")
            return False
    
    def exists(self, dataset_name: str) -> bool:
        """
        检查数据集是否已注册
        
        Args:
            dataset_name: 数据集名称
            
        Returns:
            是否已注册
        """
        if dataset_name in self._datasets:
            return True
        
        if self._db:
            try:
                row = self._db.fetchone(
                    "SELECT 1 FROM dataset_registrations WHERE name = %s AND status = 'active'",
                    (dataset_name,)
                )
                return row is not None
            except Exception as e:
                logger.error(f"检查数据集存在性失败: {e}")
        
        return False
    
    def clear(self) -> None:
        """清空所有注册信息"""
        self._datasets.clear()
        logger.info("内存中的数据集注册信息已清空")
    
    def load_from_database(self) -> int:
        """
        从数据库加载所有注册信息
        
        Returns:
            加载的数据集数量
        """
        if not self._db:
            logger.warning("数据库连接不可用")
            return 0
        
        try:
            rows = self._db.fetchall(
                "SELECT * FROM dataset_registrations WHERE status = 'active'"
            )
            
            count = 0
            for row in rows:
                registration = DatasetRegistration.from_db_row(row)
                self._datasets[registration.name] = registration
                count += 1
            
            logger.info(f"从数据库加载了 {count} 个数据集")
            return count
            
        except Exception as e:
            logger.error(f"从数据库加载失败: {e}")
            return 0
    
    def save_to_database(self) -> int:
        """
        将内存中的注册信息保存到数据库
        
        Returns:
            保存的数据集数量
        """
        if not self._db:
            logger.warning("数据库连接不可用")
            return 0
        
        count = 0
        try:
            for name, registration in self._datasets.items():
                data = registration.to_db_dict()
                
                existing = self._db.fetchone(
                    "SELECT id FROM dataset_registrations WHERE name = %s",
                    (name,)
                )
                
                if existing:
                    self._db.update(
                        "dataset_registrations",
                        data,
                        "name = %s",
                        (name,)
                    )
                else:
                    self._db.insert("dataset_registrations", data)
                
                count += 1
            
            logger.info(f"保存了 {count} 个数据集到数据库")
            return count
            
        except Exception as e:
            logger.error(f"保存到数据库失败: {e}")
            return 0


class PartitionStrategyRegistry:
    """
    划分策略注册中心
    
    管理所有支持的划分策略
    """
    
    _instance = None
    _strategies: Dict[str, PartitionStrategy] = {}
    _db: Optional[DatabaseConnection] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """初始化策略注册中心"""
        if db_connection is not None:
            self._db = db_connection
        elif self._db is None:
            try:
                self._db = get_db()
            except Exception as e:
                logger.warning(f"数据库连接失败，使用内存模式: {e}")
                self._db = None
        
        # 自动加载策略
        if not self._strategies:
            self.load_from_database()
    
    def register(self, strategy: PartitionStrategy) -> bool:
        """
        注册划分策略
        
        Args:
            strategy: 划分策略配置
            
        Returns:
            是否注册成功
        """
        try:
            self._strategies[strategy.name] = strategy
            
            if self._db:
                data = strategy.to_db_dict()
                
                existing = self._db.fetchone(
                    "SELECT id FROM partition_strategies WHERE name = %s",
                    (strategy.name,)
                )
                
                if existing:
                    self._db.update(
                        "partition_strategies",
                        data,
                        "name = %s",
                        (strategy.name,)
                    )
                else:
                    self._db.insert("partition_strategies", data)
            
            logger.info(f"划分策略 '{strategy.name}' 已注册")
            return True
            
        except Exception as e:
            logger.error(f"注册划分策略失败: {e}")
            return False
    
    def get(self, strategy_name: str) -> Optional[PartitionStrategy]:
        """
        获取划分策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            划分策略配置
        """
        if strategy_name in self._strategies:
            return self._strategies[strategy_name]
        
        if self._db:
            try:
                row = self._db.fetchone(
                    "SELECT * FROM partition_strategies WHERE name = %s AND status = 'active'",
                    (strategy_name,)
                )
                
                if row:
                    strategy = PartitionStrategy.from_db_row(row)
                    self._strategies[strategy_name] = strategy
                    return strategy
                    
            except Exception as e:
                logger.error(f"从数据库获取策略失败: {e}")
        
        return None
    
    def list_strategies(self) -> List[PartitionStrategy]:
        """
        列出所有划分策略
        
        Returns:
            划分策略列表
        """
        results = []
        
        try:
            if self._db:
                rows = self._db.fetchall(
                    "SELECT * FROM partition_strategies WHERE status = 'active' ORDER BY name"
                )
                
                for row in rows:
                    strategy = PartitionStrategy.from_db_row(row)
                    results.append(strategy)
                    self._strategies[strategy.name] = strategy
            else:
                results = list(self._strategies.values())
                results.sort(key=lambda x: x.name)
                
        except Exception as e:
            logger.error(f"列出划分策略失败: {e}")
        
        return results
    
    def get_supported_strategies(self, dataset_name: str) -> List[PartitionStrategy]:
        """
        获取数据集支持的划分策略
        
        Args:
            dataset_name: 数据集名称
            
        Returns:
            支持的划分策略列表
        """
        all_strategies = self.list_strategies()
        supported = []
        
        for strategy in all_strategies:
            if dataset_name in strategy.supported_datasets:
                supported.append(strategy)
        
        return supported
    
    def load_from_database(self) -> int:
        """
        从数据库加载所有策略
        
        Returns:
            加载的策略数量
        """
        if not self._db:
            return 0
        
        try:
            rows = self._db.fetchall(
                "SELECT * FROM partition_strategies WHERE status = 'active'"
            )
            
            count = 0
            for row in rows:
                strategy = PartitionStrategy.from_db_row(row)
                self._strategies[strategy.name] = strategy
                count += 1
            
            logger.info(f"从数据库加载了 {count} 个划分策略")
            return count
            
        except Exception as e:
            logger.error(f"从数据库加载策略失败: {e}")
            return 0


class PartitionResultRegistry:
    """
    划分结果注册中心
    
    管理划分结果的存储和查询
    """
    
    _instance = None
    _db: Optional[DatabaseConnection] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """初始化"""
        if db_connection is not None:
            self._db = db_connection
        elif self._db is None:
            try:
                self._db = get_db()
            except Exception as e:
                logger.warning(f"数据库连接失败: {e}")
                self._db = None
    
    def save(self, result: PartitionResult) -> int:
        """
        保存划分结果
        
        Args:
            result: 划分结果
            
        Returns:
            结果 ID
        """
        if not self._db:
            raise RuntimeError("数据库连接不可用")
        
        try:
            data = result.to_db_dict()
            
            # 检查是否已存在
            existing = self._db.fetchone(
                """SELECT id FROM partition_results 
                   WHERE dataset_name = %s AND strategy_name = %s 
                   AND num_clients = %s AND fingerprint = %s""",
                (result.dataset_name, result.strategy_name, 
                 result.num_clients, result.fingerprint)
            )
            
            if existing:
                # 更新
                self._db.update(
                    "partition_results",
                    data,
                    "id = %s",
                    (existing['id'],)
                )
                logger.info(f"划分结果已更新: {result.dataset_name}/{result.strategy_name}")
                return existing['id']
            else:
                # 插入
                result_id = self._db.insert("partition_results", data)
                logger.info(f"划分结果已保存: {result.dataset_name}/{result.strategy_name}")
                return result_id
                
        except Exception as e:
            logger.error(f"保存划分结果失败: {e}")
            raise
    
    def get(
        self,
        dataset_name: str,
        strategy_name: str,
        num_clients: int,
        fingerprint: Optional[str] = None
    ) -> Optional[PartitionResult]:
        """
        获取划分结果
        
        Args:
            dataset_name: 数据集名称
            strategy_name: 策略名称
            num_clients: 客户端数量
            fingerprint: 结果指纹（可选）
            
        Returns:
            划分结果
        """
        if not self._db:
            return None
        
        try:
            if fingerprint:
                row = self._db.fetchone(
                    """SELECT * FROM partition_results 
                       WHERE dataset_name = %s AND strategy_name = %s 
                       AND num_clients = %s AND fingerprint = %s""",
                    (dataset_name, strategy_name, num_clients, fingerprint)
                )
            else:
                # 获取最新的
                row = self._db.fetchone(
                    """SELECT * FROM partition_results 
                       WHERE dataset_name = %s AND strategy_name = %s 
                       AND num_clients = %s 
                       ORDER BY created_at DESC LIMIT 1""",
                    (dataset_name, strategy_name, num_clients)
                )
            
            if row:
                return PartitionResult.from_db_row(row)
            
        except Exception as e:
            logger.error(f"获取划分结果失败: {e}")
        
        return None
    
    def list_results(
        self,
        dataset_name: Optional[str] = None,
        strategy_name: Optional[str] = None
    ) -> List[PartitionResult]:
        """
        列出划分结果
        
        Args:
            dataset_name: 数据集名称筛选
            strategy_name: 策略名称筛选
            
        Returns:
            划分结果列表
        """
        if not self._db:
            return []
        
        try:
            conditions = []
            params = []
            
            if dataset_name:
                conditions.append("dataset_name = %s")
                params.append(dataset_name)
            
            if strategy_name:
                conditions.append("strategy_name = %s")
                params.append(strategy_name)
            
            if conditions:
                where_clause = " AND ".join(conditions)
                sql = f"SELECT * FROM partition_results WHERE {where_clause} ORDER BY created_at DESC"
            else:
                sql = "SELECT * FROM partition_results ORDER BY created_at DESC"
            
            rows = self._db.fetchall(sql, tuple(params))
            
            return [PartitionResult.from_db_row(row) for row in rows]
            
        except Exception as e:
            logger.error(f"列出划分结果失败: {e}")
            return []
