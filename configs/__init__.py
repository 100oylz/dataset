"""
配置模块

提供数据集和划分策略的配置管理
"""

from .default_configs import (
    DatasetConfig,
    DEFAULT_DATASET_CONFIGS,
    DEFAULT_PARTITION_CONFIGS,
    get_dataset_config,
    get_partition_config,
    build_config,
)

__all__ = [
    "DatasetConfig",
    "DEFAULT_DATASET_CONFIGS",
    "DEFAULT_PARTITION_CONFIGS",
    "get_dataset_config",
    "get_partition_config",
    "build_config",
]
