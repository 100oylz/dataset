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

from typing import List, Optional, Dict, Any
import importlib

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
    # 辅助函数
    "get_dataset_module",
    "list_available_datasets",
    "get_raw_dataset_class",
    "get_preprocessor_class",
    "get_partitioner_class",
]

# 数据集注册表
_DATASET_REGISTRY = {
    "mnist": {
        "raw": MNISTRawDataset,
        "preprocessor": MNISTPreprocessor,
        "partitioner": MNISTPartitioner,
        "module": "datasets.mnist",
    },
    "cifar10": {
        "raw": CIFAR10RawDataset,
        "preprocessor": CIFAR10Preprocessor,
        "partitioner": CIFAR10Partitioner,
        "module": "datasets.cifar10",
    },
    "fashion_mnist": {
        "raw": FashionMNISTRawDataset,
        "preprocessor": FashionMNISTPreprocessor,
        "partitioner": FashionMNISTPartitioner,
        "module": "datasets.fashion_mnist",
    },
}


def get_dataset_module(dataset_name: str) -> Optional[Any]:
    """
    获取数据集模块
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        数据集模块，如果不存在则返回None
    """
    dataset_name = dataset_name.lower()
    if dataset_name not in _DATASET_REGISTRY:
        return None
    
    module_name = _DATASET_REGISTRY[dataset_name]["module"]
    return importlib.import_module(module_name)


def list_available_datasets() -> List[str]:
    """
    列出可用数据集
    
    Returns:
        数据集名称列表
    """
    return list(_DATASET_REGISTRY.keys())


def get_raw_dataset_class(dataset_name: str) -> Optional[Any]:
    """
    获取原始数据集类
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        原始数据集类，如果不存在则返回None
    """
    dataset_name = dataset_name.lower()
    if dataset_name in _DATASET_REGISTRY:
        return _DATASET_REGISTRY[dataset_name]["raw"]
    return None


def get_preprocessor_class(dataset_name: str) -> Optional[Any]:
    """
    获取预处理器类
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        预处理器类，如果不存在则返回None
    """
    dataset_name = dataset_name.lower()
    if dataset_name in _DATASET_REGISTRY:
        return _DATASET_REGISTRY[dataset_name]["preprocessor"]
    return None


def get_partitioner_class(dataset_name: str) -> Optional[Any]:
    """
    获取划分器类
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        划分器类，如果不存在则返回None
    """
    dataset_name = dataset_name.lower()
    if dataset_name in _DATASET_REGISTRY:
        return _DATASET_REGISTRY[dataset_name]["partitioner"]
    return None


def get_dataset_info(dataset_name: str) -> Optional[Dict[str, Any]]:
    """
    获取数据集信息
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        数据集信息字典，包含名称、类别数、样本数等
    """
    raw_class = get_raw_dataset_class(dataset_name)
    if raw_class is None:
        return None
    
    # 创建一个临时实例来获取信息（不实际加载数据）
    # 使用虚拟路径
    try:
        from pathlib import Path
        temp_instance = raw_class(data_root="/tmp/dataset_temp", download=False)
        return temp_instance.get_dataset_info()
    except Exception:
        # 如果创建实例失败，返回基本信息
        return {
            "name": dataset_name,
            "num_classes": raw_class.NUM_CLASSES,
            "num_features": raw_class.NUM_FEATURES,
            "input_shape": raw_class.INPUT_SHAPE,
            "train_samples": raw_class.TRAIN_SAMPLES,
            "test_samples": raw_class.TEST_SAMPLES,
            "class_names": raw_class.CLASS_NAMES,
        }
