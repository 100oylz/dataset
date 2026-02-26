"""
CIFAR-10划分模块

实现CIFAR-10数据集的专用划分器
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from torch.utils.data import Dataset

from core import IIDPartitioner, DirichletPartitioner, PathologicalPartitioner


class CIFAR10Partitioner:
    """
    CIFAR-10划分器工厂
    
    根据策略名称创建对应的划分器
    """
    
    @staticmethod
    def create(
        strategy: str,
        num_clients: int,
        seed: int = 42,
        **kwargs
    ):
        """
        创建CIFAR-10划分器
        
        Args:
            strategy: 划分策略（"iid"/"dirichlet"/"pathological"）
            num_clients: 客户端数量
            seed: 随机种子
            **kwargs: 策略特定参数
            
        Returns:
            划分器实例
        """
        strategy = strategy.lower()
        
        if strategy == "iid":
            return CIFAR10IIDPartitioner(num_clients, seed)
        elif strategy == "dirichlet":
            alpha = kwargs.get("alpha", 0.5)
            return CIFAR10DirichletPartitioner(num_clients, alpha, seed)
        elif strategy == "pathological":
            shards_per_client = kwargs.get("shards_per_client", 2)
            return CIFAR10PathologicalPartitioner(num_clients, shards_per_client, seed)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


class CIFAR10IIDPartitioner(IIDPartitioner):
    """
    CIFAR-10 IID划分器
    
    将CIFAR-10训练数据随机均匀分配给所有客户端
    """
    
    def __init__(self, num_clients: int, seed: int = 42) -> None:
        """
        初始化CIFAR-10 IID划分器
        
        Args:
            num_clients: 客户端数量
            seed: 随机种子
        """
        super().__init__(num_clients, seed)
    
    @property
    def name(self) -> str:
        """划分器名称"""
        return "cifar10_iid"
    
    @property
    def strategy_type(self) -> str:
        """策略类型"""
        return "iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行CIFAR-10 IID划分
        
        Args:
            dataset: CIFAR-10训练数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # 调用父类的IID划分逻辑
        return super().partition(dataset)


class CIFAR10DirichletPartitioner(DirichletPartitioner):
    """
    CIFAR-10 Dirichlet划分器
    
    基于Dirichlet分布的Non-IID划分
    适用于CIFAR-10的10个类别
    
    Args:
        alpha: Dirichlet参数，默认0.5
    """
    
    def __init__(
        self,
        num_clients: int,
        alpha: float = 0.5,
        seed: int = 42
    ) -> None:
        """
        初始化CIFAR-10 Dirichlet划分器
        
        Args:
            num_clients: 客户端数量
            alpha: Dirichlet参数
            seed: 随机种子
        """
        super().__init__(num_clients, alpha, seed)
    
    @property
    def name(self) -> str:
        """划分器名称"""
        return "cifar10_dirichlet"
    
    @property
    def strategy_type(self) -> str:
        """策略类型"""
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行CIFAR-10 Dirichlet划分
        
        Args:
            dataset: CIFAR-10训练数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # 调用父类的Dirichlet划分逻辑
        return super().partition(dataset)


class CIFAR10PathologicalPartitioner(PathologicalPartitioner):
    """
    CIFAR-10病态划分器
    
    每个客户端只获得特定数量的类别
    
    Args:
        shards_per_client: 每个客户端的类别数，默认2
    """
    
    def __init__(
        self,
        num_clients: int,
        shards_per_client: int = 2,
        seed: int = 42
    ) -> None:
        """
        初始化CIFAR-10病态划分器
        
        Args:
            num_clients: 客户端数量
            shards_per_client: 每个客户端的类别数
            seed: 随机种子
        """
        super().__init__(num_clients, shards_per_client, seed)
    
    @property
    def name(self) -> str:
        """划分器名称"""
        return "cifar10_pathological"
    
    @property
    def strategy_type(self) -> str:
        """策略类型"""
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行CIFAR-10病态划分
        
        Args:
            dataset: CIFAR-10训练数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # 调用父类的Pathological划分逻辑
        return super().partition(dataset)
