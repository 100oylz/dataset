"""
数据划分基类模块

定义所有数据划分器必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset, Subset


class PartitionerBase(ABC):
    """
    数据划分抽象基类
    
    职责：
    1. 将训练数据划分为多个客户端子集
    2. 支持不同的划分策略（IID, Non-IID等）
    3. 提供划分结果的统计信息
    
    注意：只负责索引划分，不实际存储数据
    """
    
    def __init__(self, num_clients: int, seed: int = 42, **kwargs) -> None:
        """
        初始化划分器
        
        Args:
            num_clients: 客户端数量
            seed: 随机种子
            **kwargs: 其他划分特定参数
        """
        # TODO: 初始化划分器参数
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """划分策略名称"""
        # TODO: 返回划分器名称
        pass
    
    @property
    @abstractmethod
    def strategy_type(self) -> str:
        """
        划分策略类型
        
        Returns:
            "iid" 或 "non-iid"
        """
        # TODO: 返回策略类型
        pass
    
    @abstractmethod
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行数据划分
        
        Args:
            dataset: 待划分的数据集
            
        Returns:
            {client_id: [indices]} 字典
        """
        # TODO: 实现划分逻辑
        pass
    
    def get_client_dataset(self, dataset: Dataset, client_id: int, 
                          client_indices: Dict[int, List[int]]) -> Subset:
        """
        获取指定客户端的数据子集
        
        Args:
            dataset: 完整数据集
            client_id: 客户端ID
            client_indices: 划分结果字典
            
        Returns:
            客户端数据子集
        """
        # TODO: 返回Subset
        pass
    
    def get_distribution(self, dataset: Dataset, 
                         client_indices: Dict[int, List[int]]) -> Dict[int, Dict[int, int]]:
        """
        获取各客户端的数据分布
        
        Args:
            dataset: 完整数据集
            client_indices: 划分结果字典
            
        Returns:
            {client_id: {label: count}} 字典
        """
        # TODO: 计算并返回分布信息
        pass
    
    def get_statistics(self, dataset: Dataset,
                      client_indices: Dict[int, List[int]]) -> Dict[str, Any]:
        """
        获取划分的统计信息
        
        Args:
            dataset: 完整数据集
            client_indices: 划分结果字典
            
        Returns:
            统计信息字典
        """
        # TODO: 计算并返回统计信息
        pass
    
    def save_partition(self, client_indices: Dict[int, List[int]], path: str) -> None:
        """
        保存划分结果
        
        Args:
            client_indices: 划分结果字典
            path: 保存路径
        """
        # TODO: 保存划分结果
        pass
    
    def load_partition(self, path: str) -> Dict[int, List[int]]:
        """
        加载划分结果
        
        Args:
            path: 划分结果文件路径
            
        Returns:
            划分结果字典
        """
        # TODO: 加载划分结果
        pass


class IIDPartitioner(PartitionerBase):
    """
    IID划分器（独立同分布）
    
    将数据随机均匀分配给所有客户端
    """
    
    def __init__(self, num_clients: int, seed: int = 42) -> None:
        # TODO: 初始化IID划分器
        pass
    
    @property
    def name(self) -> str:
        # TODO: 返回名称
        pass
    
    @property
    def strategy_type(self) -> str:
        # TODO: 返回策略类型
        pass
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # TODO: 实现IID划分
        pass


class DirichletPartitioner(PartitionerBase):
    """
    Dirichlet划分器（Non-IID）
    
    基于Dirichlet分布的Non-IID划分
    
    Args:
        alpha: Dirichlet分布参数，越小越Non-IID
    """
    
    def __init__(self, num_clients: int, alpha: float = 0.5, seed: int = 42) -> None:
        # TODO: 初始化Dirichlet划分器
        pass
    
    @property
    def name(self) -> str:
        # TODO: 返回名称
        pass
    
    @property
    def strategy_type(self) -> str:
        # TODO: 返回策略类型
        pass
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # TODO: 实现Dirichlet划分
        pass


class PathologicalPartitioner(PartitionerBase):
    """
    病态划分器（Pathological Non-IID）
    
    每个客户端只获得特定数量的类别
    
    Args:
        shards_per_client: 每个客户端的类别数
    """
    
    def __init__(self, num_clients: int, shards_per_client: int = 2, seed: int = 42) -> None:
        # TODO: 初始化病态划分器
        pass
    
    @property
    def name(self) -> str:
        # TODO: 返回名称
        pass
    
    @property
    def strategy_type(self) -> str:
        # TODO: 返回策略类型
        pass
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # TODO: 实现病态划分
        pass
