# Datasets 模块

> 联邦学习数据集管理框架的数据集实现模块

## 概述

Datasets 模块包含所有具体数据集的实现。每个数据集都是一个独立的子包，包含原始数据加载、预处理和联邦划分的完整实现。

## 模块结构

```
datasets/
├── __init__.py              # 导出所有数据集组件
│
├── mnist/                   # MNIST 数据集
│   ├── __init__.py          # 导出 MNIST 组件
│   ├── raw.py               # MNISTRawDataset
│   ├── preprocess.py        # MNISTPreprocessor
│   └── partition.py         # MNISTPartitioner
│
├── cifar10/                 # CIFAR-10 数据集
│   ├── __init__.py          # 导出 CIFAR-10 组件
│   ├── raw.py               # CIFAR10RawDataset
│   ├── preprocess.py        # CIFAR10Preprocessor
│   └── partition.py         # CIFAR10Partitioner
│
├── fashion_mnist/           # Fashion-MNIST 数据集
│   ├── __init__.py          # 导出 Fashion-MNIST 组件
│   ├── raw.py               # FashionMNISTRawDataset
│   ├── preprocess.py        # FashionMNISTPreprocessor
│   └── partition.py         # FashionMNISTPartitioner
│
└── femnist/                 # FEMNIST 数据集
    ├── __init__.py          # 导出 FEMNIST 组件
    ├── raw.py               # FEMNISTRawDataset
    ├── preprocess.py        # FEMNISTPreprocessor
    └── partition.py         # FEMNISTPartitioner
```

## 每个数据集的标准结构

每个数据集子包必须包含以下三个文件：

```
datasets/{dataset_name}/
├── __init__.py          # 导出所有组件
├── raw.py               # 原始数据集实现
├── preprocess.py        # 预处理器实现
└── partition.py         # 划分器实现
```

### __init__.py

导出数据集的所有组件：
- `RawDataset`: 原始数据集类
- `Preprocessor`: 预处理器类
- `Partitioner`: 划分器工厂类
- 具体划分器类（IID/Dirichlet/Pathological）

### raw.py

实现原始数据集类，继承 `core.RawDatasetBase`：
- 实现数据下载逻辑
- 加载训练和测试数据
- 提供数据集元信息

### preprocess.py

实现预处理器类，继承 `core.PreprocessorBase`：
- 定义数据预处理流程
- 实现数据增强（训练时）
- 提供归一化/标准化参数

### partition.py

实现划分器类，继承 `core.PartitionerBase` 的子类：
- `Partitioner`: 工厂类，根据策略创建划分器
- `IIDPartitioner`: IID 划分实现
- `DirichletPartitioner`: Dirichlet Non-IID 划分实现
- `PathologicalPartitioner`: Pathological Non-IID 划分实现

## 现有数据集

### 1. MNIST

**描述**: 手写数字识别数据集

**基本信息**:
- 类别数: 10 (0-9)
- 训练样本: 60,000
- 测试样本: 10,000
- 图像尺寸: 28×28 灰度
- 输入形状: (1, 28, 28)

**预处理器**:
- 均值: [0.1307]
- 标准差: [0.3081]
- 支持随机旋转和平移增强

**使用示例**:
```python
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor, MNISTPartitioner

# 加载数据
raw = MNISTRawDataset(data_root="./data")
raw.download()

# 预处理
preprocessor = MNISTPreprocessor()
train_transform = preprocessor.get_train_transform()

# 划分
partitioner = MNISTPartitioner.create("dirichlet", num_clients=10, alpha=0.5)
client_indices = partitioner.partition(raw.load_train_data())
```

### 2. CIFAR-10

**描述**: 10 类彩色图像分类数据集

**基本信息**:
- 类别数: 10
  - airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck
- 训练样本: 50,000
- 测试样本: 10,000
- 图像尺寸: 32×32 彩色
- 输入形状: (3, 32, 32)

**预处理器**:
- 均值: [0.4914, 0.4822, 0.4465]
- 标准差: [0.2470, 0.2435, 0.2616]
- 支持随机裁剪、翻转等增强

**使用示例**:
```python
from datasets.cifar10 import (
    CIFAR10RawDataset,
    CIFAR10Preprocessor,
    CIFAR10Partitioner
)

raw = CIFAR10RawDataset(data_root="./data")
raw.download()

preprocessor = CIFAR10Preprocessor()
partitioner = CIFAR10Partitioner.create("iid", num_clients=10)
```

### 3. Fashion-MNIST

**描述**: 时尚物品分类数据集（MNIST 的替代）

**基本信息**:
- 类别数: 10
  - T-shirt/top, Trouser, Pullover, Dress, Coat, Sandal, Shirt, Sneaker, Bag, Ankle boot
- 训练样本: 60,000
- 测试样本: 10,000
- 图像尺寸: 28×28 灰度
- 输入形状: (1, 28, 28)

**预处理器**:
- 均值: [0.2860]
- 标准差: [0.3530]

**使用示例**:
```python
from datasets.fashion_mnist import (
    FashionMNISTRawDataset,
    FashionMNISTPreprocessor,
    FashionMNISTPartitioner
)

raw = FashionMNISTRawDataset(data_root="./data")
preprocessor = FashionMNISTPreprocessor()
partitioner = FashionMNISTPartitioner.create("dirichlet", num_clients=10, alpha=0.5)
```

### 4. FEMNIST

**描述**: 联邦学习扩展 MNIST（Federated Extended MNIST）

**基本信息**:
- 类别数: 62
  - 10 个数字 (0-9)
  - 26 个大写字母 (A-Z)
  - 26 个小写字母 (a-z)
- 训练样本: 697,932
- 测试样本: 116,323
- 图像尺寸: 28×28 灰度
- 输入形状: (1, 28, 28)

**预处理器**:
- 均值: [0.1733]
- 标准差: [0.3310]

**使用示例**:
```python
from datasets.femnist import (
    FEMNISTRawDataset,
    FEMNISTPreprocessor,
    FEMNISTPartitioner,
    FEMNISTFederatedManager
)

# 方式1: 使用联邦管理器（推荐）
manager = FEMNISTFederatedManager(
    data_root="./data",
    num_clients=100,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.1},
    seed=42
)
manager.prepare_data()

# 方式2: 使用组件
raw = FEMNISTRawDataset(data_root="./data")
raw.download()
preprocessor = FEMNISTPreprocessor()
partitioner = FEMNISTPartitioner.create("dirichlet", num_clients=100, alpha=0.1)
```

**适用场景**:
- 大规模联邦学习实验（支持更多客户端）
- 需要更多类别（62类）的分类任务
- 研究字母数字混合识别

## 快速对比

| 数据集 | 类别数 | 训练样本 | 测试样本 | 图像尺寸 | 通道数 |
|--------|--------|----------|----------|----------|--------|
| MNIST | 10 | 60,000 | 10,000 | 28×28 | 1 |
| CIFAR-10 | 10 | 50,000 | 10,000 | 32×32 | 3 |
| Fashion-MNIST | 10 | 60,000 | 10,000 | 28×28 | 1 |
| FEMNIST | 62 | 697,932 | 116,323 | 28×28 | 1 |

## 统一使用方式

### 方式1: 直接导入具体数据集

```python
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor, MNISTPartitioner
from datasets.cifar10 import CIFAR10RawDataset, CIFAR10Preprocessor, CIFAR10Partitioner
```

### 方式2: 通过工厂动态创建

```python
from database import DatasetFactory

factory = DatasetFactory(registry)
manager = factory.create("mnist", data_root="./data", num_clients=10)
```

### 方式3: 从 datasets 包导入

```python
from datasets import MNISTRawDataset, CIFAR10RawDataset

# 获取数据集列表
from datasets import list_available_datasets
print(list_available_datasets())  # ['mnist', 'cifar10', 'fashion_mnist', 'femnist']
```

## 添加新数据集

参见 [ARCHITECTURE.md](../ARCHITECTURE.md#添加新数据集的步骤) 获取详细步骤。

简要流程：
1. 创建目录 `datasets/my_dataset/`
2. 实现 `raw.py`（继承 `RawDatasetBase`）
3. 实现 `preprocess.py`（继承 `PreprocessorBase`）
4. 实现 `partition.py`（继承划分器基类）
5. 创建 `__init__.py` 导出组件
6. 在 `configs/default_configs.py` 添加配置
7. 注册到数据库（可选）

## 注意事项

1. **统计量准确性**: 预处理器的均值/标准差必须与实际数据匹配
2. **下载可靠性**: 原始数据集下载应使用稳定的源（如 torchvision）
3. **划分可复现**: 划分器应使用随机种子保证结果可复现
4. **内存效率**: 大数据集应考虑内存效率，使用懒加载
