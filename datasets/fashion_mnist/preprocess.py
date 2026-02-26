"""
Fashion-MNIST预处理模块

实现Fashion-MNIST数据集的专用预处理器
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import torch
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms

from core import PreprocessorBase


class FashionMNISTPreprocessor(PreprocessorBase):
    """
    Fashion-MNIST预处理器
    
    职责：
    1. 实现Fashion-MNIST的归一化
    2. 支持数据增强
    3. 提供训练和测试的不同变换
    
    Fashion-MNIST统计信息：
    - 均值: [0.2860]
    - 标准差: [0.3530]
    """
    
    # Fashion-MNIST标准化参数
    MEAN: List[float] = [0.2860]
    STD: List[float] = [0.3530]
    
    def __init__(
        self,
        dataset_name: str = "fashion_mnist",
        augment: bool = True,
        rotation_degrees: float = 10.0,
        **kwargs
    ) -> None:
        """
        初始化Fashion-MNIST预处理器
        
        Args:
            dataset_name: 数据集名称
            augment: 是否使用数据增强
            rotation_degrees: 随机旋转角度
            **kwargs: 其他参数
        """
        super().__init__(dataset_name, **kwargs)
        self.augment = augment
        self.rotation_degrees = rotation_degrees
        
        # 存储参数
        self._params = {
            "augment": augment,
            "rotation_degrees": rotation_degrees,
            "mean": self.MEAN,
            "std": self.STD
        }
    
    @property
    def name(self) -> str:
        """预处理器名称"""
        return "fashion_mnist_preprocessor"
    
    def fit(self, dataset: Dataset) -> "FashionMNISTPreprocessor":
        """
        拟合预处理器
        
        对于Fashion-MNIST，使用预计算的统计量，无需拟合
        
        Args:
            dataset: 数据集（忽略）
            
        Returns:
            self
        """
        # Fashion-MNIST使用预计算的统计量，无需拟合
        return self
    
    def get_train_transform(self) -> Callable:
        """
        获取Fashion-MNIST训练变换
        
        包括：
        - 数据增强（可选）
        - 转换为Tensor
        - 归一化
        
        Returns:
            训练变换函数
        """
        transform_list = []
        
        # 数据增强
        if self.augment:
            transform_list.append(
                transforms.RandomRotation(degrees=self.rotation_degrees)
            )
        
        # 转换为Tensor并归一化
        transform_list.append(transforms.ToTensor())
        transform_list.append(
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        )
        
        return transforms.Compose(transform_list)
    
    def get_test_transform(self) -> Callable:
        """
        获取Fashion-MNIST测试变换
        
        包括：
        - 转换为Tensor
        - 归一化
        
        Returns:
            测试变换函数
        """
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        ])
    
    def inverse_transform(self, data: torch.Tensor) -> torch.Tensor:
        """
        Fashion-MNIST反归一化
        
        Args:
            data: 归一化后的数据
            
        Returns:
            反归一化数据
        """
        mean = torch.tensor(self.MEAN, device=data.device).view(-1, 1, 1)
        std = torch.tensor(self.STD, device=data.device).view(-1, 1, 1)
        return data * std + mean
    
    def save_params(self, path: str) -> None:
        """保存预处理参数"""
        super().save_params(path)
    
    def load_params(self, path: str) -> "FashionMNISTPreprocessor":
        """加载预处理参数"""
        super().load_params(path)
        return self
    
    def get_params(self) -> Dict[str, Any]:
        """获取预处理参数"""
        return self._params.copy()
    
    def set_params(self, params: Dict[str, Any]) -> "FashionMNISTPreprocessor":
        """设置预处理参数"""
        self._params.update(params)
        self.augment = params.get("augment", self.augment)
        self.rotation_degrees = params.get("rotation_degrees", self.rotation_degrees)
        return self
