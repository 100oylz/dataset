"""
数据集实现模块

包含所有具体数据集的实现：
- mnist: MNIST数据集
- cifar10: CIFAR-10数据集
- fashion_mnist: Fashion-MNIST数据集

每个数据集包含：
- raw: 原始数据集类
- preprocess: 预处理器类
- partition: 划分器类
"""

# MNIST
from .mnist import (
    MNISTRawDataset,
    MNISTPreprocessor,
    MNISTPartitioner,
    MNISTIIDPartitioner,
    MNISTDirichletPartitioner,
    MNISTPathologicalPartitioner,
)

# CIFAR-10
from .cifar10 import (
    CIFAR10RawDataset,
    CIFAR10Preprocessor,
    CIFAR10Partitioner,
    CIFAR10IIDPartitioner,
    CIFAR10DirichletPartitioner,
    CIFAR10PathologicalPartitioner,
)

# Fashion-MNIST
from .fashion_mnist import (
    FashionMNISTRawDataset,
    FashionMNISTPreprocessor,
    FashionMNISTPartitioner,
    FashionMNISTIIDPartitioner,
    FashionMNISTDirichletPartitioner,
    FashionMNISTPathologicalPartitioner,
)

__all__ = [
    # MNIST
    "MNISTRawDataset",
    "MNISTPreprocessor",
    "MNISTPartitioner",
    "MNISTIIDPartitioner",
    "MNISTDirichletPartitioner",
    "MNISTPathologicalPartitioner",
    # CIFAR-10
    "CIFAR10RawDataset",
    "CIFAR10Preprocessor",
    "CIFAR10Partitioner",
    "CIFAR10IIDPartitioner",
    "CIFAR10DirichletPartitioner",
    "CIFAR10PathologicalPartitioner",
    # Fashion-MNIST
    "FashionMNISTRawDataset",
    "FashionMNISTPreprocessor",
    "FashionMNISTPartitioner",
    "FashionMNISTIIDPartitioner",
    "FashionMNISTDirichletPartitioner",
    "FashionMNISTPathologicalPartitioner",
]


def get_dataset_module(dataset_name: str):
    """
    获取数据集模块
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        数据集模块
    """
    # TODO: 实现根据名称获取模块的逻辑
    pass


def list_available_datasets() -> List[str]:
    """
    列出可用数据集
    
    Returns:
        数据集名称列表
    """
    # TODO: 实现列出可用数据集的逻辑
    pass
