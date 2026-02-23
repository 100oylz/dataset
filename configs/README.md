# Configs 模块

> 联邦学习数据集管理框架的配置管理模块

## 概述

Configs 模块提供数据集和划分策略的配置管理功能。通过集中管理默认配置，简化了数据集的创建和使用过程。

## 模块结构

```
configs/
├── __init__.py              # 导出配置相关类和函数
└── default_configs.py       # 默认配置定义
```

## 核心类详解

### 1. DatasetConfig

**位置**: `default_configs.py`

**职责**: 数据集配置的完整数据类，包含数据集使用的所有参数

**配置字段**:

| 类别 | 字段 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| 基础配置 | `dataset_name` | str | "" | 数据集名称 |
| | `data_root` | str | "./data" | 数据根目录 |
| 联邦学习 | `num_clients` | int | 10 | 客户端数量 |
| | `partition_strategy` | str | "iid" | 划分策略 |
| | `partition_params` | dict | {} | 划分策略参数 |
| 预处理 | `augment` | bool | True | 是否数据增强 |
| | `normalize` | bool | True | 是否归一化 |
| 数据加载 | `batch_size` | int | 32 | 批次大小 |
| | `num_workers` | int | 0 | 数据加载线程数 |
| | `pin_memory` | bool | False | 是否锁页内存 |
| 其他 | `seed` | int | 42 | 随机种子 |
| | `download` | bool | True | 是否自动下载 |
| | `force_preprocess` | bool | False | 是否强制重新预处理 |

**方法**:
- `to_dict()`: 转换为字典
- `from_dict(config_dict)`: 从字典创建
- `update(**kwargs)`: 更新配置

**示例**:
```python
from configs import DatasetConfig

# 创建配置
config = DatasetConfig(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)

# 转换为字典
config_dict = config.to_dict()

# 从字典创建
config = DatasetConfig.from_dict(config_dict)

# 更新配置
config.update(num_clients=20, batch_size=64)
```

### 2. DEFAULT_DATASET_CONFIGS

**位置**: `default_configs.py`

**职责**: 存储所有内置数据集的默认配置

**结构**:
```python
DEFAULT_DATASET_CONFIGS: Dict[str, Dict[str, Any]] = {
    "mnist": {
        "num_classes": 10,
        "num_features": 784,
        "input_shape": (1, 28, 28),
        "train_samples": 60000,
        "test_samples": 10000,
        "data_type": "image",
        "task_type": "classification",
        "class_names": [...],
        # 模块路径（用于动态导入）
        "raw_dataset_module": "datasets.mnist.raw",
        "raw_dataset_class": "MNISTRawDataset",
        "preprocessor_module": "datasets.mnist.preprocess",
        "preprocessor_class": "MNISTPreprocessor",
        "partitioner_module": "datasets.mnist.partition",
        "partitioner_class": "MNISTPartitioner",
    },
    "cifar10": {...},
    "fashion_mnist": {...},
}
```

### 3. DEFAULT_PARTITION_CONFIGS

**位置**: `default_configs.py`

**职责**: 存储所有划分策略的默认配置

**结构**:
```python
DEFAULT_PARTITION_CONFIGS: Dict[str, Dict[str, Any]] = {
    "iid": {
        "description": "独立同分布划分",
        "strategy_type": "iid",
        "default_params": {},
    },
    "dirichlet": {
        "description": "Dirichlet分布Non-IID划分",
        "strategy_type": "non-iid",
        "default_params": {"alpha": 0.5},
        "param_schema": {
            "alpha": {
                "type": "float",
                "default": 0.5,
                "description": "Dirichlet分布参数，越小越Non-IID",
                "min": 0.01,
                "max": 100.0,
            }
        },
    },
    "pathological": {
        "description": "病态Non-IID划分",
        "strategy_type": "non-iid",
        "default_params": {"shards_per_client": 2},
        "param_schema": {
            "shards_per_client": {
                "type": "int",
                "default": 2,
                "description": "每个客户端的类别数",
                "min": 1,
            }
        },
    },
}
```

### 4. 辅助函数

#### get_dataset_config(dataset_name: str) -> Dict[str, Any]

获取指定数据集的默认配置

```python
from configs import get_dataset_config

config = get_dataset_config("mnist")
print(config["num_classes"])  # 10
print(config["input_shape"])  # (1, 28, 28)
```

#### get_partition_config(strategy: str) -> Dict[str, Any]

获取指定划分策略的配置

```python
from configs import get_partition_config

config = get_partition_config("dirichlet")
print(config["default_params"])  # {"alpha": 0.5}
```

#### build_config(...) -> DatasetConfig

构建完整的数据集配置

```python
from configs import build_config

config = build_config(
    dataset_name="mnist",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    batch_size=64
)
```

## 配置层级

配置按以下优先级合并（高优先级覆盖低优先级）：

1. **运行时参数**: 函数调用时传入的参数
2. **用户配置文件**: 用户自定义的 YAML/JSON 配置文件
3. **DatasetConfig 默认值**: `DatasetConfig` 类中的默认值
4. **数据集特定配置**: `DEFAULT_DATASET_CONFIGS` 中的配置
5. **划分策略配置**: `DEFAULT_PARTITION_CONFIGS` 中的配置

## 使用示例

### 示例1: 使用 build_config 创建配置

```python
from configs import build_config

# 构建 MNIST 配置，使用 Dirichlet 划分
config = build_config(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    batch_size=32,
    augment=True
)

print(config)
# DatasetConfig(
#   dataset_name='mnist',
#   data_root='./data',
#   num_clients=10,
#   partition_strategy='dirichlet',
#   partition_params={'alpha': 0.5},
#   ...
# )
```

### 示例2: 查询数据集信息

```python
from configs import get_dataset_config, DEFAULT_DATASET_CONFIGS

# 获取所有支持的数据集
all_datasets = list(DEFAULT_DATASET_CONFIGS.keys())
print(all_datasets)  # ['mnist', 'cifar10', 'fashion_mnist']

# 获取特定数据集信息
mnist_info = get_dataset_config("mnist")
print(f"MNIST 类别数: {mnist_info['num_classes']}")
print(f"MNIST 训练样本: {mnist_info['train_samples']}")
```

### 示例3: 查询划分策略信息

```python
from configs import get_partition_config, DEFAULT_PARTITION_CONFIGS

# 获取所有支持的策略
all_strategies = list(DEFAULT_PARTITION_CONFIGS.keys())
print(all_strategies)  # ['iid', 'dirichlet', 'pathological']

# 获取特定策略信息
dirichlet_info = get_partition_config("dirichlet")
print(f"描述: {dirichlet_info['description']}")
print(f"默认参数: {dirichlet_info['default_params']}")
print(f"参数模式: {dirichlet_info['param_schema']}")
```

### 示例4: 修改配置

```python
from configs import DatasetConfig

# 从默认配置创建
config = DatasetConfig()

# 修改配置
config.dataset_name = "cifar10"
config.num_clients = 20
config.batch_size = 64

# 或使用 update 方法
config.update(
    num_clients=20,
    batch_size=64,
    seed=123
)
```

## 添加新数据集配置

添加新数据集时，需要在 `DEFAULT_DATASET_CONFIGS` 中添加配置：

```python
# configs/default_configs.py

DEFAULT_DATASET_CONFIGS = {
    # ... 现有配置
    
    "my_dataset": {
        "num_classes": 10,
        "num_features": 3072,
        "input_shape": (3, 32, 32),
        "train_samples": 50000,
        "test_samples": 10000,
        "data_type": "image",
        "task_type": "classification",
        "class_names": ['class0', 'class1', ...],
        # 模块路径
        "raw_dataset_module": "datasets.my_dataset.raw",
        "raw_dataset_class": "MyDatasetRawDataset",
        "preprocessor_module": "datasets.my_dataset.preprocess",
        "preprocessor_class": "MyDatasetPreprocessor",
        "partitioner_module": "datasets.my_dataset.partition",
        "partitioner_class": "MyDatasetPartitioner",
    },
}
```

## 添加新划分策略配置

添加新划分策略时，需要在 `DEFAULT_PARTITION_CONFIGS` 中添加配置：

```python
# configs/default_configs.py

DEFAULT_PARTITION_CONFIGS = {
    # ... 现有配置
    
    "my_strategy": {
        "description": "我的自定义划分策略",
        "strategy_type": "non-iid",  # 或 "iid"
        "default_params": {
            "param1": 0.5,
            "param2": 10,
        },
        "param_schema": {
            "param1": {
                "type": "float",
                "default": 0.5,
                "description": "参数1的描述",
                "min": 0.0,
                "max": 1.0,
            },
            "param2": {
                "type": "int",
                "default": 10,
                "description": "参数2的描述",
                "min": 1,
            },
        },
    },
}
```

## 注意事项

1. **模块路径**: 配置中的模块路径必须与实际的文件路径一致
2. **类名正确性**: 确保类名拼写正确，否则动态导入会失败
3. **数据一致性**: 统计信息（如 `train_samples`）应与实际数据一致
4. **参数范围**: `param_schema` 中定义的范围应合理，用于参数验证
