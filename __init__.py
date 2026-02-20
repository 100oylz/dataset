"""
联邦学习数据集管理框架

提供数据集管理、预处理和联邦划分功能

架构说明：
- core: 核心基类（RawDatasetBase, PreprocessorBase, PartitionerBase, DatasetManagerBase）
- database: 数据库模块（注册信息、动态导入）
- datasets: 具体数据集实现（每个数据集有自己的raw, preprocess, partition模块）
- configs: 配置管理
- utils: 工具函数

使用示例：
    # 方式1：直接使用数据集管理器
    from datasets import MNISTManager
    
    manager = MNISTManager(
        data_root="./data",
        num_clients=10,
        partition_strategy="dirichlet"
    )
    manager.prepare_data()
    
    loader = manager.get_client_loader(0, batch_size=32)
    
    # 方式2：通过工厂动态创建
    from database import DatasetFactory
    
    factory = DatasetFactory()
    manager = factory.create(
        dataset_name="mnist",
        data_root="./data",
        num_clients=10,
        partition_strategy="dirichlet"
    )
"""

__version__ = "2.0.0"

# 导出核心基类
from core import (
    RawDatasetBase,
    PreprocessorBase,
    PartitionerBase,
    DatasetManagerBase,
)

# 导出数据库模块
from database import (
    DatasetRegistration,
    DatasetRegistry,
    DynamicImporter,
    DatasetFactory,
)

# 导出配置模块
from configs import DatasetConfig, build_config

# 导出工具函数
from utils import set_seed, get_device

__all__ = [
    # 版本
    "__version__",
    # 核心基类
    "RawDatasetBase",
    "PreprocessorBase",
    "PartitionerBase",
    "DatasetManagerBase",
    # 数据库
    "DatasetRegistration",
    "DatasetRegistry",
    "DynamicImporter",
    "DatasetFactory",
    # 配置
    "DatasetConfig",
    "build_config",
    # 工具
    "set_seed",
    "get_device",
]


def initialize():
    """
    初始化框架
    
    加载所有内置数据集到注册中心
    """
    # TODO: 实现初始化逻辑
    pass
