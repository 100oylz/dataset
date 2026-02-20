"""
Fashion-MNIST原始数据集模块

实现Fashion-MNIST原始数据集的加载
"""

from typing import Optional, Tuple, List
from pathlib import Path

import torch
from torch.utils.data import Dataset
from torchvision import datasets as tv_datasets

from core import RawDatasetBase


class FashionMNISTRawDataset(RawDatasetBase):
    """
    Fashion-MNIST原始数据集
    
    职责：
    1. 下载Fashion-MNIST数据
    2. 加载原始训练集和测试集
    3. 提供Fashion-MNIST的基本信息
    """
    
    # Fashion-MNIST数据集常量
    NUM_CLASSES: int = 10
    NUM_FEATURES: int = 784  # 28 * 28
    INPUT_SHAPE: Tuple[int, int, int] = (1, 28, 28)
    TRAIN_SAMPLES: int = 60000
    TEST_SAMPLES: int = 10000
    
    CLASS_NAMES: List[str] = [
        'T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
        'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot'
    ]
    
    def __init__(self, data_root: str, download: bool = True, **kwargs) -> None:
        """
        初始化Fashion-MNIST原始数据集
        
        Args:
            data_root: 数据根目录
            download: 是否自动下载
            **kwargs: 其他参数
        """
        # TODO: 初始化Fashion-MNIST原始数据集
        pass
    
    @property
    def name(self) -> str:
        """数据集名称"""
        # TODO: 返回"fashion_mnist"
        pass
    
    @property
    def num_classes(self) -> int:
        """类别数量"""
        # TODO: 返回10
        pass
    
    @property
    def num_features(self) -> int:
        """特征维度"""
        # TODO: 返回784
        pass
    
    @property
    def input_shape(self) -> Tuple[int, ...]:
        """输入数据形状"""
        # TODO: 返回(1, 28, 28)
        pass
    
    @property
    def train_samples(self) -> int:
        """训练样本数"""
        # TODO: 返回60000
        pass
    
    @property
    def test_samples(self) -> int:
        """测试样本数"""
        # TODO: 返回10000
        pass
    
    def download(self) -> None:
        """
        下载Fashion-MNIST数据
        
        使用torchvision自动下载
        """
        # TODO: 实现Fashion-MNIST下载逻辑
        pass
    
    def load_train_data(self) -> Dataset:
        """
        加载Fashion-MNIST训练数据集
        
        Returns:
            原始Fashion-MNIST训练数据集（未经预处理）
        """
        # TODO: 实现加载Fashion-MNIST训练集逻辑
        pass
    
    def load_test_data(self) -> Dataset:
        """
        加载Fashion-MNIST测试数据集
        
        Returns:
            原始Fashion-MNIST测试数据集（未经预处理）
        """
        # TODO: 实现加载Fashion-MNIST测试集逻辑
        pass
    
    def get_class_names(self) -> List[str]:
        """
        获取Fashion-MNIST类别名称
        
        Returns:
            类别名称列表
        """
        # TODO: 返回CLASS_NAMES
        pass
