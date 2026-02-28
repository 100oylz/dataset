"""
CIFAR-10数据集模块

包含CIFAR-10的所有组件：
- raw: 原始数据集
- preprocess: 预处理器
- partition: 划分器
- manager: 联邦学习管理器
"""

from .raw import CIFAR10RawDataset
from .preprocess import CIFAR10Preprocessor
from .partition import (
    CIFAR10Partitioner,
    CIFAR10IIDPartitioner,
    CIFAR10DirichletPartitioner,
    CIFAR10PathologicalPartitioner,
)

# 导入core的FederatedDatasetManager作为基类
from core import FederatedDatasetManager


class CIFAR10FederatedManager(FederatedDatasetManager):
    """
    CIFAR-10联邦学习数据集管理器
    
    完整的CIFAR-10联邦学习数据管理实现
    """
    
    @property
    def dataset_name(self) -> str:
        return "cifar10"
    
    @property
    def raw_dataset_class(self):
        return CIFAR10RawDataset
    
    @property
    def preprocessor_class(self):
        return CIFAR10Preprocessor
    
    @property
    def partitioner_class(self):
        # 返回工厂类，支持动态创建不同策略的划分器
        return CIFAR10Partitioner


__all__ = [
    "CIFAR10RawDataset",
    "CIFAR10Preprocessor",
    "CIFAR10Partitioner",
    "CIFAR10IIDPartitioner",
    "CIFAR10DirichletPartitioner",
    "CIFAR10PathologicalPartitioner",
    "CIFAR10FederatedManager",
]
