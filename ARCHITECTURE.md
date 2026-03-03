# 联邦学习数据集管理框架 - 架构文档

## 架构概览

```
project/
├── __init__.py                      # 包入口，导出主要API
├── ARCHITECTURE.md                  # 本文档
│
├── core/                            # 核心基类模块
│   ├── __init__.py                  # 导出所有基类
│   ├── raw_dataset_base.py          # 原始数据集基类 (RawDatasetBase)
│   ├── preprocessor_base.py         # 预处理器基类 (PreprocessorBase)
│   ├── partitioner_base.py          # 划分器基类 (PartitionerBase)
│   └── dataset_manager_base.py      # 数据集管理器基类 (DatasetManagerBase)
│
├── database/                        # 数据库模块
│   ├── __init__.py                  # 导出数据库相关类
│   ├── models.py                    # 数据模型 (DatasetRegistration, PartitionStrategy)
│   ├── dataset_registry.py          # 数据集注册中心 (DatasetRegistry)
│   └── dynamic_importer.py          # 动态导入模块 (DynamicImporter, DatasetFactory)
│
├── datasets/                        # 数据集实现模块
│   ├── __init__.py                  # 导出所有数据集
│   │
│   ├── mnist/                       # MNIST数据集
│   │   ├── __init__.py              # 导出MNIST组件
│   │   ├── raw.py                   # MNIST原始数据集 (MNISTRawDataset)
│   │   ├── preprocess.py            # MNIST预处理器 (MNISTPreprocessor)
│   │   └── partition.py             # MNIST划分器 (MNISTPartitioner)
│   │
│   ├── cifar10/                     # CIFAR-10数据集
│   │   ├── __init__.py              # 导出CIFAR-10组件
│   │   ├── raw.py                   # CIFAR-10原始数据集 (CIFAR10RawDataset)
│   │   ├── preprocess.py            # CIFAR-10预处理器 (CIFAR10Preprocessor)
│   │   └── partition.py             # CIFAR-10划分器 (CIFAR10Partitioner)
│   │
│   └── fashion_mnist/               # Fashion-MNIST数据集
│       ├── __init__.py              # 导出Fashion-MNIST组件
│       ├── raw.py                   # Fashion-MNIST原始数据集 (FashionMNISTRawDataset)
│       ├── preprocess.py            # Fashion-MNIST预处理器 (FashionMNISTPreprocessor)
│       └── partition.py             # Fashion-MNIST划分器 (FashionMNISTPartitioner)
│
├── configs/                         # 配置模块
│   ├── __init__.py                  # 导出配置相关
│   └── default_configs.py           # 默认配置 (DatasetConfig, DEFAULT_DATASET_CONFIGS)
│
└── utils/                           # 工具模块
    ├── __init__.py                  # 导出工具函数
    └── helpers.py                   # 辅助函数 (set_seed, get_device, etc.)
```

## 核心设计原则

### 1. 单一职责原则 (SRP)

每个类只负责一个功能：
- **RawDatasetBase**: 只负责原始数据的下载和加载
- **PreprocessorBase**: 只负责数据预处理（归一化、增强等）
- **PartitionerBase**: 只负责数据划分（IID/Non-IID）
- **DatasetManagerBase**: 协调上述三个组件

### 2. 每个数据集独立实现

每个数据集（如MNIST、CIFAR-10）都有自己的：
- 原始数据集类（继承RawDatasetBase）
- 预处理器类（继承PreprocessorBase）
- 划分器类（继承PartitionerBase）

这样设计的好处：
- 数据集之间完全解耦
- 易于添加新数据集
- 支持数据集特定的优化

### 3. 数据库支持动态导入

数据库表`dataset_registrations`记录每个数据集的：
- 模块路径（如 `datasets.mnist.raw`）
- 类名（如 `MNISTRawDataset`）

通过 `DynamicImporter` 实现：
```python
# 根据数据库记录动态导入
importer = DynamicImporter()
raw_dataset_class = importer.import_class(
    module_path="datasets.mnist.raw",
    class_name="MNISTRawDataset"
)
```

## 模块详细说明

### core/ 核心基类模块

#### raw_dataset_base.py
- `RawDatasetBase`: 抽象基类，定义原始数据集的接口
  - `download()`: 下载数据
  - `load_train_data()`: 加载训练集
  - `load_test_data()`: 加载测试集
  - 属性: `num_classes`, `num_features`, `input_shape`

#### preprocessor_base.py
- `PreprocessorBase`: 抽象基类，定义预处理器接口
  - `fit()`: 根据数据拟合参数
  - `get_train_transform()`: 获取训练变换
  - `get_test_transform()`: 获取测试变换
  - `inverse_transform()`: 反变换

#### partitioner_base.py
- `PartitionerBase`: 抽象基类，定义划分器接口
  - `partition()`: 执行划分，返回 `{client_id: [indices]}`
  - `get_distribution()`: 获取分布信息
  - 子类: `IIDPartitioner`, `DirichletPartitioner`, `PathologicalPartitioner`

#### dataset_manager_base.py
- `DatasetManagerBase`: 抽象基类，定义管理器接口
  - `prepare_data()`: 准备数据（下载->预处理->划分）
  - `get_client_loader()`: 获取客户端数据加载器
  - 属性: `raw_dataset_class`, `preprocessor_class`, `partitioner_class`

### database/ 数据库模块

#### models.py
- `DatasetRegistration`: 数据集注册信息数据类
  - 基本信息：name, display_name, description
  - 数据特性：num_classes, input_shape, data_type
  - **模块路径**：raw_dataset_module, preprocessor_module, partitioner_module
  - **类名**：raw_dataset_class, preprocessor_class, partitioner_class

#### dataset_registry.py
- `DatasetRegistry`: 数据集注册中心（单例模式）
  - `register()`: 注册数据集
  - `get()`: 获取注册信息
  - `list_datasets()`: 列出所有数据集

#### dynamic_importer.py
- `DynamicImporter`: 动态导入器
  - `import_class()`: 根据模块路径和类名动态导入
  - `create_raw_dataset()`: 创建原始数据集实例
  - `create_preprocessor()`: 创建预处理器实例
  - `create_partitioner()`: 创建划分器实例
- `DatasetFactory`: 数据集工厂
  - `create()`: 通过数据集名称创建完整的管理器

### datasets/ 数据集实现模块

每个数据集的模块结构相同，以MNIST为例：

#### mnist/raw.py
- `MNISTRawDataset(RawDatasetBase)`: MNIST原始数据集
  - 实现MNIST特定的下载和加载逻辑
  - 定义MNIST的常量（10类，28x28图像等）

#### mnist/preprocess.py
- `MNISTPreprocessor(PreprocessorBase)`: MNIST预处理器
  - 使用MNIST特定的统计量（mean=0.1307, std=0.3081）
  - 实现MNIST特定的数据增强

#### mnist/partition.py
- `MNISTPartitioner`: 工厂类，创建MNIST划分器
- `MNISTIIDPartitioner(IIDPartitioner)`: MNIST的IID划分
- `MNISTDirichletPartitioner(DirichletPartitioner)`: MNIST的Dirichlet划分
- `MNISTPathologicalPartitioner(PathologicalPartitioner)`: MNIST的病态划分

## 使用示例

### 方式1：直接使用具体数据集

```python
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor, MNISTPartitioner

# 创建原始数据集
raw_dataset = MNISTRawDataset(data_root="./data")
raw_dataset.download()

# 创建预处理器
preprocessor = MNISTPreprocessor()
train_transform = preprocessor.get_train_transform()

# 创建划分器
partitioner = MNISTPartitioner.create(
    strategy="dirichlet",
    num_clients=10,
    alpha=0.5
)
client_indices = partitioner.partition(raw_dataset.load_train_data())
```

### 方式2：通过工厂动态创建

```python
from database import DatasetFactory, DatasetRegistry

# 初始化注册中心（从数据库加载）
registry = DatasetRegistry()
registry.load_from_database()

# 使用工厂创建管理器
factory = DatasetFactory(registry)
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)

# 准备数据
manager.prepare_data()

# 获取客户端数据加载器
loader = manager.get_client_loader(0, batch_size=32)
```

### 方式3：使用便捷函数创建管理器

```python
from datasets import create_federated_manager

# 通过名称快速创建管理器
manager = create_federated_manager(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    seed=42
)
manager.prepare_data()
```

### 方式4：直接实例化具体管理器

```python
# 每个数据集都有完整的FederatedManager实现
from datasets.mnist import MNISTFederatedManager

manager = MNISTFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    seed=42
)
manager.prepare_data()

# 可视化客户端分布
manager.visualize_client_distribution(
    title="MNIST Client Distribution",
    save_path="./results/mnist_dist.png"
)
```

## 添加新数据集的步骤

1. **创建数据集目录**
   ```bash
   mkdir datasets/my_dataset
   touch datasets/my_dataset/__init__.py
   ```

2. **实现原始数据集类** (`raw.py`)
   ```python
   from core import RawDatasetBase
   
   class MyDatasetRawDataset(RawDatasetBase):
       @property
       def num_classes(self) -> int:
           return 10
       # ... 实现其他方法
   ```

3. **实现预处理器类** (`preprocess.py`)
   ```python
   from core import PreprocessorBase
   
   class MyDatasetPreprocessor(PreprocessorBase):
       def get_train_transform(self):
           # ... 实现训练变换
   ```

4. **实现划分器类** (`partition.py`)
   ```python
   from core import IIDPartitioner
   
   class MyDatasetIIDPartitioner(IIDPartitioner):
       # ... 实现划分逻辑
   ```

5. **在 `__init__.py` 中导出**
   ```python
   from .raw import MyDatasetRawDataset
   from .preprocess import MyDatasetPreprocessor
   from .partition import MyDatasetPartitioner
   ```

6. **注册到数据库**
   ```python
   from database import DatasetRegistration, DatasetRegistry
   
   registration = DatasetRegistration(
       name="my_dataset",
       raw_dataset_module="datasets.my_dataset.raw",
       raw_dataset_class="MyDatasetRawDataset",
       # ... 其他信息
   )
   
   registry = DatasetRegistry()
   registry.register(registration)
   ```

## 扩展功能

- [x] 支持更多数据集（FEMNIST已添加）
- [ ] 支持文本数据集
- [ ] 支持音频数据集
- [x] 实现具体的数据集管理器类（FederatedDatasetManager）
- [x] 添加可视化工具（visualize_client_distribution）
- [x] 添加数据统计分析工具（get_partition_info, get_statistics）

## 特性说明

### 懒加载模式
`FederatedDatasetManager` 支持懒加载，首次调用数据访问方法时才真正准备数据，提高启动速度。

### 划分结果持久化
支持划分结果的保存和加载，确保实验可复现：
```python
manager.save_split("./splits/mnist_split.json")
manager.load_split("./splits/mnist_split.json")
```

### 客户端分布可视化
```python
manager.visualize_client_distribution(
    title="Client Distribution",
    save_path="./results/dist.png",  # None则直接显示
    figsize=(12, 5),
    max_clients=10,
    max_classes=10
)
```
