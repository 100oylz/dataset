# Core 模块

> 联邦学习数据集管理框架的核心基类定义模块

## 概述

Core 模块定义了所有数据集组件必须遵循的抽象基类，并提供了核心实现。遵循**单一职责原则**，每个基类只定义一个功能领域的接口：

- **RawDatasetBase**: 原始数据的下载和加载
- **PreprocessorBase**: 数据预处理和增强
- **PartitionerBase**: 联邦学习数据划分（含 IID、Dirichlet、Pathological 实现）
- **DatasetManagerBase**: 协调管理上述组件
- **FederatedDatasetManager**: 联邦学习场景下的完整管理器实现

## 模块结构

```
core/
├── __init__.py                  # 导出所有基类
├── raw_dataset_base.py          # 原始数据集基类
├── preprocessor_base.py         # 预处理器基类 + ComposePreprocessor
├── partitioner_base.py          # 划分器基类 + 3种划分实现
└── dataset_manager_base.py      # 数据集管理器基类 + FederatedDatasetManager
```

## 核心类详解

### 1. RawDatasetBase

**职责**: 定义原始数据集的接口

**抽象属性**:
- `num_classes`: 类别数量
- `num_features`: 特征维度
- `input_shape`: 输入数据形状 (C, H, W) 或 (D,)
- `train_samples`: 训练样本数
- `test_samples`: 测试样本数

**已实现属性**:
- `name`: 数据集名称（返回 `_dataset_name`）

**抽象方法**:
- `download()`: 下载原始数据
- `load_train_data()`: 加载训练集（返回 PyTorch Dataset）
- `load_test_data()`: 加载测试集（返回 PyTorch Dataset）

**示例**:
```python
from core import RawDatasetBase

class MyDatasetRawDataset(RawDatasetBase):
    @property
    def num_classes(self) -> int:
        return 10
    
    @property
    def num_features(self) -> int:
        return 784
    
    @property
    def input_shape(self) -> Tuple[int, ...]:
        return (1, 28, 28)
    
    def download(self) -> None:
        # 实现数据下载逻辑
        pass
    
    def load_train_data(self) -> Dataset:
        # 返回训练数据集
        pass
    
    def load_test_data(self) -> Dataset:
        # 返回测试数据集
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
- `inverse_transform(data)`: 逆向变换（反归一化），默认返回原数据
- `save_params(path)`: 保存预处理参数为 JSON
- `load_params(path)`: 从 JSON 加载预处理参数
- `get_params()`: 获取参数字典
- `set_params(params)`: 设置参数

**示例**:
```python
from core import PreprocessorBase
from torchvision import transforms

class MyDatasetPreprocessor(PreprocessorBase):
    MEAN = [0.5]
    STD = [0.5]
    
    @property
    def name(self) -> str:
        return "my_preprocessor"
    
    def fit(self, dataset):
        # 计算并保存统计量
        return self
    
    def get_train_transform(self):
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        ])
    
    def get_test_transform(self):
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        ])
```

### 3. ComposePreprocessor

**继承**: `PreprocessorBase`

**职责**: 组合多个预处理器，按顺序应用各自的变换

**示例**:
```python
from core import ComposePreprocessor

# 创建多个预处理器
preprocessor1 = ResizePreprocessor(size=224)
preprocessor2 = NormalizePreprocessor(mean=[0.5], std=[0.5])

# 组合
composed = ComposePreprocessor([preprocessor1, preprocessor2])

# 获取组合后的变换
train_transform = composed.get_train_transform()
```

### 4. PartitionerBase

**职责**: 定义联邦学习数据划分器的接口

**抽象属性**:
- `name`: 划分策略名称
- `strategy_type`: 策略类型（"iid" 或 "non-iid"）

**抽象方法**:
- `partition(dataset)`: 执行划分，返回 `{client_id: [indices]}`

**已实现方法**:
- `get_client_dataset(dataset, client_id, client_indices)`: 获取客户端数据子集（返回 Subset）
- `get_distribution(dataset, client_indices)`: 获取各客户端的类别分布
- `get_statistics(dataset, client_indices)`: 获取划分统计信息（样本数、不平衡比例等）
- `save_partition(client_indices, path)`: 保存划分结果为 JSON
- `load_partition(path)`: 从 JSON 加载划分结果

**示例**:
```python
from core import PartitionerBase

class MyCustomPartitioner(PartitionerBase):
    def __init__(self, num_clients: int, custom_param: float, seed: int = 42):
        super().__init__(num_clients, seed, custom_param=custom_param)
        self.custom_param = custom_param
    
    @property
    def name(self) -> str:
        return "my_custom"
    
    @property
    def strategy_type(self) -> str:
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # 实现自定义划分逻辑
        client_indices = {}
        # ... 划分代码
        return client_indices
```

### 5. IIDPartitioner

**继承**: `PartitionerBase`

**职责**: 独立同分布（IID）划分

**实现逻辑**: 随机打乱数据索引，然后均匀分配给各客户端

**示例**:
```python
from core import IIDPartitioner

# 创建 IID 划分器
partitioner = IIDPartitioner(num_clients=10, seed=42)

# 执行划分
client_indices = partitioner.partition(dataset)

# 获取统计信息
stats = partitioner.get_statistics(dataset, client_indices)
print(f"总样本数: {stats['total_samples']}")
print(f"每个客户端平均样本数: {stats['statistics']['mean_samples_per_client']}")
```

### 6. DirichletPartitioner

**继承**: `PartitionerBase`

**职责**: 基于 Dirichlet 分布的 Non-IID 划分

**参数**:
- `alpha`: Dirichlet 分布浓度参数（默认 0.5）
  - 越小越 Non-IID（客户端数据分布差异越大）
  - 越大越接近 IID
  - 当 alpha → ∞ 时，接近 IID 划分

**示例**:
```python
from core import DirichletPartitioner

# 创建 Dirichlet 划分器（alpha=0.5 产生较明显的 Non-IID）
partitioner = DirichletPartitioner(num_clients=10, alpha=0.5, seed=42)

# 执行划分
client_indices = partitioner.partition(dataset)

# 查看类别分布
distribution = partitioner.get_distribution(dataset, client_indices)
print(distribution[0])  # 客户端 0 的类别分布
```

### 7. PathologicalPartitioner

**继承**: `PartitionerBase`

**职责**: 病态 Non-IID 划分（基于 shard 的划分）

**参数**:
- `shards_per_client`: 每个客户端获得的类别数（shard 数，默认 2）

**实现逻辑**: 
1. 按类别排序所有样本
2. 将数据分成 `num_clients * shards_per_client` 个 shard
3. 每个客户端随机获得 `shards_per_client` 个 shard

**示例**:
```python
from core import PathologicalPartitioner

# 创建 Pathological 划分器（每个客户端获得 2 个类别）
partitioner = PathologicalPartitioner(
    num_clients=10, 
    shards_per_client=2, 
    seed=42
)

# 执行划分
client_indices = partitioner.partition(dataset)

# 保存划分结果
partitioner.save_partition(client_indices, "./pathological_split.json")

# 加载划分结果
loaded_indices = partitioner.load_partition("./pathological_split.json")
```

### 8. DatasetManagerBase

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

**已实现方法**:
- `get_data_info()`: 获取数据基本信息
- `get_partition_info()`: 获取划分信息
- `save_split(path)`: 保存划分结果
- `load_split(path)`: 加载划分结果

### 9. FederatedDatasetManager

**继承**: `DatasetManagerBase`

**职责**: 提供联邦学习场景下的完整数据管理功能

**特性**:
- **懒加载模式**: 首次访问数据时才真正准备数据
- **自动数据准备**: 自动执行下载 -> 预处理 -> 划分流程
- **划分持久化**: 支持划分结果的保存和加载
- **完整统计**: 提供数据和划分的详细统计信息

**子类只需指定**:
- `dataset_name`: 数据集名称
- `raw_dataset_class`: 原始数据集类
- `preprocessor_class`: 预处理器类
- `partitioner_class`: 划分器类

**示例**:
```python
from core import FederatedDatasetManager
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor, MNISTPartitioner

class MNISTFederatedManager(FederatedDatasetManager):
    """MNIST 联邦学习数据集管理器"""
    
    @property
    def dataset_name(self) -> str:
        return "mnist"
    
    @property
    def raw_dataset_class(self):
        return MNISTRawDataset
    
    @property
    def preprocessor_class(self):
        return MNISTPreprocessor
    
    @property
    def partitioner_class(self):
        return MNISTPartitioner

# 创建管理器
manager = MNISTFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    seed=42
)

# 准备数据（懒加载：第一次访问时才真正准备）
manager.prepare_data()

# 获取客户端数据加载器
train_loader = manager.get_client_loader(0, batch_size=32, shuffle=True)

# 获取测试数据加载器
test_loader = manager.get_test_loader(batch_size=256)

# 获取数据和划分信息
data_info = manager.get_data_info()
partition_info = manager.get_partition_info()

# 保存划分结果
manager.save_split("./mnist_split.json")

# 加载划分结果（重新设置划分，不重新准备数据）
manager.load_split("./mnist_split.json")
```

## 使用示例

### 完整示例：创建自定义联邦学习数据集

```python
from core import (
    RawDatasetBase,
    PreprocessorBase,
    IIDPartitioner,
    FederatedDatasetManager
)
from torch.utils.data import Dataset
from torchvision import transforms

# 1. 实现原始数据集
class CustomRawDataset(RawDatasetBase):
    NUM_CLASSES = 10
    INPUT_SHAPE = (3, 32, 32)
    
    @property
    def num_classes(self) -> int:
        return self.NUM_CLASSES
    
    @property
    def num_features(self) -> int:
        return 3072
    
    @property
    def input_shape(self) -> Tuple[int, ...]:
        return self.INPUT_SHAPE
    
    @property
    def train_samples(self) -> int:
        return 50000
    
    @property
    def test_samples(self) -> int:
        return 10000
    
    def download(self) -> None:
        pass
    
    def load_train_data(self) -> Dataset:
        pass
    
    def load_test_data(self) -> Dataset:
        pass

# 2. 实现预处理器
class CustomPreprocessor(PreprocessorBase):
    @property
    def name(self) -> str:
        return "custom_preprocessor"
    
    def fit(self, dataset):
        return self
    
    def get_train_transform(self):
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
    
    def get_test_transform(self):
        return self.get_train_transform()

# 3. 实现划分器（继承已有实现）
class CustomIIDPartitioner(IIDPartitioner):
    @property
    def name(self) -> str:
        return "custom_iid"

class CustomDirichletPartitioner(DirichletPartitioner):
    @property
    def name(self) -> str:
        return "custom_dirichlet"

# 4. 实现管理器
class CustomFederatedManager(FederatedDatasetManager):
    @property
    def dataset_name(self) -> str:
        return "custom"
    
    @property
    def raw_dataset_class(self):
        return CustomRawDataset
    
    @property
    def preprocessor_class(self):
        return CustomPreprocessor
    
    @property
    def partitioner_class(self):
        return CustomDirichletPartitioner

# 5. 使用
manager = CustomFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)
manager.prepare_data()
loader = manager.get_client_loader(0, batch_size=32)
```

## 设计原则

1. **单一职责**: 每个基类只定义一个功能领域的接口
2. **抽象基类**: 使用 `ABC` 和 `@abstractmethod` 强制子类实现必要方法
3. **类型安全**: 所有抽象方法和属性都有类型注解
4. **可扩展性**: 通过继承基类可以轻松添加新功能
5. **默认实现**: 常用功能（如划分策略）提供默认实现，减少重复代码

## 注意事项

- 所有抽象方法和属性必须被子类实现
- `FederatedDatasetManager` 已实现所有抽象方法，子类只需指定类属性
- `IIDPartitioner`、`DirichletPartitioner`、`PathologicalPartitioner` 已实现完整逻辑，子类通常只需重写 `name` 属性
- 保持接口的向后兼容性
- 添加新抽象方法时，需更新所有现有子类
