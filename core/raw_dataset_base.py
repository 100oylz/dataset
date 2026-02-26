"""
原始数据集基类模块

定义所有原始数据集必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import torch
from torch.utils.data import Dataset

class RawDatasetBase(ABC):
    """
    原始数据集抽象基类
    
    职责：
    1. 下载和加载原始数据
    2. 提供数据的基本信息（样本数、类别数、特征维度等）
    3. 返回标准格式的训练集和测试集
    
    注意：不包含任何预处理逻辑
    """
    
    def __init__(self, data_root: str, dataset_name: str, **kwargs) -> None:
        """
        初始化原始数据集
        
        Args:
            data_root: 数据根目录
            dataset_name: 数据集名称
            **kwargs: 其他数据集特定参数
        """
        self._data_root = Path(data_root)
        self._dataset_name = dataset_name
        self._kwargs = kwargs
        
        # 确保数据目录存在
        self._ensure_data_dir()
    
    @property
    def data_root(self) -> Path:
        """数据根目录"""
        return self._data_root
    
    @property
    def dataset_name(self) -> str:
        """数据集名称"""
        return self._dataset_name
    
    @property
    def name(self) -> str:
        """数据集名称（子类实现）"""
        return self._dataset_name

    
    @property
    @abstractmethod
    def num_classes(self) -> int:
        """类别数量（子类实现）"""
        pass
    
    @property
    @abstractmethod
    def num_features(self) -> int:
        """特征维度（子类实现）"""
        pass
    
    @property
    @abstractmethod
    def input_shape(self) -> Tuple[int, ...]:
        """输入数据形状，如 (3, 32, 32) 或 (784,)（子类实现）"""
        pass
    
    @property
    @abstractmethod
    def train_samples(self) -> int:
        """训练样本数（子类实现）"""
        pass
    
    @property
    @abstractmethod
    def test_samples(self) -> int:
        """测试样本数（子类实现）"""
        pass
    
    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        self._data_root.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def download(self) -> None:
        """
        下载原始数据
        
        如果数据已存在则跳过
        """
        pass
    
    @abstractmethod
    def load_train_data(self) -> Dataset:
        """
        加载训练数据集
        
        Returns:
            原始训练数据集（未经预处理）
        """
        # TODO: 返回训练数据集
        pass
    
    @abstractmethod
    def load_test_data(self) -> Dataset:
        """
        加载测试数据集
        
        Returns:
            原始测试数据集（未经预处理）
        """
        # TODO: 返回测试数据集
        pass
    
    def get_class_names(self) -> Optional[List[str]]:
        """
        获取类别名称列表
        
        Returns:
            类别名称列表，如果不适用则返回None
        """
        # TODO: 返回类别名称列表（可选实现）
        return None
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        获取数据集完整信息
        
        Returns:
            包含数据集元信息的字典
        """
        info = {
            "name": self.name,
            "num_classes": self.num_classes,
            "num_features": self.num_features,
            "input_shape": self.input_shape,
            "train_samples": self.train_samples,
            "test_samples": self.test_samples,
        }
        
        # 添加类别名称（如果可用）
        class_names = self.get_class_names()
        if class_names is not None:
            info["class_names"] = class_names
        
        return info
