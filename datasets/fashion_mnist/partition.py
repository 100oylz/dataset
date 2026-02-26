"""
Fashion-MNIST划分模块

实现Fashion-MNIST数据集的专用划分器
"""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from torch.utils.data import Dataset

from core import IIDPartitioner, DirichletPartitioner, PathologicalPartitioner


class FashionMNISTPartitioner:
    """
    Fashion-MNIST划分器工厂
    
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
        创建Fashion-MNIST划分器
        
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
            return FashionMNISTIIDPartitioner(num_clients, seed)
        elif strategy == "dirichlet":
            alpha = kwargs.get("alpha", 0.5)
            return FashionMNISTDirichletPartitioner(num_clients, alpha, seed)
        elif strategy == "pathological":
            shards_per_client = kwargs.get("shards_per_client", 2)
            return FashionMNISTPathologicalPartitioner(num_clients, shards_per_client, seed)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


class FashionMNISTIIDPartitioner(IIDPartitioner):
    """
    Fashion-MNIST IID划分器
    """
    
    def __init__(self, num_clients: int, seed: int = 42) -> None:
        """
        初始化Fashion-MNIST IID划分器
        
        Args:
            num_clients: 客户端数量
            seed: 随机种子
        """
        super().__init__(num_clients, seed)
    
    @property
    def name(self) -> str:
        """划分器名称"""
        return "fashion_mnist_iid"
    
    @property
    def strategy_type(self) -> str:
        """策略类型"""
        return "iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行Fashion-MNIST IID划分
        
        Args:
            dataset: Fashion-MNIST训练数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # 调用父类的IID划分逻辑
        return super().partition(dataset)


class FashionMNISTDirichletPartitioner(DirichletPartitioner):
    """
    Fashion-MNIST Dirichlet划分器
    """
    
    def __init__(
        self,
        num_clients: int,
        alpha: float = 0.5,
        seed: int = 42
    ) -> None:
        """
        初始化Fashion-MNIST Dirichlet划分器
        
        Args:
            num_clients: 客户端数量
            alpha: Dirichlet参数
            seed: 随机种子
        """
        super().__init__(num_clients, alpha, seed)
    
    @property
    def name(self) -> str:
        """划分器名称"""
        return "fashion_mnist_dirichlet"
    
    @property
    def strategy_type(self) -> str:
        """策略类型"""
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行Fashion-MNIST Dirichlet划分
        
        Args:
            dataset: Fashion-MNIST训练数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # 调用父类的Dirichlet划分逻辑
        return super().partition(dataset)


class FashionMNISTPathologicalPartitioner(PathologicalPartitioner):
    """
    Fashion-MNIST病态划分器
    """
    
    def __init__(
        self,
        num_clients: int,
        shards_per_client: int = 2,
        seed: int = 42
    ) -> None:
        """
        初始化Fashion-MNIST病态划分器
        
        Args:
            num_clients: 客户端数量
            shards_per_client: 每个客户端的类别数
            seed: 随机种子
        """
        super().__init__(num_clients, shards_per_client, seed)
    
    @property
    def name(self) -> str:
        """划分器名称"""
        return "fashion_mnist_pathological"
    
    @property
    def strategy_type(self) -> str:
        """策略类型"""
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行Fashion-MNIST病态划分
        
        Args:
            dataset: Fashion-MNIST训练数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # 调用父类的Pathological划分逻辑
        return super().partition(dataset)
