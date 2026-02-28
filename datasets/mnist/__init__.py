"""
MNIST数据集模块

包含MNIST的所有组件：
- raw: 原始数据集
- preprocess: 预处理器
- partition: 划分器
- manager: 联邦学习管理器
"""

from .raw import MNISTRawDataset
from .preprocess import MNISTPreprocessor
from .partition import (
    MNISTPartitioner,
    MNISTIIDPartitioner,
    MNISTDirichletPartitioner,
    MNISTPathologicalPartitioner,
)

# 导入core的FederatedDatasetManager作为基类
from core import FederatedDatasetManager


class MNISTFederatedManager(FederatedDatasetManager):
    """
    MNIST联邦学习数据集管理器
    
    完整的MNIST联邦学习数据管理实现
    """
    
    @property
    def dataset_name(self) -> str:
        return "mnist"
    
    @property
    def raw_dataset_class(self):
        return MNISTRawDataset
    
    @property
    def preprocessor_class(self):
        return MNISTPreprocessor
    
    @property
    def partitioner_class(self):
        # 返回工厂类，支持动态创建不同策略的划分器
        return MNISTPartitioner


__all__ = [
    "MNISTRawDataset",
    "MNISTPreprocessor",
    "MNISTPartitioner",
    "MNISTIIDPartitioner",
    "MNISTDirichletPartitioner",
    "MNISTPathologicalPartitioner",
    "MNISTFederatedManager",
]
