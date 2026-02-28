"""
数据集管理器基类模块

定义数据集管理器的高层接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset, Subset

from core.raw_dataset_base import RawDatasetBase
from core.preprocessor_base import PreprocessorBase
from core.partitioner_base import PartitionerBase
from utils.helpers import set_seed, save_json, load_json


class DatasetManagerBase(ABC):
    """
    数据集管理器抽象基类
    
    职责：
    1. 协调原始数据集、预处理器和划分器
    2. 提供统一的数据访问接口
    3. 管理数据的生命周期（下载->预处理->划分）
    
    每个具体数据集应有自己的管理器实现，通过指定以下类属性：
    - dataset_name: 数据集名称
    - raw_dataset_class: 原始数据集类
    - preprocessor_class: 预处理器类
    - partitioner_class: 划分器类
    """
    
    def __init__(
        self,
        data_root: str,
        num_clients: int,
        partition_strategy: str,
        partition_params: Optional[Dict[str, Any]] = None,
        seed: int = 42,
        **kwargs
    ) -> None:
        """
        初始化数据集管理器
        
        Args:
            data_root: 数据根目录
            num_clients: 客户端数量
            partition_strategy: 划分策略（"iid", "dirichlet", "pathological"）
            partition_params: 划分策略参数
            seed: 随机种子
            **kwargs: 其他参数
        """
        self._data_root = data_root
        self._num_clients = num_clients
        self._partition_strategy = partition_strategy
        self._partition_params = partition_params or {}
        self._seed = seed
        self._kwargs = kwargs
        
        # 设置随机种子
        set_seed(seed)
        
        # 懒加载标记
        self._is_prepared = False
    
    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """
        数据集名称
        
        Returns:
            数据集名称字符串
        """
        pass
    
    @property
    @abstractmethod
    def raw_dataset_class(self) -> Type[RawDatasetBase]:
        """
        原始数据集类
        
        Returns:
            RawDatasetBase 的子类
        """
        pass
    
    @property
    @abstractmethod
    def preprocessor_class(self) -> Type[PreprocessorBase]:
        """
        预处理器类
        
        Returns:
            PreprocessorBase 的子类
        """
        pass
    
    @property
    @abstractmethod
    def partitioner_class(self) -> Type[PartitionerBase]:
        """
        划分器类
        
        Returns:
            PartitionerBase 的子类
        """
        pass
    
    def prepare_data(self, force_download: bool = False, force_preprocess: bool = False) -> None:
        """
        准备数据（下载->预处理->划分）
        
        使用懒加载模式：第一次调用时才真正准备数据
        
        Args:
            force_download: 是否强制重新下载
            force_preprocess: 是否强制重新预处理
        """
        # 子类实现具体的数据准备流程
        pass
    
    @abstractmethod
    def get_client_loader(
        self, 
        client_id: int, 
        batch_size: int = 32,
        shuffle: bool = True,
        **kwargs
    ) -> DataLoader:
        """
        获取客户端数据加载器
        
        Args:
            client_id: 客户端ID
            batch_size: 批次大小
            shuffle: 是否打乱
            **kwargs: 其他DataLoader参数
            
        Returns:
            DataLoader实例
        """
        pass
    
    @abstractmethod
    def get_test_loader(
        self,
        batch_size: int = 256,
        **kwargs
    ) -> DataLoader:
        """
        获取测试数据加载器
        
        Args:
            batch_size: 批次大小
            **kwargs: 其他DataLoader参数
            
        Returns:
            DataLoader实例
        """
        pass
    
    @abstractmethod
    def get_client_dataset(self, client_id: int) -> Dataset:
        """
        获取客户端数据集
        
        Args:
            client_id: 客户端ID
            
        Returns:
            预处理后的客户端数据集
        """
        pass
    
    @abstractmethod
    def get_test_dataset(self) -> Dataset:
        """
        获取测试数据集
        
        Returns:
            预处理后的测试数据集
        """
        pass
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        获取数据信息
        
        Returns:
            包含数据基本信息的字典
        """
        info = {
            "dataset_name": self.dataset_name,
            "num_clients": self._num_clients,
            "partition_strategy": self._partition_strategy,
            "partition_params": self._partition_params,
            "seed": self._seed,
        }
        return info
    
    def get_partition_info(self) -> Dict[str, Any]:
        """
        获取划分信息
        
        Returns:
            包含划分统计信息的字典
        """
        # 子类应重写此方法以提供详细的划分信息
        return {
            "num_clients": self._num_clients,
            "partition_strategy": self._partition_strategy,
        }
    
    def save_split(self, path: Optional[str] = None) -> None:
        """
        保存划分结果
        
        Args:
            path: 保存路径，默认为 {data_root}/{dataset_name}_split.json
        """
        if path is None:
            path = Path(self._data_root) / f"{self.dataset_name}_split.json"
        
        # 子类应重写此方法以保存实际的划分结果
        save_json({}, path)
    
    def load_split(self, path: Optional[str] = None) -> None:
        """
        加载划分结果
        
        Args:
            path: 划分结果路径，默认为 {data_root}/{dataset_name}_split.json
        """
        if path is None:
            path = Path(self._data_root) / f"{self.dataset_name}_split.json"
        
        # 子类应重写此方法以加载实际的划分结果
        load_json(path)


class FederatedDatasetManager(DatasetManagerBase):
    """
    联邦学习数据集管理器基类
    
    提供联邦学习场景下的数据管理功能，实现所有抽象方法。
    子类只需指定 dataset_name, raw_dataset_class, preprocessor_class, partitioner_class。
    
    内部维护：
    - _raw_dataset: 原始数据集实例
    - _preprocessor: 预处理器实例
    - _partitioner: 划分器实例
    - _train_dataset: 预处理后的训练数据集
    - _test_dataset: 预处理后的测试数据集
    - _client_indices: 划分结果 {client_id: [indices]}
    """
    
    def __init__(
        self,
        data_root: str,
        num_clients: int,
        partition_strategy: str,
        partition_params: Optional[Dict[str, Any]] = None,
        seed: int = 42,
        **kwargs
    ) -> None:
        """
        初始化联邦学习数据集管理器
        
        Args:
            data_root: 数据根目录
            num_clients: 客户端数量
            partition_strategy: 划分策略
            partition_params: 划分策略参数
            seed: 随机种子
            **kwargs: 其他参数（传递给各组件）
        """
        super().__init__(
            data_root=data_root,
            num_clients=num_clients,
            partition_strategy=partition_strategy,
            partition_params=partition_params,
            seed=seed,
            **kwargs
        )
        
        # 内部实例（懒加载）
        self._raw_dataset: Optional[RawDatasetBase] = None
        self._preprocessor: Optional[PreprocessorBase] = None
        self._partitioner: Optional[PartitionerBase] = None
        
        # 数据集（预处理后）
        self._train_dataset: Optional[Dataset] = None
        self._test_dataset: Optional[Dataset] = None
        
        # 划分结果
        self._client_indices: Optional[Dict[int, List[int]]] = None
    
    @property
    @abstractmethod
    def dataset_name(self) -> str:
        """数据集名称（子类必须实现）"""
        pass
    
    @property
    @abstractmethod
    def raw_dataset_class(self) -> Type[RawDatasetBase]:
        """原始数据集类（子类必须实现）"""
        pass
    
    @property
    @abstractmethod
    def preprocessor_class(self) -> Type[PreprocessorBase]:
        """预处理器类（子类必须实现）"""
        pass
    
    @property
    @abstractmethod
    def partitioner_class(self) -> Type[PartitionerBase]:
        """划分器类（子类必须实现）"""
        pass
    
    def _ensure_prepared(self) -> None:
        """
        确保数据已准备好
        
        如果数据未准备，自动调用 prepare_data()
        """
        if not self._is_prepared:
            self.prepare_data()
    
    def prepare_data(self, force_download: bool = False, force_preprocess: bool = False) -> None:
        """
        准备数据流程：下载 -> 预处理 -> 划分
        
        Args:
            force_download: 是否强制重新下载
            force_preprocess: 是否强制重新预处理
        """
        if self._is_prepared and not force_download and not force_preprocess:
            return
        
        # 1. 创建并下载原始数据集
        self._raw_dataset = self.raw_dataset_class(
            data_root=self._data_root,
            **self._kwargs
        )
        
        if force_download or not self._is_prepared:
            self._raw_dataset.download()
        
        # 2. 加载原始数据
        raw_train_data = self._raw_dataset.load_train_data()
        raw_test_data = self._raw_dataset.load_test_data()

        # 3. 创建并拟合预处理器
        self._preprocessor = self.preprocessor_class(
            dataset_name=self.dataset_name,
            **self._kwargs
        )
        
        if force_preprocess or not self._is_prepared:
            self._preprocessor.fit(raw_train_data)
        
        # 4. 应用预处理变换
        # 这里假设原始数据集支持通过 preprocessor 进行变换
        # 实际实现可能需要根据具体情况调整
        self._train_dataset = self._apply_transform(raw_train_data, self._preprocessor.get_train_transform())
        self._test_dataset = self._apply_transform(raw_test_data, self._preprocessor.get_test_transform())

        # 5. 创建划分器并执行划分
        # 支持工厂类模式（如果有create方法）或直接实例化
        if hasattr(self.partitioner_class, 'create'):
            # 工厂类模式
            self._partitioner = self.partitioner_class.create(
                strategy=self._partition_strategy,
                num_clients=self._num_clients,
                seed=self._seed,
                **self._partition_params
            )
        else:
            # 直接实例化模式
            self._partitioner = self.partitioner_class(
                num_clients=self._num_clients,
                seed=self._seed,
                **self._partition_params
            )
        
        self._client_indices = self._partitioner.partition(self._train_dataset)
        
        self._is_prepared = True
    
    def _apply_transform(self, dataset: Dataset, transform: Any) -> Dataset:
        """
        应用变换到数据集
        
        Args:
            dataset: 原始数据集
            transform: 变换函数
            
        Returns:
            变换后的数据集
        """
        # 如果数据集本身支持设置变换，直接使用
        if hasattr(dataset, 'transform'):
            dataset.transform = transform
            return dataset
        
        # 否则，创建一个包装数据集
        # 这里返回原始数据集，实际使用时在 DataLoader 中应用变换
        return dataset
    
    def get_client_loader(
        self, 
        client_id: int, 
        batch_size: int = 32,
        shuffle: bool = True,
        **kwargs
    ) -> DataLoader:
        """
        获取客户端数据加载器
        
        Args:
            client_id: 客户端ID
            batch_size: 批次大小
            shuffle: 是否打乱
            **kwargs: 其他DataLoader参数
            
        Returns:
            DataLoader实例
            
        Raises:
            ValueError: 如果 client_id 无效
        """
        self._ensure_prepared()
        
        if client_id < 0 or client_id >= self._num_clients:
            raise ValueError(f"Invalid client_id: {client_id}, must be in [0, {self._num_clients})")
        
        client_dataset = self.get_client_dataset(client_id)
        
        # 合并默认参数和传入的参数
        loader_kwargs = {
            'batch_size': batch_size,
            'shuffle': shuffle,
        }
        loader_kwargs.update(kwargs)
        
        return DataLoader(client_dataset, **loader_kwargs)
    
    def get_test_loader(self, batch_size: int = 256, **kwargs) -> DataLoader:
        """
        获取测试数据加载器
        
        Args:
            batch_size: 批次大小
            **kwargs: 其他DataLoader参数
            
        Returns:
            DataLoader实例
        """
        self._ensure_prepared()
        
        test_dataset = self.get_test_dataset()
        
        # 合并默认参数和传入的参数
        loader_kwargs = {
            'batch_size': batch_size,
            'shuffle': False,
        }
        loader_kwargs.update(kwargs)
        
        return DataLoader(test_dataset, **loader_kwargs)
    
    def get_client_dataset(self, client_id: int) -> Dataset:
        """
        获取客户端数据集
        
        Args:
            client_id: 客户端ID
            
        Returns:
            预处理后的客户端数据子集
            
        Raises:
            ValueError: 如果 client_id 无效
        """
        self._ensure_prepared()
        
        if client_id < 0 or client_id >= self._num_clients:
            raise ValueError(f"Invalid client_id: {client_id}, must be in [0, {self._num_clients})")
        
        if self._client_indices is None or self._train_dataset is None:
            raise RuntimeError("Data not prepared properly")
        
        # 使用划分器的 get_client_dataset 方法
        return self._partitioner.get_client_dataset(
            self._train_dataset, 
            client_id, 
            self._client_indices
        )
    
    def get_test_dataset(self) -> Dataset:
        """
        获取测试数据集
        
        Returns:
            预处理后的测试数据集
        """
        self._ensure_prepared()
        
        if self._test_dataset is None:
            raise RuntimeError("Data not prepared properly")
        
        return self._test_dataset
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        获取数据信息
        
        Returns:
            包含数据基本信息的字典
        """
        self._ensure_prepared()
        
        info = super().get_data_info()
        
        if self._raw_dataset is not None:
            info.update({
                "num_classes": self._raw_dataset.num_classes,
                "num_features": self._raw_dataset.num_features,
                "input_shape": self._raw_dataset.input_shape,
                "train_samples": self._raw_dataset.train_samples,
                "test_samples": self._raw_dataset.test_samples,
            })
            
            # 添加类别名称（如果可用）
            class_names = self._raw_dataset.get_class_names()
            if class_names is not None:
                info["class_names"] = class_names
        
        return info
    
    def get_partition_info(self) -> Dict[str, Any]:
        """
        获取划分信息
        
        Returns:
            包含划分统计信息的字典
        """
        self._ensure_prepared()
        
        if self._partitioner is None or self._client_indices is None:
            raise RuntimeError("Data not prepared properly")
        
        info = {
            "num_clients": self._num_clients,
            "partition_strategy": self._partition_strategy,
            "partition_params": self._partition_params,
            "partitioner_name": self._partitioner.name,
            "strategy_type": self._partitioner.strategy_type,
        }
        
        # 添加统计信息
        if self._train_dataset is not None:
            stats = self._partitioner.get_statistics(self._train_dataset, self._client_indices)
            info["statistics"] = stats
        
        return info
    
    def save_split(self, path: Optional[str] = None) -> None:
        """
        保存划分结果
        
        Args:
            path: 保存路径，默认为 {data_root}/{dataset_name}_split.json
        """
        self._ensure_prepared()
        
        if path is None:
            path = Path(self._data_root) / f"{self.dataset_name}_split.json"
        
        if self._partitioner is None or self._client_indices is None:
            raise RuntimeError("No split to save")
        
        self._partitioner.save_partition(self._client_indices, str(path))
    
    def load_split(self, path: Optional[str] = None) -> None:
        """
        加载划分结果
        
        加载后会重新设置 _client_indices，但不会改变 _is_prepared 状态
        
        Args:
            path: 划分结果路径，默认为 {data_root}/{dataset_name}_split.json
        """
        if path is None:
            path = Path(self._data_root) / f"{self.dataset_name}_split.json"
        
        # 确保划分器已创建
        if self._partitioner is None:
            self._partitioner = self.partitioner_class(
                num_clients=self._num_clients,
                seed=self._seed,
                **self._partition_params
            )
        
        self._client_indices = self._partitioner.load_partition(str(path))
        
        # 验证客户端数量
        if len(self._client_indices) != self._num_clients:
            raise ValueError(
                f"Loaded split has {len(self._client_indices)} clients, "
                f"but expected {self._num_clients}"
            )
