"""
CIFAR-10预处理模块

实现CIFAR-10数据集的专用预处理器
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import torch
import numpy as np
from torch.utils.data import Dataset
from torchvision import transforms

from core import PreprocessorBase


class CIFAR10Preprocessor(PreprocessorBase):
    """
    CIFAR-10预处理器
    
    职责：
    1. 实现CIFAR-10的归一化
    2. 支持数据增强（RandomCrop, RandomHorizontalFlip等）
    3. 提供训练和测试的不同变换
    
    CIFAR-10统计信息：
    - 均值: [0.4914, 0.4822, 0.4465]
    - 标准差: [0.2470, 0.2435, 0.2616]
    """
    
    # CIFAR-10标准化参数
    MEAN: List[float] = [0.4914, 0.4822, 0.4465]
    STD: List[float] = [0.2470, 0.2435, 0.2616]
    
    def __init__(
        self,
        dataset_name: str = "cifar10",
        augment: bool = True,
        crop_padding: int = 4,
        flip_prob: float = 0.5,
        **kwargs
    ) -> None:
        """
        初始化CIFAR-10预处理器
        
        Args:
            dataset_name: 数据集名称
            augment: 是否使用数据增强
            crop_padding: 随机裁剪填充
            flip_prob: 水平翻转概率
            **kwargs: 其他参数
        """
        super().__init__(dataset_name, **kwargs)
        self.augment = augment
        self.crop_padding = crop_padding
        self.flip_prob = flip_prob
        
        # 存储参数
        self._params = {
            "augment": augment,
            "crop_padding": crop_padding,
            "flip_prob": flip_prob,
            "mean": self.MEAN,
            "std": self.STD
        }
    
    @property
    def name(self) -> str:
        """预处理器名称"""
        return "cifar10_preprocessor"
    
    def fit(self, dataset: Dataset) -> "CIFAR10Preprocessor":
        """
        拟合预处理器
        
        对于CIFAR-10，使用预计算的统计量，无需拟合
        
        Args:
            dataset: 数据集（忽略）
            
        Returns:
            self
        """
        # CIFAR-10使用预计算的统计量，无需拟合
        return self
    
    def get_train_transform(self) -> Callable:
        """
        获取CIFAR-10训练变换
        
        包括：
        - 随机裁剪（padding=4）
        - 随机水平翻转
        - 转换为Tensor
        - 归一化
        
        Returns:
            训练变换函数
        """
        transform_list = []
        
        # 数据增强
        if self.augment:
            transform_list.append(
                transforms.RandomCrop(32, padding=self.crop_padding)
            )
            transform_list.append(
                transforms.RandomHorizontalFlip(p=self.flip_prob)
            )
        
        # 转换为Tensor并归一化
        transform_list.append(transforms.ToTensor())
        transform_list.append(
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        )
        
        return transforms.Compose(transform_list)
    
    def get_test_transform(self) -> Callable:
        """
        获取CIFAR-10测试变换
        
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
        CIFAR-10反归一化
        
        Args:
            data: 归一化后的数据
            
        Returns:
            反归一化数据
        """
        mean = torch.tensor(self.MEAN, device=data.device).view(-1, 1, 1)
        std = torch.tensor(self.STD, device=data.device).view(-1, 1, 1)
        return data * std + mean
    
    def save_params(self, path: str) -> None:
        """
        保存预处理参数
        
        Args:
            path: 保存路径
        """
        super().save_params(path)
    
    def load_params(self, path: str) -> "CIFAR10Preprocessor":
        """
        加载预处理参数
        
        Args:
            path: 参数文件路径
            
        Returns:
            self
        """
        super().load_params(path)
        return self
    
    def get_params(self) -> Dict[str, Any]:
        """
        获取预处理参数
        
        Returns:
            预处理参数字典
        """
        return self._params.copy()
    
    def set_params(self, params: Dict[str, Any]) -> "CIFAR10Preprocessor":
        """
        设置预处理参数
        
        Args:
            params: 预处理参数字典
            
        Returns:
            self
        """
        self._params.update(params)
        self.augment = params.get("augment", self.augment)
        self.crop_padding = params.get("crop_padding", self.crop_padding)
        self.flip_prob = params.get("flip_prob", self.flip_prob)
        return self
