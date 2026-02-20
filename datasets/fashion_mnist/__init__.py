"""
Fashion-MNIST数据集模块

包含Fashion-MNIST的所有组件：
- raw: 原始数据集
- preprocess: 预处理器
- partition: 划分器
"""

from .raw import FashionMNISTRawDataset
from .preprocess import FashionMNISTPreprocessor
from .partition import (
    FashionMNISTPartitioner,
    FashionMNISTIIDPartitioner,
    FashionMNISTDirichletPartitioner,
    FashionMNISTPathologicalPartitioner,
)

__all__ = [
    "FashionMNISTRawDataset",
    "FashionMNISTPreprocessor",
    "FashionMNISTPartitioner",
    "FashionMNISTIIDPartitioner",
    "FashionMNISTDirichletPartitioner",
    "FashionMNISTPathologicalPartitioner",
]
