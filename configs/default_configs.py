"""
默认配置模块

提供数据集的默认配置和配置管理
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from utils.helpers import load_json, save_json

DB_DATACONFIG_PATH = os.getenv("DB_DATA_CONFIG_PATH", "./data_configs")
DB_PARTITION_PATH = os.getenv("DB_PARTITION_PATH", "./partition_configs")


@dataclass
class DatasetConfig:
    """
    数据集配置类

    包含数据集的所有配置参数
    """

    # 基础配置
    dataset_name: str = ""  # 数据集名称
    data_root: str = "./data"  # 数据根目录

    # 联邦学习配置
    num_clients: int = 10  # 客户端数量
    partition_strategy: str = "iid"  # 划分策略
    partition_params: Dict[str, Any] = field(default_factory=dict)  # 划分参数

    # 预处理配置
    augment: bool = True  # 是否数据增强
    normalize: bool = True  # 是否归一化

    # 数据加载配置
    batch_size: int = 32  # 批次大小
    num_workers: int = 0  # 数据加载线程数
    pin_memory: bool = False  # 是否锁页内存

    # 随机种子
    seed: int = 42  # 随机种子

    # 其他参数
    download: bool = True  # 是否自动下载
    force_preprocess: bool = False  # 是否强制重新预处理

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dataset_name": self.dataset_name,
            "data_root": self.data_root,
            "num_clients": self.num_clients,
            "partition_strategy": self.partition_strategy,
            "partition_params": self.partition_params,
            "augment": self.augment,
            "normalize": self.normalize,
            "batch_size": self.batch_size,
            "num_workers": self.num_workers,
            "pin_memory": self.pin_memory,
            "seed": self.seed,
            "download": self.download,
            "force_preprocess": self.force_preprocess,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DatasetConfig":
        """从字典创建配置"""
        # 过滤掉不在 dataclass 中的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered_dict)

    def update(self, **kwargs) -> "DatasetConfig":
        """更新配置并返回自身（支持链式调用）"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


def get_dataset_config(dataset_name: str) -> Dict[str, Any]:
    """
    从数据库目录加载数据集配置

    Args:
        dataset_name: 数据集名称

    Returns:
        数据集配置字典

    Raises:
        FileNotFoundError: 当数据集配置不存在时
    """
    config_file = Path(DB_DATACONFIG_PATH) / dataset_name / "config.json"

    if not config_file.exists():
        raise FileNotFoundError(f"数据集 '{dataset_name}' 的配置不存在: {config_file}")

    return load_json(config_file)


def get_partition_config(strategy: str) -> Dict[str, Any]:
    """
    从配置目录加载划分策略配置

    Args:
        strategy: 划分策略名称

    Returns:
        划分策略配置字典

    Raises:
        FileNotFoundError: 当划分策略配置不存在时
    """
    config_file = Path(DB_PARTITION_PATH) / f"{strategy}.json"

    if not config_file.exists():
        raise FileNotFoundError(f"划分策略 '{strategy}' 的配置不存在: {config_file}")

    return load_json(config_file)


def build_config(
    dataset_name: str,
    num_clients: int = 10,
    partition_strategy: str = "iid",
    partition_params: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    **kwargs,
) -> DatasetConfig:
    """
    构建数据集配置

    从各自配置目录加载数据集和划分策略配置，构建完整的 DatasetConfig 对象。
    如提供 save_path，将配置保存到指定路径。

    Args:
        dataset_name: 数据集名称
        num_clients: 客户端数量
        partition_strategy: 划分策略
        partition_params: 划分参数，如为 None 则使用策略默认参数
        save_path: 配置保存路径，如为 None 则不保存
        **kwargs: 其他参数覆盖（如 data_root, batch_size 等）

    Returns:
        数据集配置对象
    """
    # 加载数据集配置
    dataset_info = get_dataset_config(dataset_name)

    # 加载划分策略配置，获取默认参数
    if partition_params is None:
        try:
            strategy_config = get_partition_config(partition_strategy)
            partition_params = strategy_config.get("default_params", {})
        except FileNotFoundError:
            partition_params = {}

    # 构建配置对象
    config = DatasetConfig(
        dataset_name=dataset_name,
        num_clients=num_clients,
        partition_strategy=partition_strategy,
        partition_params=partition_params,
    )

    # 应用其他参数覆盖
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    # 保存配置到文件（如指定路径）
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        # 确保路径以 .json 结尾
        if save_path.suffix != ".json":
            save_path = save_path.with_suffix(".json")
        save_json(config.to_dict(), save_path)

    return config
