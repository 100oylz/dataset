# Core 模块 - AI Agent 指引

> 为 AI Agent 提供的 Core 模块开发和维护指南

## 🎯 模块定位

Core 模块是整个框架的**基石**，定义了所有数据集组件的契约（Contract）。修改此模块会影响整个框架，需要特别谨慎。

## 📁 文件职责

| 文件 | 职责 | 修改风险 | 实现状态 |
|------|------|----------|----------|
| `raw_dataset_base.py` | 定义原始数据集接口 | ⭐⭐⭐⭐⭐ 高 | 基类定义完成 |
| `preprocessor_base.py` | 定义预处理器接口 | ⭐⭐⭐⭐ 中高 | 基类 + ComposePreprocessor 实现完成 |
| `partitioner_base.py` | 定义划分器接口 | ⭐⭐⭐⭐ 中高 | 基类 + 3种划分策略实现完成 |
| `dataset_manager_base.py` | 定义管理器接口 | ⭐⭐⭐⭐⭐ 高 | 基类 + FederatedDatasetManager 实现完成 |
| `__init__.py` | 统一导出接口 | ⭐⭐ 低 | 完成 |

## 🔧 常见任务

### 任务1: 向 RawDatasetBase 添加新抽象属性

**场景**: 需要所有数据集提供新的元信息

**步骤**:
1. 在 `RawDatasetBase` 中添加新的 `@abstractmethod` 装饰的属性
2. 更新所有数据集的 `raw.py` 实现
3. 更新 `configs/default_configs.py` 中的默认配置

**示例**:
```python
# raw_dataset_base.py
@property
@abstractmethod
def class_weights(self) -> List[float]:
    """类别权重，用于处理不平衡数据"""
    pass

# 然后在每个数据集的 raw.py 中实现
@property
def class_weights(self) -> List[float]:
    return [1.0] * self.num_classes
```

### 任务2: 添加新的划分策略基类

**场景**: 需要支持现有划分器无法实现的划分方式

**步骤**:
1. 在 `partitioner_base.py` 中创建新的划分器类
2. 继承 `PartitionerBase`
3. 定义策略特定的参数
4. 实现 `name`、`strategy_type` 属性和 `partition()` 方法
5. 在 `__init__.py` 中导出

**示例**:
```python
# partitioner_base.py
class ClusterPartitioner(PartitionerBase):
    """
    基于聚类的划分器
    
    根据数据特征相似性进行划分
    """
    
    def __init__(self, num_clients: int, num_clusters: int, seed: int = 42):
        super().__init__(num_clients, seed)
        self.num_clusters = num_clusters
    
    @property
    def name(self) -> str:
        return "cluster"
    
    @property
    def strategy_type(self) -> str:
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # 实现聚类划分逻辑
        pass
```

### 任务3: 修改 PreprocessorBase 接口

**场景**: 需要添加新的预处理方法

**注意**: 这会影响到所有数据集的预处理器实现

**步骤**:
1. 在 `PreprocessorBase` 中添加新方法
2. 如果方法是抽象的，所有子类必须实现
3. 如果方法有默认实现，确保不会破坏现有功能

**示例**:
```python
# preprocessor_base.py
class PreprocessorBase(ABC):
    # ... 现有代码
    
    @abstractmethod
    def get_validation_transform(self) -> Callable:
        """
        获取验证数据变换
        
        用于早停时的验证集评估
        """
        pass
```

### 任务4: 使用 FederatedDatasetManager

**场景**: 创建一个新的联邦学习数据集管理器

**注意**: `FederatedDatasetManager` 已实现所有抽象方法，子类只需指定类属性

**示例**:
```python
from core import FederatedDatasetManager
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor, MNISTPartitioner

class MNISTFederatedManager(FederatedDatasetManager):
    """
    MNIST 联邦学习数据集管理器
    
    只需指定以下类属性，父类会自动完成数据准备流程：
    - dataset_name: 数据集名称
    - raw_dataset_class: 原始数据集类
    - preprocessor_class: 预处理器类
    - partitioner_class: 划分器类
    """
    
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

# 使用示例
manager = MNISTFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    seed=42
)

# 准备数据（下载 -> 预处理 -> 划分）
manager.prepare_data()

# 获取客户端数据加载器
loader = manager.get_client_loader(0, batch_size=32)

# 获取划分统计信息
info = manager.get_partition_info()
print(info["statistics"])

# 保存划分结果
manager.save_split("./mnist_split.json")
```

### 任务5: 修复接口兼容性问题

**场景**: 修改基类后导致子类不兼容

**检查清单**:
- [ ] 所有抽象方法都有实现
- [ ] 所有抽象属性都有定义
- [ ] 方法签名一致（参数名、类型、返回值）
- [ ] 没有遗漏任何数据集实现

**快速检查脚本**:
```python
# 检查所有基类是否可实例化
from core import RawDatasetBase, PreprocessorBase, PartitionerBase

# 这些应该都不能直接实例化
try:
    RawDatasetBase()
    print("ERROR: RawDatasetBase 可以被实例化")
except TypeError:
    print("OK: RawDatasetBase 是抽象基类")

# 检查具体划分器是否可以实例化
from core import IIDPartitioner
try:
    partitioner = IIDPartitioner(num_clients=10, seed=42)
    print(f"OK: IIDPartitioner 可以实例化: {partitioner.name}")
except TypeError as e:
    print(f"ERROR: {e}")
```

## 🚨 重要约束

### 1. 抽象方法必须实现

所有标记为 `@abstractmethod` 的方法必须在子类中实现，否则子类也无法实例化。

```python
# ❌ 错误：子类没有实现抽象方法
class BadPartitioner(IIDPartitioner):
    pass  # 缺少 name 和 partition 方法的实现

# 这会抛出 TypeError
partitioner = BadPartitioner(num_clients=10)
```

### 2. FederatedDatasetManager 使用规范

```python
# ✅ 正确：只指定类属性
class MyManager(FederatedDatasetManager):
    @property
    def dataset_name(self) -> str:
        return "my_dataset"
    
    @property
    def raw_dataset_class(self):
        return MyRawDataset
    
    @property
    def preprocessor_class(self):
        return MyPreprocessor
    
    @property
    def partitioner_class(self):
        return MyPartitioner

# ❌ 错误：不需要重写已实现的方法
class BadManager(FederatedDatasetManager):
    @property
    def dataset_name(self) -> str:
        return "bad_dataset"
    
    def prepare_data(self, ...):  # 不需要重写！
        pass
```

### 3. 划分器实现规范

```python
# ✅ 正确：继承基类实现，只重写 name
class MyDatasetIIDPartitioner(IIDPartitioner):
    @property
    def name(self) -> str:
        return "my_dataset_iid"

# ❌ 错误：重复实现 partition 逻辑
class BadPartitioner(IIDPartitioner):
    @property
    def name(self) -> str:
        return "bad"
    
    def partition(self, dataset):
        # 不需要重写！父类已实现
        pass
```

### 4. 保持接口稳定性

Core 模块的接口应该保持**向后兼容**:

- **可以添加**: 新的可选方法、新的带默认值的参数
- **谨慎修改**: 现有方法的签名
- **避免删除**: 任何已存在的方法或属性

### 5. 类型注解必须准确

所有抽象方法和属性都应有准确的类型注解:

```python
# ✅ 正确
from typing import Dict, List

def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
    pass

# ❌ 错误（缺少返回类型）
def partition(self, dataset: Dataset):
    pass
```

## 🔗 模块关系

```
core/
    ├── raw_dataset_base.py
    │       ↑
    │       └── 被 datasets/*/raw.py 继承
    │
    ├── preprocessor_base.py
    │       ├── PreprocessorBase (抽象基类)
    │       │       ↑
    │       │       └── 被 datasets/*/preprocess.py 继承
    │       └── ComposePreprocessor (组合预处理器)
    │
    ├── partitioner_base.py
    │       ├── PartitionerBase (抽象基类)
    │       ├── IIDPartitioner (IID 划分实现)
    │       ├── DirichletPartitioner (Dirichlet 划分实现)
    │       └── PathologicalPartitioner (Pathological 划分实现)
    │               ↑
    │               └── 被 datasets/*/partition.py 继承
    │
    └── dataset_manager_base.py
            ├── DatasetManagerBase (抽象基类)
            └── FederatedDatasetManager (联邦学习管理器实现)
                    ↑
                    └── 被子类继承，只需指定类属性
```

## 📝 代码规范

### 添加新抽象方法

```python
@abstractmethod
def new_method(self, param: Type) -> ReturnType:
    """
    方法的简短描述
    
    详细说明方法的用途、参数和返回值。
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 什么情况下抛出此异常
    """
    pass
```

### 添加新抽象属性

```python
@property
@abstractmethod
def new_property(self) -> PropertyType:
    """
    属性的简短描述
    
    Returns:
        返回值说明
    """
    pass
```

## 🐛 调试技巧

### 检查抽象方法实现

```python
import inspect
from core import PartitionerBase

# 获取所有抽象方法
abstract_methods = PartitionerBase.__abstractmethods__
print(f"PartitionerBase 的抽象方法: {abstract_methods}")

# 检查已实现类
from core import IIDPartitioner
print(f"IIDPartitioner 仍需实现的抽象方法: {IIDPartitioner.__abstractmethods__}")
```

### 验证子类实现

```python
from datasets.mnist import MNISTRawDataset

# 检查是否实现了所有抽象方法
assert hasattr(MNISTRawDataset, 'download')
assert hasattr(MNISTRawDataset, 'load_train_data')
assert hasattr(MNISTRawDataset, 'load_test_data')

# 测试实例化
raw = MNISTRawDataset(data_root="./data")
print(f"数据集名称: {raw.name}")
print(f"类别数: {raw.num_classes}")
```

### 测试划分器

```python
from core import DirichletPartitioner
from torch.utils.data import TensorDataset
import torch

# 创建测试数据集
data = torch.randn(1000, 10)
labels = torch.randint(0, 10, (1000,))
dataset = TensorDataset(data, labels)

# 创建划分器
partitioner = DirichletPartitioner(num_clients=10, alpha=0.5, seed=42)
client_indices = partitioner.partition(dataset)

# 验证划分结果
print(f"客户端数量: {len(client_indices)}")
print(f"总样本数: {sum(len(indices) for indices in client_indices.values())}")

# 获取统计信息
stats = partitioner.get_statistics(dataset, client_indices)
print(f"不平衡比例: {stats['statistics']['imbalance_ratio']}")
```

## 📚 相关文档

- [../README.md](../README.md) - 项目总览
- [../AGENTS.md](../AGENTS.md) - 项目 AI Agent 指引
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - 架构设计文档
- [./README.md](./README.md) - Core 模块文档
- [../database/AGENTS.md](../database/AGENTS.md) - Database 模块指引
