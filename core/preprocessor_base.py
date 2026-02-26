"""
预处理基类模块

定义所有数据预处理器必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import torch
import numpy as np
from torch.utils.data import Dataset

try:
    from utils.helpers import save_json, load_json
except ImportError:
    # 相对导入回退
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.helpers import save_json, load_json


class PreprocessorBase(ABC):
    """
    数据预处理抽象基类
    
    职责：
    1. 对原始数据进行预处理（归一化、标准化、增强等）
    2. 提供训练集和测试集的变换逻辑
    3. 支持序列化和反序列化预处理参数
    
    注意：不包含数据下载或加载逻辑
    """
    
    def __init__(self, dataset_name: str, **kwargs) -> None:
        """
        初始化预处理器
        
        Args:
            dataset_name: 数据集名称
            **kwargs: 其他预处理特定参数
        """
        self.dataset_name = dataset_name
        self._params: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        预处理器名称
        
        Returns:
            预处理器的唯一标识名称
        """
        pass
    
    @abstractmethod
    def fit(self, dataset: Dataset) -> "PreprocessorBase":
        """
        根据数据拟合预处理参数
        
        例如：计算均值、标准差等统计量
        
        Args:
            dataset: 用于拟合的数据集
            
        Returns:
            self，支持链式调用
        """
        pass
    
    @abstractmethod
    def get_train_transform(self) -> Callable:
        """
        获取训练数据变换函数
        
        Returns:
            变换函数，输入原始数据，输出预处理后的数据
        """
        pass
    
    @abstractmethod
    def get_test_transform(self) -> Callable:
        """
        获取测试数据变换函数
        
        通常不包含数据增强
        
        Returns:
            变换函数，输入原始数据，输出预处理后的数据
        """
        pass
    
    def inverse_transform(self, data: Any) -> Any:
        """
        逆向变换（反归一化等）
        
        Args:
            data: 预处理后的数据
            
        Returns:
            原始尺度数据。默认实现返回原数据，子类可重写
        """
        return data
    
    def save_params(self, path: str) -> None:
        """
        保存预处理参数到文件
        
        Args:
            path: 保存路径
        """
        params = {
            "dataset_name": self.dataset_name,
            "preprocessor_name": self.name,
            "params": self.get_params()
        }
        save_json(params, path)
    
    def load_params(self, path: str) -> "PreprocessorBase":
        """
        从文件加载预处理参数
        
        Args:
            path: 参数文件路径
            
        Returns:
            self，支持链式调用
        """
        data = load_json(path)
        if "params" in data:
            self.set_params(data["params"])
        return self
    
    def get_params(self) -> Dict[str, Any]:
        """
        获取预处理参数字典
        
        Returns:
            包含所有预处理参数的字典。默认返回空字典，子类可重写
        """
        return self._params.copy()
    
    def set_params(self, params: Dict[str, Any]) -> "PreprocessorBase":
        """
        设置预处理参数
        
        Args:
            params: 预处理参数字典
            
        Returns:
            self，支持链式调用
        """
        self._params.update(params)
        return self


class ComposePreprocessor(PreprocessorBase):
    """
    组合预处理器
    
    将多个预处理器按顺序组合，依次应用各自的变换
    """
    
    def __init__(self, preprocessors: List[PreprocessorBase]) -> None:
        """
        初始化组合预处理器
        
        Args:
            preprocessors: 预处理器列表，按顺序应用
        """
        # 使用第一个预处理器的 dataset_name，如果没有则使用空字符串
        dataset_name = preprocessors[0].dataset_name if preprocessors else ""
        super().__init__(dataset_name)
        self.preprocessors: List[PreprocessorBase] = list(preprocessors)
    
    @property
    def name(self) -> str:
        """
        预处理器名称
        
        Returns:
            组合名称，格式为 "Compose[preprocessor1, preprocessor2, ...]"
        """
        names = [p.name for p in self.preprocessors]
        return f"Compose[{', '.join(names)}]"
    
    def fit(self, dataset: Dataset) -> "ComposePreprocessor":
        """
        依次拟合所有预处理器
        
        每个预处理器按顺序对数据集进行拟合
        
        Args:
            dataset: 用于拟合的数据集
            
        Returns:
            self，支持链式调用
        """
        for preprocessor in self.preprocessors:
            preprocessor.fit(dataset)
        return self
    
    def get_train_transform(self) -> Callable:
        """
        获取组合的训练变换函数
        
        依次应用所有预处理器的训练变换
        
        Returns:
            组合的训练变换函数
        """
        transforms = [p.get_train_transform() for p in self.preprocessors]
        
        def composed_transform(data: Any) -> Any:
            for transform in transforms:
                data = transform(data)
            return data
        
        return composed_transform
    
    def get_test_transform(self) -> Callable:
        """
        获取组合的测试变换函数
        
        依次应用所有预处理器的测试变换
        
        Returns:
            组合的测试变换函数
        """
        transforms = [p.get_test_transform() for p in self.preprocessors]
        
        def composed_transform(data: Any) -> Any:
            for transform in transforms:
                data = transform(data)
            return data
        
        return composed_transform
