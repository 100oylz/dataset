"""
FEMNIST原始数据集模块

FEMNIST (Federated Extended MNIST) 是 MNIST 的扩展版本，包含：
- 10 个数字 (0-9)
- 26 个小写字母 (a-z)
- 26 个大写字母 (A-Z)

共 62 个类别，图像为 28x28 灰度图
"""

from typing import Optional, Tuple, List
from pathlib import Path

import torch
from torch.utils.data import Dataset
from torchvision import datasets as tv_datasets

from core import RawDatasetBase


class FEMNISTRawDataset(RawDatasetBase):
    """
    FEMNIST原始数据集
    
    职责：
    1. 下载FEMNIST数据（使用EMNIST作为数据源）
    2. 加载原始训练集和测试集
    3. 提供FEMNIST的基本信息
    
    FEMNIST数据集常量：
    - 62个类别：10数字 + 26小写字母 + 26大写字母
    - 图像尺寸：28x28 灰度图
    """
    
    # FEMNIST数据集常量
    NUM_CLASSES: int = 62
    NUM_FEATURES: int = 784  # 28 * 28
    INPUT_SHAPE: Tuple[int, int, int] = (1, 28, 28)
    TRAIN_SAMPLES: int = 697932  # EMNIST ByClass 训练集
    TEST_SAMPLES: int = 116323   # EMNIST ByClass 测试集
    
    CLASS_NAMES: List[str] = [
        # 数字 0-9
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        # 大写字母 A-Z
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z',
        # 小写字母 a-z
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
        'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
        'u', 'v', 'w', 'x', 'y', 'z'
    ]
    
    def __init__(self, data_root: str, download: bool = True, **kwargs) -> None:
        """
        初始化FEMNIST原始数据集
        
        Args:
            data_root: 数据根目录
            download: 是否自动下载
            **kwargs: 其他参数
        """
        super().__init__(data_root, "femnist", **kwargs)
        self._download = download
        self._train_dataset: Optional[Dataset] = None
        self._test_dataset: Optional[Dataset] = None
    
    @property
    def name(self) -> str:
        """数据集名称"""
        return "femnist"
    
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
        下载FEMNIST数据
        
        FEMNIST基于EMNIST数据集，使用 'byclass' 分割
        """
        # EMNIST 'byclass' 包含所有 62 个类别
        tv_datasets.EMNIST(
            root=self._data_root,
            split='byclass',
            train=True,
            download=True
        )
        tv_datasets.EMNIST(
            root=self._data_root,
            split='byclass',
            train=False,
            download=True
        )
    
    def load_train_data(self) -> Dataset:
        """
        加载FEMNIST训练数据集
        
        Returns:
            原始FEMNIST训练数据集（未经预处理）
        """
        if self._train_dataset is None:
            self._train_dataset = tv_datasets.EMNIST(
                root=self._data_root,
                split='byclass',
                train=True,
                download=self._download
            )
        return self._train_dataset
    
    def load_test_data(self) -> Dataset:
        """
        加载FEMNIST测试数据集
        
        Returns:
            原始FEMNIST测试数据集（未经预处理）
        """
        if self._test_dataset is None:
            self._test_dataset = tv_datasets.EMNIST(
                root=self._data_root,
                split='byclass',
                train=False,
                download=self._download
            )
        return self._test_dataset
    
    def get_class_names(self) -> List[str]:
        """
        获取FEMNIST类别名称
        
        Returns:
            62个类别的名称列表
        """
        return self.CLASS_NAMES
