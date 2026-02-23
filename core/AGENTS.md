# Core 模块 - AI Agent 指引

> 为 AI Agent 提供的 Core 模块开发和维护指南

## 🎯 模块定位

Core 模块是整个框架的**基石**，定义了所有数据集组件的契约（Contract）。修改此模块会影响整个框架，需要特别谨慎。

## 📁 文件职责

| 文件 | 职责 | 修改风险 |
|------|------|----------|
| `raw_dataset_base.py` | 定义原始数据集接口 | ⭐⭐⭐⭐⭐ 高 |
| `preprocessor_base.py` | 定义预处理器接口 | ⭐⭐⭐⭐ 中高 |
| `partitioner_base.py` | 定义划分器接口 | ⭐⭐⭐⭐ 中高 |
| `dataset_manager_base.py` | 定义管理器接口 | ⭐⭐⭐⭐⭐ 高 |
| `__init__.py` | 统一导出接口 | ⭐⭐ 低 |

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
1. 在 `partitioner_base.py` 中创建新的划分器基类
2. 继承 `PartitionerBase`
3. 定义策略特定的参数
4. 在 `__init__.py` 中导出

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

### 任务4: 修复接口兼容性问题

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
```

## 🚨 重要约束

### 1. 抽象方法必须实现

所有标记为 `@abstractmethod` 的方法必须在子类中实现，否则子类也无法实例化。

```python
# ❌ 错误：子类没有实现抽象方法
class BadPartitioner(IIDPartitioner):
    pass  # 缺少 partition 方法的实现

# 这会抛出 TypeError
partitioner = BadPartitioner(num_clients=10)
```

### 2. 保持接口稳定性

Core 模块的接口应该保持**向后兼容**:

- **可以添加**: 新的可选方法、新的带默认值的参数
- **谨慎修改**: 现有方法的签名
- **避免删除**: 任何已存在的方法或属性

### 3. 类型注解必须准确

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
    │       ↑
    │       └── 被 datasets/*/preprocess.py 继承
    │
    ├── partitioner_base.py
    │       ↑
    │       └── 被 datasets/*/partition.py 继承
    │
    └── dataset_manager_base.py
            ↑
            └── 被 database/dynamic_importer.py 引用
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
```

### 验证子类实现

```python
from datasets.mnist import MNISTRawDataset

# 检查是否实现了所有抽象方法
assert hasattr(MNISTRawDataset, 'download')
assert hasattr(MNISTRawDataset, 'load_train_data')
assert hasattr(MNISTRawDataset, 'load_test_data')
```

## 📚 相关文档

- [../README.md](../README.md) - 项目总览
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - 架构设计文档
- [../database/AGENTS.md](../database/AGENTS.md) - Database 模块指引
