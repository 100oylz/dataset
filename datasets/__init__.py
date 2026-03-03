"""
数据集实现模块

包含所有具体数据集的实现：
- mnist: MNIST数据集
- cifar10: CIFAR-10数据集
- fashion_mnist: Fashion-MNIST数据集
- femnist: FEMNIST数据集（联邦学习扩展MNIST，62个类别）

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
    MNISTFederatedManager,
)

# CIFAR-10
from .cifar10 import (
    CIFAR10RawDataset,
    CIFAR10Preprocessor,
    CIFAR10Partitioner,
    CIFAR10IIDPartitioner,
    CIFAR10DirichletPartitioner,
    CIFAR10PathologicalPartitioner,
    CIFAR10FederatedManager,
)

# Fashion-MNIST
from .fashion_mnist import (
    FashionMNISTRawDataset,
    FashionMNISTPreprocessor,
    FashionMNISTPartitioner,
    FashionMNISTIIDPartitioner,
    FashionMNISTDirichletPartitioner,
    FashionMNISTPathologicalPartitioner,
    FashionMNISTFederatedManager,
)

# FEMNIST
from .femnist import (
    FEMNISTRawDataset,
    FEMNISTPreprocessor,
    FEMNISTPartitioner,
    FEMNISTIIDPartitioner,
    FEMNISTDirichletPartitioner,
    FEMNISTPathologicalPartitioner,
    FEMNISTFederatedManager,
)

# 数据集注册导入功能
from .registry import (
    DatasetRegistryImporter,
    register_all,
    register_datasets,
    register_strategies,
)

__all__ = [
    # MNIST
    "MNISTRawDataset",
    "MNISTPreprocessor",
    "MNISTPartitioner",
    "MNISTIIDPartitioner",
    "MNISTDirichletPartitioner",
    "MNISTPathologicalPartitioner",
    "MNISTFederatedManager",
    # CIFAR-10
    "CIFAR10RawDataset",
    "CIFAR10Preprocessor",
    "CIFAR10Partitioner",
    "CIFAR10IIDPartitioner",
    "CIFAR10DirichletPartitioner",
    "CIFAR10PathologicalPartitioner",
    "CIFAR10FederatedManager",
    # Fashion-MNIST
    "FashionMNISTRawDataset",
    "FashionMNISTPreprocessor",
    "FashionMNISTPartitioner",
    "FashionMNISTIIDPartitioner",
    "FashionMNISTDirichletPartitioner",
    "FashionMNISTPathologicalPartitioner",
    "FashionMNISTFederatedManager",
    # FEMNIST
    "FEMNISTRawDataset",
    "FEMNISTPreprocessor",
    "FEMNISTPartitioner",
    "FEMNISTIIDPartitioner",
    "FEMNISTDirichletPartitioner",
    "FEMNISTPathologicalPartitioner",
    "FEMNISTFederatedManager",
    # 辅助函数
    "get_dataset_module",
    "list_available_datasets",
    "get_raw_dataset_class",
    "get_preprocessor_class",
    "get_partitioner_class",
    "get_federated_manager_class",
    "create_federated_manager",
    # 数据集注册导入功能
    "DatasetRegistryImporter",
    "register_all",
    "register_datasets",
    "register_strategies",
]

# 数据集注册表
_DATASET_REGISTRY = {
    "mnist": {
        "raw": MNISTRawDataset,
        "preprocessor": MNISTPreprocessor,
        "partitioner": MNISTPartitioner,
        "manager": MNISTFederatedManager,
        "module": "datasets.mnist",
    },
    "cifar10": {
        "raw": CIFAR10RawDataset,
        "preprocessor": CIFAR10Preprocessor,
        "partitioner": CIFAR10Partitioner,
        "manager": CIFAR10FederatedManager,
        "module": "datasets.cifar10",
    },
    "fashion_mnist": {
        "raw": FashionMNISTRawDataset,
        "preprocessor": FashionMNISTPreprocessor,
        "partitioner": FashionMNISTPartitioner,
        "manager": FashionMNISTFederatedManager,
        "module": "datasets.fashion_mnist",
    },
    "femnist": {
        "raw": FEMNISTRawDataset,
        "preprocessor": FEMNISTPreprocessor,
        "partitioner": FEMNISTPartitioner,
        "manager": FEMNISTFederatedManager,
        "module": "datasets.femnist",
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


def get_federated_manager_class(dataset_name: str) -> Optional[Any]:
    """
    获取联邦学习管理器类
    
    Args:
        dataset_name: 数据集名称
        
    Returns:
        联邦学习管理器类，如果不存在则返回None
    """
    dataset_name = dataset_name.lower()
    if dataset_name in _DATASET_REGISTRY:
        return _DATASET_REGISTRY[dataset_name].get("manager")
    return None


def create_federated_manager(
    dataset_name: str,
    data_root: str,
    num_clients: int,
    partition_strategy: str = "iid",
    partition_params: Optional[Dict[str, Any]] = None,
    seed: int = 42,
    **kwargs
) -> Optional[Any]:
    """
    创建联邦学习管理器实例
    
    便捷函数，用于快速创建指定数据集的联邦学习管理器
    
    Args:
        dataset_name: 数据集名称
        data_root: 数据根目录
        num_clients: 客户端数量
        partition_strategy: 划分策略（iid/dirichlet/pathological）
        partition_params: 划分策略参数
        seed: 随机种子
        **kwargs: 其他参数
        
    Returns:
        联邦学习管理器实例，如果数据集不存在则返回None
        
    Example:
        >>> manager = create_federated_manager(
        ...     dataset_name="mnist",
        ...     data_root="./data",
        ...     num_clients=10,
        ...     partition_strategy="dirichlet",
        ...     partition_params={"alpha": 0.5}
        ... )
        >>> manager.prepare_data()
        >>> loader = manager.get_client_loader(0, batch_size=32)
    """
    manager_class = get_federated_manager_class(dataset_name)
    if manager_class is None:
        return None
    
    return manager_class(
        data_root=data_root,
        num_clients=num_clients,
        partition_strategy=partition_strategy,
        partition_params=partition_params or {},
        seed=seed,
        **kwargs
    )


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
