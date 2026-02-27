"""
数据库模块

提供数据集注册、查询和动态导入功能
支持 MySQL 数据库存储
"""

from .models import (
    DatasetRegistration,
    PartitionStrategy,
    PartitionResult,
    DATASET_TABLE_SQL,
)
from .db_connection import (
    DatabaseConfig,
    DatabaseConnection,
    get_db,
    init_database,
    close_database,
)
from .dataset_registry import (
    DatasetRegistry,
    PartitionStrategyRegistry,
    PartitionResultRegistry,
)
from .dynamic_importer import (
    DynamicImporter,
    DatasetFactory,
)

__all__ = [
    # 数据模型
    "DatasetRegistration",
    "PartitionStrategy",
    "PartitionResult",
    "DATASET_TABLE_SQL",
    # 数据库连接
    "DatabaseConfig",
    "DatabaseConnection",
    "get_db",
    "init_database",
    "close_database",
    # 注册中心
    "DatasetRegistry",
    "PartitionStrategyRegistry",
    "PartitionResultRegistry",
    # 动态导入
    "DynamicImporter",
    "DatasetFactory",
]
