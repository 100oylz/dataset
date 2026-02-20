"""
CIFAR-10数据集模块

包含CIFAR-10的所有组件：
- raw: 原始数据集
- preprocess: 预处理器
- partition: 划分器
"""

from .raw import CIFAR10RawDataset
from .preprocess import CIFAR10Preprocessor
from .partition import (
    CIFAR10Partitioner,
    CIFAR10IIDPartitioner,
    CIFAR10DirichletPartitioner,
    CIFAR10PathologicalPartitioner,
)

__all__ = [
    "CIFAR10RawDataset",
    "CIFAR10Preprocessor",
    "CIFAR10Partitioner",
    "CIFAR10IIDPartitioner",
    "CIFAR10DirichletPartitioner",
    "CIFAR10PathologicalPartitioner",
]
