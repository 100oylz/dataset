"""
Fashion-MNIST数据集模块

包含Fashion-MNIST的所有组件：
- raw: 原始数据集
- preprocess: 预处理器
- partition: 划分器
- manager: 联邦学习管理器
"""

from .raw import FashionMNISTRawDataset
from .preprocess import FashionMNISTPreprocessor
from .partition import (
    FashionMNISTPartitioner,
    FashionMNISTIIDPartitioner,
    FashionMNISTDirichletPartitioner,
    FashionMNISTPathologicalPartitioner,
)

# 导入core的FederatedDatasetManager作为基类
from core import FederatedDatasetManager


class FashionMNISTFederatedManager(FederatedDatasetManager):
    """
    Fashion-MNIST联邦学习数据集管理器
    
    完整的Fashion-MNIST联邦学习数据管理实现
    """
    
    @property
    def dataset_name(self) -> str:
        return "fashion_mnist"
    
    @property
    def raw_dataset_class(self):
        return FashionMNISTRawDataset
    
    @property
    def preprocessor_class(self):
        return FashionMNISTPreprocessor
    
    @property
    def partitioner_class(self):
        # 返回工厂类，支持动态创建不同策略的划分器
        return FashionMNISTPartitioner


__all__ = [
    "FashionMNISTRawDataset",
    "FashionMNISTPreprocessor",
    "FashionMNISTPartitioner",
    "FashionMNISTIIDPartitioner",
    "FashionMNISTDirichletPartitioner",
    "FashionMNISTPathologicalPartitioner",
    "FashionMNISTFederatedManager",
]
