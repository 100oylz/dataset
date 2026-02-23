# Core 模块

> 联邦学习数据集管理框架的核心基类定义模块

## 概述

Core 模块定义了所有数据集组件必须遵循的抽象基类。遵循**单一职责原则**，每个基类只定义一个功能领域的接口：

- **RawDatasetBase**: 原始数据的下载和加载
- **PreprocessorBase**: 数据预处理和增强
- **PartitionerBase**: 联邦学习数据划分
- **DatasetManagerBase**: 协调管理上述组件

## 模块结构

```
core/
├── __init__.py                  # 导出所有基类
├── raw_dataset_base.py          # 原始数据集基类
├── preprocessor_base.py         # 预处理器基类
├── partitioner_base.py          # 划分器基类
└── dataset_manager_base.py      # 数据集管理器基类
```

## 核心类详解

### 1. RawDatasetBase

**职责**: 定义原始数据集的接口

**抽象属性**:
- `name`: 数据集名称
- `num_classes`: 类别数量
- `num_features`: 特征维度
- `input_shape`: 输入数据形状 (C, H, W) 或 (D,)
- `train_samples`: 训练样本数
- `test_samples`: 测试样本数

**抽象方法**:
- `download()`: 下载原始数据
- `load_train_data()`: 加载训练集（返回 PyTorch Dataset）
- `load_test_data()`: 加载测试集（返回 PyTorch Dataset）

**示例**:
```python
from core import RawDatasetBase

class MyDatasetRawDataset(RawDatasetBase):
    @property
    def name(self) -> str:
        return "my_dataset"
    
    @property
    def num_classes(self) -> int:
        return 10
    
    def download(self) -> None:
        # 实现数据下载逻辑
        pass
    
    def load_train_data(self) -> Dataset:
        # 返回训练数据集
        pass
```

### 2. PreprocessorBase

**职责**: 定义数据预处理器的接口

**抽象属性**:
- `name`: 预处理器名称

**抽象方法**:
- `fit(dataset)`: 根据数据拟合参数（如计算均值、标准差）
- `get_train_transform()`: 获取训练数据变换函数
- `get_test_transform()`: 获取测试数据变换函数

**已实现方法**:
- `inverse_transform()`: 逆向变换（反归一化）
- `save_params(path)`: 保存预处理参数
- `load_params(path)`: 加载预处理参数
- `get_params()`: 获取参数字典
- `set_params(params)`: 设置参数

**示例**:
```python
from core import PreprocessorBase

class MyDatasetPreprocessor(PreprocessorBase):
    @property
    def name(self) -> str:
        return "my_preprocessor"
    
    def fit(self, dataset):
        # 计算并保存统计量
        return self
    
    def get_train_transform(self):
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
```

### 3. PartitionerBase

**职责**: 定义联邦学习数据划分器的接口

**抽象属性**:
- `name`: 划分策略名称
- `strategy_type`: 策略类型（"iid" 或 "non-iid"）

**抽象方法**:
- `partition(dataset)`: 执行划分，返回 `{client_id: [indices]}`

**已实现方法**:
- `get_client_dataset(dataset, client_id, client_indices)`: 获取客户端数据子集
- `get_distribution(dataset, client_indices)`: 获取各客户端的数据分布
- `get_statistics(dataset, client_indices)`: 获取划分统计信息
- `save_partition(client_indices, path)`: 保存划分结果
- `load_partition(path)`: 加载划分结果

**内置划分器**:
- `IIDPartitioner`: 独立同分布划分
- `DirichletPartitioner`: Dirichlet 分布 Non-IID 划分
- `PathologicalPartitioner`: 病态 Non-IID 划分

**示例**:
```python
from core import IIDPartitioner

class MyDatasetIIDPartitioner(IIDPartitioner):
    @property
    def name(self) -> str:
        return "my_dataset_iid"
    
    @property
    def strategy_type(self) -> str:
        return "iid"
    
    def partition(self, dataset):
        # 实现 IID 划分逻辑
        num_samples = len(dataset)
        indices = list(range(num_samples))
        # ... 划分逻辑
        return client_indices
```

### 4. DatasetManagerBase

**职责**: 定义数据集管理器的接口，协调 raw/preprocessor/partitioner

**抽象属性**:
- `dataset_name`: 数据集名称
- `raw_dataset_class`: 原始数据集类
- `preprocessor_class`: 预处理器类
- `partitioner_class`: 划分器类

**抽象方法**:
- `prepare_data()`: 准备数据（下载 -> 预处理 -> 划分）
- `get_client_loader(client_id, batch_size)`: 获取客户端数据加载器
- `get_test_loader(batch_size)`: 获取测试数据加载器
- `get_client_dataset(client_id)`: 获取客户端数据集
- `get_test_dataset()`: 获取测试数据集

**示例**:
```python
from core import DatasetManagerBase

class MyDatasetManager(DatasetManagerBase):
    @property
    def dataset_name(self) -> str:
        return "my_dataset"
    
    @property
    def raw_dataset_class(self):
        from datasets.my_dataset import MyDatasetRawDataset
        return MyDatasetRawDataset
    
    def prepare_data(self, force_download=False, force_preprocess=False):
        # 实现数据准备流程
        pass
```

### 5. FederatedDatasetManager

**继承**: `DatasetManagerBase`

**职责**: 提供联邦学习场景下的专用数据管理功能

这是 `DatasetManagerBase` 的特化版本，为联邦学习场景提供额外的便利方法。

### 6. ComposePreprocessor

**继承**: `PreprocessorBase`

**职责**: 组合多个预处理器

用于将多个预处理步骤按顺序组合执行。

## 使用示例

### 创建自定义数据集组件

```python
from core import (
    RawDatasetBase,
    PreprocessorBase,
    IIDPartitioner,
    DatasetManagerBase
)

# 1. 实现原始数据集
class CustomRawDataset(RawDatasetBase):
    @property
    def num_classes(self) -> int:
        return 10
    
    def download(self) -> None:
        pass
    
    def load_train_data(self) -> Dataset:
        # 加载训练数据
        pass
    
    def load_test_data(self) -> Dataset:
        # 加载测试数据
        pass

# 2. 实现预处理器
class CustomPreprocessor(PreprocessorBase):
    def get_train_transform(self):
        return transforms.ToTensor()
    
    def get_test_transform(self):
        return transforms.ToTensor()

# 3. 实现划分器
class CustomIIDPartitioner(IIDPartitioner):
    def partition(self, dataset):
        # 划分逻辑
        pass

# 4. 实现管理器
class CustomManager(DatasetManagerBase):
    @property
    def raw_dataset_class(self):
        return CustomRawDataset
    
    @property
    def preprocessor_class(self):
        return CustomPreprocessor
```

## 设计原则

1. **单一职责**: 每个基类只定义一个功能领域的接口
2. **抽象基类**: 使用 `ABC` 和 `@abstractmethod` 强制子类实现必要方法
3. **类型安全**: 所有抽象方法和属性都有类型注解
4. **可扩展性**: 通过继承基类可以轻松添加新功能

## 注意事项

- 所有抽象方法和属性必须被子类实现
- 保持接口的向后兼容性
- 添加新抽象方法时，需更新所有现有子类
