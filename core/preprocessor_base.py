"""
预处理基类模块

定义所有数据预处理器必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import torch
import numpy as np
from torch.utils.data import Dataset


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
        # TODO: 初始化预处理参数
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """预处理器名称"""
        # TODO: 返回预处理器名称
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
        # TODO: 实现拟合逻辑
        pass
    
    @abstractmethod
    def get_train_transform(self) -> Callable:
        """
        获取训练数据变换函数
        
        Returns:
            变换函数，输入原始数据，输出预处理后的数据
        """
        # TODO: 返回训练变换函数
        pass
    
    @abstractmethod
    def get_test_transform(self) -> Callable:
        """
        获取测试数据变换函数
        
        通常不包含数据增强
        
        Returns:
            变换函数，输入原始数据，输出预处理后的数据
        """
        # TODO: 返回测试变换函数
        pass
    
    def inverse_transform(self, data: Any) -> Any:
        """
        逆向变换（反归一化等）
        
        Args:
            data: 预处理后的数据
            
        Returns:
            原始尺度数据
        """
        # TODO: 实现逆变换（可选）
        pass
    
    def save_params(self, path: str) -> None:
        """
        保存预处理参数到文件
        
        Args:
            path: 保存路径
        """
        # TODO: 保存预处理参数
        pass
    
    def load_params(self, path: str) -> "PreprocessorBase":
        """
        从文件加载预处理参数
        
        Args:
            path: 参数文件路径
            
        Returns:
            self，支持链式调用
        """
        # TODO: 加载预处理参数
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """
        获取预处理参数字典
        
        Returns:
            包含所有预处理参数的字典
        """
        # TODO: 返回预处理参数
        return {}
    
    def set_params(self, params: Dict[str, Any]) -> "PreprocessorBase":
        """
        设置预处理参数
        
        Args:
            params: 预处理参数字典
            
        Returns:
            self，支持链式调用
        """
        # TODO: 设置预处理参数
        pass


class ComposePreprocessor(PreprocessorBase):
    """
    组合预处理器
    
    将多个预处理器按顺序组合
    """
    
    def __init__(self, preprocessors: List[PreprocessorBase]) -> None:
        """
        初始化组合预处理器
        
        Args:
            preprocessors: 预处理器列表
        """
        # TODO: 初始化组合预处理器
        pass
    
    @property
    def name(self) -> str:
        """预处理器名称"""
        # TODO: 返回组合名称
        pass
    
    def fit(self, dataset: Dataset) -> "PreprocessorBase":
        """依次拟合所有预处理器"""
        # TODO: 实现依次拟合
        pass
    
    def get_train_transform(self) -> Callable:
        """获取组合的训练变换"""
        # TODO: 返回组合训练变换
        pass
    
    def get_test_transform(self) -> Callable:
        """获取组合的测试变换"""
        # TODO: 返回组合测试变换
        pass
