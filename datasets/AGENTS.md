# Datasets 模块 - AI Agent 指引

> 为 AI Agent 提供的数据集实现开发和维护指南

## 🎯 模块定位

Datasets 模块是框架的**数据集实现层**，包含所有具体数据集的完整实现。每个数据集都是独立的子包，遵循统一的结构规范。

## 📁 目录结构标准

每个数据集子包**必须**遵循以下结构：

```
datasets/{dataset_name}/
├── __init__.py          # 导出组件
├── raw.py               # 原始数据集
├── preprocess.py        # 预处理器
└── partition.py         # 划分器
```

### 文件命名规范

| 文件 | 类名格式 | 示例 |
|------|----------|------|
| `raw.py` | `{DatasetName}RawDataset` | `MNISTRawDataset` |
| `preprocess.py` | `{DatasetName}Preprocessor` | `MNISTPreprocessor` |
| `partition.py` | `{DatasetName}Partitioner` | `MNISTPartitioner` |

### 划分器类命名

| 划分策略 | 类名格式 | 示例 |
|----------|----------|------|
| 工厂类 | `{DatasetName}Partitioner` | `MNISTPartitioner` |
| IID | `{DatasetName}IIDPartitioner` | `MNISTIIDPartitioner` |
| Dirichlet | `{DatasetName}DirichletPartitioner` | `MNISTDirichletPartitioner` |
| Pathological | `{DatasetName}PathologicalPartitioner` | `MNISTPathologicalPartitioner` |

## 🔧 常见任务

### 任务1: 添加全新的数据集

**步骤详解**:

#### Step 1: 创建目录结构

```bash
mkdir -p datasets/my_dataset
touch datasets/my_dataset/__init__.py
touch datasets/my_dataset/raw.py
touch datasets/my_dataset/preprocess.py
touch datasets/my_dataset/partition.py
```

#### Step 2: 实现 raw.py

```python
"""
MyDataset 原始数据集模块
"""

from typing import List, Optional, Tuple
from torch.utils.data import Dataset
from torchvision import datasets as tv_datasets

from core import RawDatasetBase


class MyDatasetRawDataset(RawDatasetBase):
    """MyDataset 原始数据集"""
    
    # 数据集常量 - 根据实际情况修改
    NUM_CLASSES: int = 10
    NUM_FEATURES: int = 3072  # 3 * 32 * 32
    INPUT_SHAPE: Tuple[int, int, int] = (3, 32, 32)
    TRAIN_SAMPLES: int = 50000
    TEST_SAMPLES: int = 10000
    
    CLASS_NAMES: List[str] = ['class0', 'class1', ...]
    
    def __init__(self, data_root: str, download: bool = True, **kwargs) -> None:
        self.data_root = data_root
        self.download_flag = download
    
    @property
    def name(self) -> str:
        return "my_dataset"
    
    @property
    def num_classes(self) -> int:
        return self.NUM_CLASSES
    
    @property
    def num_features(self) -> int:
        return self.NUM_FEATURES
    
    @property
    def input_shape(self) -> Tuple[int, ...]:
        return self.INPUT_SHAPE
    
    @property
    def train_samples(self) -> int:
        return self.TRAIN_SAMPLES
    
    @property
    def test_samples(self) -> int:
        return self.TEST_SAMPLES
    
    def download(self) -> None:
        """下载数据 - 使用 torchvision 或自定义下载逻辑"""
        # 示例：使用 torchvision
        tv_datasets.MyDataset(
            root=self.data_root,
            train=True,
            download=self.download_flag
        )
    
    def load_train_data(self) -> Dataset:
        """加载训练集"""
        return tv_datasets.MyDataset(
            root=self.data_root,
            train=True,
            download=False,
            transform=None  # 原始数据，不加变换
        )
    
    def load_test_data(self) -> Dataset:
        """加载测试集"""
        return tv_datasets.MyDataset(
            root=self.data_root,
            train=False,
            download=False,
            transform=None
        )
    
    def get_class_names(self) -> List[str]:
        return self.CLASS_NAMES
```

#### Step 3: 实现 preprocess.py

```python
"""
MyDataset 预处理模块
"""

from typing import Any, Callable, Dict
import torch
from torch.utils.data import Dataset
from torchvision import transforms

from core import PreprocessorBase


class MyDatasetPreprocessor(PreprocessorBase):
    """MyDataset 预处理器"""
    
    # 根据实际数据计算或查找统计量
    MEAN: List[float] = [0.5, 0.5, 0.5]
    STD: List[float] = [0.5, 0.5, 0.5]
    
    def __init__(
        self,
        dataset_name: str = "my_dataset",
        augment: bool = True,
        **kwargs
    ) -> None:
        self.dataset_name = dataset_name
        self.augment = augment
    
    @property
    def name(self) -> str:
        return "my_dataset_preprocessor"
    
    def fit(self, dataset: Dataset) -> "MyDatasetPreprocessor":
        """
        拟合预处理器
        
        对于已知统计量的数据集，直接返回 self
        对于需要计算统计量的数据集，在此处计算
        """
        # 如需计算：
        # self.MEAN, self.STD = compute_mean_std(dataset)
        return self
    
    def get_train_transform(self) -> Callable:
        """训练数据变换"""
        transform_list = [transforms.ToTensor()]
        
        if self.augment:
            transform_list.extend([
                transforms.RandomCrop(32, padding=4),
                transforms.RandomHorizontalFlip(),
            ])
        
        transform_list.append(
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        )
        
        return transforms.Compose(transform_list)
    
    def get_test_transform(self) -> Callable:
        """测试数据变换"""
        return transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=self.MEAN, std=self.STD)
        ])
```

#### Step 4: 实现 partition.py

```python
"""
MyDataset 划分模块
"""

from typing import Dict, List
from torch.utils.data import Dataset

from core import IIDPartitioner, DirichletPartitioner, PathologicalPartitioner


class MyDatasetPartitioner:
    """MyDataset 划分器工厂"""
    
    @staticmethod
    def create(strategy: str, num_clients: int, seed: int = 42, **kwargs):
        """创建划分器"""
        if strategy == "iid":
            return MyDatasetIIDPartitioner(num_clients, seed)
        elif strategy == "dirichlet":
            alpha = kwargs.get("alpha", 0.5)
            return MyDatasetDirichletPartitioner(num_clients, alpha, seed)
        elif strategy == "pathological":
            shards = kwargs.get("shards_per_client", 2)
            return MyDatasetPathologicalPartitioner(num_clients, shards, seed)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


class MyDatasetIIDPartitioner(IIDPartitioner):
    """IID 划分"""
    
    def __init__(self, num_clients: int, seed: int = 42):
        super().__init__(num_clients, seed)
    
    @property
    def name(self) -> str:
        return "my_dataset_iid"
    
    @property
    def strategy_type(self) -> str:
        return "iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # 调用父类实现或自定义
        return super().partition(dataset)


class MyDatasetDirichletPartitioner(DirichletPartitioner):
    """Dirichlet Non-IID 划分"""
    
    def __init__(self, num_clients: int, alpha: float = 0.5, seed: int = 42):
        super().__init__(num_clients, alpha, seed)
    
    @property
    def name(self) -> str:
        return "my_dataset_dirichlet"
    
    @property
    def strategy_type(self) -> str:
        return "non-iid"


class MyDatasetPathologicalPartitioner(PathologicalPartitioner):
    """Pathological Non-IID 划分"""
    
    def __init__(self, num_clients: int, shards_per_client: int = 2, seed: int = 42):
        super().__init__(num_clients, shards_per_client, seed)
    
    @property
    def name(self) -> str:
        return "my_dataset_pathological"
    
    @property
    def strategy_type(self) -> str:
        return "non-iid"
```

#### Step 5: 创建 __init__.py

```python
"""
MyDataset 数据集模块
"""

from .raw import MyDatasetRawDataset
from .preprocess import MyDatasetPreprocessor
from .partition import (
    MyDatasetPartitioner,
    MyDatasetIIDPartitioner,
    MyDatasetDirichletPartitioner,
    MyDatasetPathologicalPartitioner,
)

__all__ = [
    "MyDatasetRawDataset",
    "MyDatasetPreprocessor",
    "MyDatasetPartitioner",
    "MyDatasetIIDPartitioner",
    "MyDatasetDirichletPartitioner",
    "MyDatasetPathologicalPartitioner",
]
```

#### Step 6: 添加到 configs

在 `configs/default_configs.py` 的 `DEFAULT_DATASET_CONFIGS` 中添加：

```python
"my_dataset": {
    "num_classes": 10,
    "num_features": 3072,
    "input_shape": (3, 32, 32),
    "train_samples": 50000,
    "test_samples": 10000,
    "data_type": "image",
    "task_type": "classification",
    "class_names": ['class0', 'class1', ...],
    "raw_dataset_module": "datasets.my_dataset.raw",
    "raw_dataset_class": "MyDatasetRawDataset",
    "preprocessor_module": "datasets.my_dataset.preprocess",
    "preprocessor_class": "MyDatasetPreprocessor",
    "partitioner_module": "datasets.my_dataset.partition",
    "partitioner_class": "MyDatasetPartitioner",
},
```

#### Step 7: 更新 datasets/__init__.py

```python
from .my_dataset import (
    MyDatasetRawDataset,
    MyDatasetPreprocessor,
    MyDatasetPartitioner,
    # ...
)

__all__ = [
    # ... 现有导出
    # MyDataset
    "MyDatasetRawDataset",
    "MyDatasetPreprocessor",
    "MyDatasetPartitioner",
    # ...
]
```

### 任务2: 修复数据加载问题

**症状**: 数据加载失败、返回 None 或形状不匹配

**检查清单**:
1. `raw.py` 中的路径是否正确
2. `download()` 是否成功执行
3. `load_train_data()` 返回的是否是 PyTorch Dataset
4. 数据形状是否符合 `input_shape` 声明

**调试代码**:
```python
from datasets.my_dataset import MyDatasetRawDataset

raw = MyDatasetRawDataset(data_root="./data")

# 测试下载
raw.download()

# 测试加载
train_data = raw.load_train_data()
print(f"Train data length: {len(train_data)}")
print(f"First sample shape: {train_data[0][0].shape}")
print(f"First label: {train_data[0][1]}")
```

### 任务3: 更新预处理参数

**场景**: 需要更新均值/标准差或其他预处理参数

**步骤**:
1. 更新 `preprocess.py` 中的常量
2. 更新 `configs/default_configs.py` 中的相关配置
3. 测试预处理后的数据范围是否正确

**验证代码**:
```python
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor

raw = MNISTRawDataset(data_root="./data")
preprocessor = MNISTPreprocessor()

# 获取变换
transform = preprocessor.get_train_transform()

# 测试变换
dataset = raw.load_train_data()
sample, label = dataset[0]
print(f"Original: min={sample.min()}, max={sample.max()}")

transformed = transform(sample)
print(f"Transformed: min={transformed.min()}, max={transformed.max()}")
```

### 任务4: 实现自定义划分策略

**场景**: 需要为特定数据集实现特殊的划分方式

**示例**:
```python
# datasets/my_dataset/partition.py

class MyDatasetCustomPartitioner(PartitionerBase):
    """自定义划分策略"""
    
    def __init__(self, num_clients: int, custom_param: float, seed: int = 42):
        super().__init__(num_clients, seed)
        self.custom_param = custom_param
    
    @property
    def name(self) -> str:
        return "my_dataset_custom"
    
    @property
    def strategy_type(self) -> str:
        return "non-iid"
    
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        # 实现自定义划分逻辑
        client_indices = {}
        # ... 划分代码
        return client_indices
```

## 🚨 重要约束

### 1. 必须实现所有抽象方法

每个继承的基类都有抽象方法，必须全部实现：

```python
# ✅ 正确
class MyDatasetRawDataset(RawDatasetBase):
    def download(self): ...
    def load_train_data(self): ...
    def load_test_data(self): ...
    # ... 所有抽象属性

# ❌ 错误 - 缺少抽象方法实现
class BadDatasetRawDataset(RawDatasetBase):
    def download(self): ...
    # 缺少 load_train_data 等方法
```

### 2. 数据类型一致性

```python
# ✅ 正确
@property
def input_shape(self) -> Tuple[int, ...]:
    return (3, 32, 32)  # 通道优先

# ❌ 错误
@property
def input_shape(self) -> Tuple[int, ...]:
    return (32, 32, 3)  # 通道最后，与 PyTorch 约定不符
```

### 3. 划分器随机种子

```python
# ✅ 正确 - 使用随机种子
class MyPartitioner(IIDPartitioner):
    def partition(self, dataset):
        np.random.seed(self.seed)  # 使用基类中的 seed
        # ... 划分逻辑

# ❌ 错误 - 未使用种子
class BadPartitioner(IIDPartitioner):
    def partition(self, dataset):
        indices = np.random.permutation(...)  # 结果不可复现
```

## 🔗 模块关系

```
datasets/
    ├── __init__.py (统一导出)
    │
    ├── mnist/
    │       ├── raw.py → 继承 core.RawDatasetBase
    │       ├── preprocess.py → 继承 core.PreprocessorBase
    │       └── partition.py → 继承 core.*Partitioner
    │
    ├── cifar10/
    │       └── ...
    │
    └── fashion_mnist/
            └── ...
```

## 📝 代码模板

### raw.py 模板

```python
"""
{DatasetName} 原始数据集模块
"""

from typing import List, Tuple
from torch.utils.data import Dataset
from torchvision import datasets as tv_datasets

from core import RawDatasetBase


class {DatasetName}RawDataset(RawDatasetBase):
    """{DatasetName} 原始数据集"""
    
    NUM_CLASSES: int = {num_classes}
    NUM_FEATURES: int = {num_features}
    INPUT_SHAPE: Tuple[int, ...] = {input_shape}
    TRAIN_SAMPLES: int = {train_samples}
    TEST_SAMPLES: int = {test_samples}
    
    CLASS_NAMES: List[str] = [{class_names}]
    
    def __init__(self, data_root: str, download: bool = True, **kwargs) -> None:
        self.data_root = data_root
        self.download_flag = download
    
    @property
    def name(self) -> str:
        return "{dataset_name_lower}"
    
    @property
    def num_classes(self) -> int:
        return self.NUM_CLASSES
    
    @property
    def num_features(self) -> int:
        return self.NUM_FEATURES
    
    @property
    def input_shape(self) -> Tuple[int, ...]:
        return self.INPUT_SHAPE
    
    @property
    def train_samples(self) -> int:
        return self.TRAIN_SAMPLES
    
    @property
    def test_samples(self) -> int:
        return self.TEST_SAMPLES
    
    def download(self) -> None:
        pass
    
    def load_train_data(self) -> Dataset:
        pass
    
    def load_test_data(self) -> Dataset:
        pass
    
    def get_class_names(self) -> List[str]:
        return self.CLASS_NAMES
```

## 📚 相关文档

- [../README.md](../README.md) - 项目总览
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - 架构设计
- [../core/AGENTS.md](../core/AGENTS.md) - Core 模块指引
- [../database/AGENTS.md](../database/AGENTS.md) - Database 模块指引
