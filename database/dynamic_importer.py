"""
动态导入模块

提供从模块路径动态导入类的功能
支持数据集组件的动态加载
"""

import importlib
import logging
import sys
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from core import (
    RawDatasetBase,
    PreprocessorBase,
    PartitionerBase,
    DatasetManagerBase,
)
from .models import DatasetRegistration

logger = logging.getLogger(__name__)
T = TypeVar("T")


class DynamicImporter:
    """
    动态导入器
    
    根据模块路径和类名动态导入类
    提供缓存机制避免重复导入
    """
    
    _cache: Dict[str, Type[Any]] = {}
    _instance_cache: Dict[str, Any] = {}
    
    def __init__(self):
        """初始化动态导入器"""
        pass
    
    @classmethod
    def _get_cache_key(cls, module_path: str, class_name: str) -> str:
        """生成缓存键"""
        return f"{module_path}.{class_name}"
    
    @classmethod
    def import_class(cls, module_path: str, class_name: str) -> Type[Any]:
        """
        动态导入类
        
        Args:
            module_path: 模块路径，如 "datasets.mnist.raw"
            class_name: 类名，如 "MNISTRawDataset"
            
        Returns:
            导入的类
            
        Raises:
            ImportError: 导入失败
            AttributeError: 类不存在
        """
        cache_key = cls._get_cache_key(module_path, class_name)
        
        # 检查缓存
        if cache_key in cls._cache:
            logger.debug(f"从缓存获取类: {cache_key}")
            return cls._cache[cache_key]
        
        try:
            # 导入模块
            if module_path not in sys.modules:
                module = importlib.import_module(module_path)
                logger.debug(f"导入模块: {module_path}")
            else:
                module = sys.modules[module_path]
            
            # 获取类
            if not hasattr(module, class_name):
                raise AttributeError(
                    f"模块 '{module_path}' 中没有类 '{class_name}'"
                )
            
            class_obj = getattr(module, class_name)
            
            # 缓存类
            cls._cache[cache_key] = class_obj
            logger.info(f"成功导入类: {cache_key}")
            
            return class_obj
            
        except ImportError as e:
            logger.error(f"导入模块失败 '{module_path}': {e}")
            raise
        except AttributeError as e:
            logger.error(f"获取类失败 '{class_name}': {e}")
            raise
    
    @classmethod
    def import_dataset_components(
        cls,
        registration: DatasetRegistration
    ) -> Dict[str, Type[Any]]:
        """
        导入数据集的所有组件类
        
        Args:
            registration: 数据集注册信息
            
        Returns:
            {
                "raw_dataset": 原始数据集类,
                "preprocessor": 预处理器类,
                "partitioner": 划分器类,
                "manager": 管理器类,
            }
            
        Raises:
            ImportError: 导入失败
        """
        components = {}
        
        # 导入原始数据集类
        if registration.raw_dataset_module and registration.raw_dataset_class:
            components["raw_dataset"] = cls.import_class(
                registration.raw_dataset_module,
                registration.raw_dataset_class
            )
        
        # 导入预处理器类
        if registration.preprocessor_module and registration.preprocessor_class:
            components["preprocessor"] = cls.import_class(
                registration.preprocessor_module,
                registration.preprocessor_class
            )
        
        # 导入划分器类
        if registration.partitioner_module and registration.partitioner_class:
            components["partitioner"] = cls.import_class(
                registration.partitioner_module,
                registration.partitioner_class
            )
        
        # 导入管理器类（可选）
        if registration.manager_module and registration.manager_class:
            try:
                components["manager"] = cls.import_class(
                    registration.manager_module,
                    registration.manager_class
                )
            except (ImportError, AttributeError):
                logger.warning(f"管理器类导入失败（可选）: {registration.manager_module}.{registration.manager_class}")
        
        return components
    
    @classmethod
    def create_instance(
        cls,
        module_path: str,
        class_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        动态创建类实例
        
        Args:
            module_path: 模块路径
            class_name: 类名
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            类实例
            
        Raises:
            ImportError: 导入失败
            TypeError: 实例化失败
        """
        class_obj = cls.import_class(module_path, class_name)
        
        try:
            instance = class_obj(*args, **kwargs)
            logger.debug(f"创建实例: {class_name}")
            return instance
        except Exception as e:
            logger.error(f"创建实例失败 '{class_name}': {e}")
            raise TypeError(f"无法实例化 '{class_name}': {e}")
    
    @classmethod
    def create_raw_dataset(
        cls,
        registration: DatasetRegistration,
        data_root: str,
        **kwargs
    ) -> RawDatasetBase:
        """
        创建原始数据集实例
        
        Args:
            registration: 数据集注册信息
            data_root: 数据根目录
            **kwargs: 其他参数
            
        Returns:
            原始数据集实例
        """
        dataset_class = cls.import_class(
            registration.raw_dataset_module,
            registration.raw_dataset_class
        )
        
        instance = dataset_class(data_root=data_root, **kwargs)
        
        if not isinstance(instance, RawDatasetBase):
            raise TypeError(
                f"'{registration.raw_dataset_class}' 不是 RawDatasetBase 的子类"
            )
        
        return instance
    
    @classmethod
    def create_preprocessor(
        cls,
        registration: DatasetRegistration,
        **kwargs
    ) -> PreprocessorBase:
        """
        创建预处理器实例
        
        Args:
            registration: 数据集注册信息
            **kwargs: 其他参数
            
        Returns:
            预处理器实例
        """
        preprocessor_class = cls.import_class(
            registration.preprocessor_module,
            registration.preprocessor_class
        )
        
        # 自动设置 dataset_name
        if 'dataset_name' not in kwargs:
            kwargs['dataset_name'] = registration.name
        
        instance = preprocessor_class(**kwargs)
        
        if not isinstance(instance, PreprocessorBase):
            raise TypeError(
                f"'{registration.preprocessor_class}' 不是 PreprocessorBase 的子类"
            )
        
        return instance
    
    @classmethod
    def create_partitioner(
        cls,
        registration: DatasetRegistration,
        num_clients: int,
        strategy: str = "iid",
        **kwargs
    ) -> PartitionerBase:
        """
        创建划分器实例
        
        Args:
            registration: 数据集注册信息
            num_clients: 客户端数量
            strategy: 划分策略
            **kwargs: 其他参数
            
        Returns:
            划分器实例
        """
        partitioner_class = cls.import_class(
            registration.partitioner_module,
            registration.partitioner_class
        )
        
        # 检查是否是工厂类
        if hasattr(partitioner_class, 'create'):
            # 使用工厂方法创建
            instance = partitioner_class.create(
                strategy=strategy,
                num_clients=num_clients,
                **kwargs
            )
        else:
            # 直接实例化
            instance = partitioner_class(
                num_clients=num_clients,
                **kwargs
            )
        
        if not isinstance(instance, PartitionerBase):
            raise TypeError(
                f"'{registration.partitioner_class}' 不是 PartitionerBase 的子类"
            )
        
        return instance
    
    @classmethod
    def create_manager(
        cls,
        registration: DatasetRegistration,
        data_root: str,
        num_clients: int,
        partition_strategy: str = "iid",
        partition_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DatasetManagerBase:
        """
        创建数据集管理器实例
        
        动态构建 FederatedDatasetManager 的子类
        
        Args:
            registration: 数据集注册信息
            data_root: 数据根目录
            num_clients: 客户端数量
            partition_strategy: 划分策略
            partition_params: 划分策略参数
            **kwargs: 其他参数
            
        Returns:
            数据集管理器实例
        """
        from core import FederatedDatasetManager
        
        # 导入组件类
        raw_dataset_class = cls.import_class(
            registration.raw_dataset_module,
            registration.raw_dataset_class
        )
        preprocessor_class = cls.import_class(
            registration.preprocessor_module,
            registration.preprocessor_class
        )
        partitioner_class = cls.import_class(
            registration.partitioner_module,
            registration.partitioner_class
        )
        
        # 动态创建管理器类
        class DynamicDatasetManager(FederatedDatasetManager):
            @property
            def dataset_name(self) -> str:
                return registration.name
            
            @property
            def raw_dataset_class(self):
                return raw_dataset_class
            
            @property
            def preprocessor_class(self):
                return preprocessor_class
            
            @property
            def partitioner_class(self):
                return partitioner_class
        
        # 设置类名
        DynamicDatasetManager.__name__ = f"{registration.name.title()}DatasetManager"
        
        # 创建实例
        if partition_params is None:
            partition_params = {}
        
        instance = DynamicDatasetManager(
            data_root=data_root,
            num_clients=num_clients,
            partition_strategy=partition_strategy,
            partition_params=partition_params,
            **kwargs
        )
        
        return instance
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除导入缓存"""
        cls._cache.clear()
        cls._instance_cache.clear()
        logger.info("动态导入缓存已清除")
    
    @classmethod
    def get_cache_info(cls) -> Dict[str, int]:
        """
        获取缓存信息
        
        Returns:
            缓存统计信息
        """
        return {
            "class_cache_size": len(cls._cache),
            "instance_cache_size": len(cls._instance_cache),
            "cached_classes": list(cls._cache.keys())
        }
    
    @classmethod
    def is_cached(cls, module_path: str, class_name: str) -> bool:
        """
        检查类是否在缓存中
        
        Args:
            module_path: 模块路径
            class_name: 类名
            
        Returns:
            是否在缓存中
        """
        cache_key = cls._get_cache_key(module_path, class_name)
        return cache_key in cls._cache


class DatasetFactory:
    """
    数据集工厂
    
    通过数据集名称创建完整的数据集管理器
    自动查找注册信息并动态导入相应模块
    """
    
    def __init__(self, registry: Optional[Any] = None):
        """
        初始化数据集工厂
        
        Args:
            registry: 数据集注册中心，如果为None则创建新实例
        """
        if registry is None:
            from .dataset_registry import DatasetRegistry
            self.registry = DatasetRegistry()
        else:
            self.registry = registry
    
    def create(
        self,
        dataset_name: str,
        data_root: str,
        num_clients: int,
        partition_strategy: str = "iid",
        partition_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DatasetManagerBase:
        """
        创建数据集管理器
        
        Args:
            dataset_name: 数据集名称
            data_root: 数据根目录
            num_clients: 客户端数量
            partition_strategy: 划分策略
            partition_params: 划分策略参数
            **kwargs: 其他参数
            
        Returns:
            数据集管理器实例
            
        Raises:
            ValueError: 数据集未注册
            ImportError: 动态导入失败
        """
        # 获取注册信息
        registration = self.registry.get(dataset_name)
        
        if registration is None:
            raise ValueError(
                f"数据集 '{dataset_name}' 未注册。"
                f"可用数据集: {self.list_available_datasets()}"
            )
        
        logger.info(
            f"创建数据集管理器: {dataset_name}, "
            f"策略: {partition_strategy}, 客户端数: {num_clients}"
        )
        
        # 创建管理器实例
        try:
            manager = DynamicImporter.create_manager(
                registration=registration,
                data_root=data_root,
                num_clients=num_clients,
                partition_strategy=partition_strategy,
                partition_params=partition_params,
                **kwargs
            )
            
            logger.info(f"数据集管理器创建成功: {dataset_name}")
            return manager
            
        except Exception as e:
            logger.error(f"创建数据集管理器失败: {e}")
            raise
    
    def create_components(
        self,
        dataset_name: str,
        data_root: str,
        num_clients: int,
        partition_strategy: str = "iid",
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建数据集的所有组件
        
        Args:
            dataset_name: 数据集名称
            data_root: 数据根目录
            num_clients: 客户端数量
            partition_strategy: 划分策略
            **kwargs: 其他参数
            
        Returns:
            {
                "raw_dataset": 原始数据集实例,
                "preprocessor": 预处理器实例,
                "partitioner": 划分器实例,
            }
        """
        registration = self.registry.get(dataset_name)
        
        if registration is None:
            raise ValueError(f"数据集 '{dataset_name}' 未注册")
        
        components = {}
        
        # 创建原始数据集
        components["raw_dataset"] = DynamicImporter.create_raw_dataset(
            registration=registration,
            data_root=data_root
        )
        
        # 创建预处理器
        components["preprocessor"] = DynamicImporter.create_preprocessor(
            registration=registration
        )
        
        # 创建划分器
        components["partitioner"] = DynamicImporter.create_partitioner(
            registration=registration,
            num_clients=num_clients,
            strategy=partition_strategy,
            **kwargs
        )
        
        return components
    
    def list_available_datasets(self) -> List[str]:
        """
        列出所有可用数据集名称
        
        Returns:
            数据集名称列表
        """
        registrations = self.registry.list_datasets()
        return [reg.name for reg in registrations]
    
    def get_dataset_info(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """
        获取数据集信息
        
        Args:
            dataset_name: 数据集名称
            
        Returns:
            数据集信息字典
        """
        registration = self.registry.get(dataset_name)
        
        if registration:
            return registration.to_dict()
        
        return None
    
    def get_supported_strategies(self, dataset_name: str) -> List[str]:
        """
        获取数据集支持的划分策略
        
        Args:
            dataset_name: 数据集名称
            
        Returns:
            策略名称列表
        """
        from .dataset_registry import PartitionStrategyRegistry
        
        strategy_registry = PartitionStrategyRegistry()
        strategies = strategy_registry.get_supported_strategies(dataset_name)
        
        return [s.name for s in strategies]
