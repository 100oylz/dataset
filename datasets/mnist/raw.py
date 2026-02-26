"""
MNIST原始数据集模块

实现MNIST原始数据集的加载
"""

from typing import Optional, Tuple, List
from pathlib import Path

import torch
from torch.utils.data import Dataset
from torchvision import datasets as tv_datasets

from core import RawDatasetBase


class MNISTRawDataset(RawDatasetBase):
    """
    MNIST原始数据集
    
    职责：
    1. 下载MNIST数据
    2. 加载原始训练集和测试集
    3. 提供MNIST的基本信息
    """
    
    # MNIST数据集常量
    NUM_CLASSES: int = 10
    NUM_FEATURES: int = 784  # 28 * 28
    INPUT_SHAPE: Tuple[int, int, int] = (1, 28, 28)
    TRAIN_SAMPLES: int = 60000
    TEST_SAMPLES: int = 10000
    
    CLASS_NAMES: List[str] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
    def __init__(self, data_root: str, download: bool = True, **kwargs) -> None:
        """
        初始化MNIST原始数据集
        
        Args:
            data_root: 数据根目录
            download: 是否自动下载
            **kwargs: 其他参数
        """
        super().__init__(data_root, "mnist", **kwargs)
        self._download = download
        self._train_dataset: Optional[Dataset] = None
        self._test_dataset: Optional[Dataset] = None
    
    @property
    def name(self) -> str:
        """数据集名称"""
        return "mnist"
    
    @property
    def num_classes(self) -> int:
        """类别数量"""
        return self.NUM_CLASSES
    
    @property
    def num_features(self) -> int:
        """特征维度"""
        return self.NUM_FEATURES
    
    @property
    def input_shape(self) -> Tuple[int, ...]:
        """输入数据形状"""
        return self.INPUT_SHAPE
    
    @property
    def train_samples(self) -> int:
        """训练样本数"""
        return self.TRAIN_SAMPLES
    
    @property
    def test_samples(self) -> int:
        """测试样本数"""
        return self.TEST_SAMPLES
    
    def download(self) -> None:
        """
        下载MNIST数据
        
        使用torchvision自动下载
        """
        # 通过加载训练集触发下载
        tv_datasets.MNIST(
            root=self._data_root,
            train=True,
            download=True
        )
        # 通过加载测试集触发下载
        tv_datasets.MNIST(
            root=self._data_root,
            train=False,
            download=True
        )
    
    def load_train_data(self) -> Dataset:
        """
        加载MNIST训练数据集
        
        Returns:
            原始MNIST训练数据集（未经预处理）
        """
        if self._train_dataset is None:
            self._train_dataset = tv_datasets.MNIST(
                root=self._data_root,
                train=True,
                download=self._download
            )
        return self._train_dataset
    
    def load_test_data(self) -> Dataset:
        """
        加载MNIST测试数据集
        
        Returns:
            原始MNIST测试数据集（未经预处理）
        """
        if self._test_dataset is None:
            self._test_dataset = tv_datasets.MNIST(
                root=self._data_root,
                train=False,
                download=self._download
            )
        return self._test_dataset
    
    def get_class_names(self) -> List[str]:
        """
        获取MNIST类别名称
        
        Returns:
            数字0-9的列表
        """
        return self.CLASS_NAMES
