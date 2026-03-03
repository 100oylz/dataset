"""
FEMNIST数据集模块

包含FEMNIST的所有组件：
- raw: 原始数据集
- preprocess: 预处理器
- partition: 划分器
- manager: 联邦学习管理器

FEMNIST (Federated Extended MNIST) 包含 62 个类别：
- 10 个数字 (0-9)
- 26 个大写字母 (A-Z)
- 26 个小写字母 (a-z)
"""

from .raw import FEMNISTRawDataset
from .preprocess import FEMNISTPreprocessor
from .partition import (
    FEMNISTPartitioner,
    FEMNISTIIDPartitioner,
    FEMNISTDirichletPartitioner,
    FEMNISTPathologicalPartitioner,
)

# 导入core的FederatedDatasetManager作为基类
from core import FederatedDatasetManager


class FEMNISTFederatedManager(FederatedDatasetManager):
    """
    FEMNIST联邦学习数据集管理器
    
    完整的FEMNIST联邦学习数据管理实现
    
    FEMNIST特点：
    - 62个类别（10数字 + 26大写字母 + 26小写字母）
    - 28x28 灰度图像
    - ~697K 训练样本，~116K 测试样本
    """
    
    @property
    def dataset_name(self) -> str:
        return "femnist"
    
    @property
    def raw_dataset_class(self):
        return FEMNISTRawDataset
    
    @property
    def preprocessor_class(self):
        return FEMNISTPreprocessor
    
    @property
    def partitioner_class(self):
        # 返回工厂类，支持动态创建不同策略的划分器
        return FEMNISTPartitioner


__all__ = [
    "FEMNISTRawDataset",
    "FEMNISTPreprocessor",
    "FEMNISTPartitioner",
    "FEMNISTIIDPartitioner",
    "FEMNISTDirichletPartitioner",
    "FEMNISTPathologicalPartitioner",
    "FEMNISTFederatedManager",
]
