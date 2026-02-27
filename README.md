# 联邦学习数据集管理框架

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.10+-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 一个专为联邦学习设计的灵活、可扩展的数据集管理框架，支持多种数据集、预处理方式和联邦划分策略。

## 🌟 特性

- **模块化设计**: 遵循单一职责原则，将数据加载、预处理、划分逻辑分离
- **多数据集支持**: 内置 MNIST、CIFAR-10、Fashion-MNIST 等经典数据集
- **灵活的数据划分**: 支持 IID、Dirichlet 分布、Pathological 等多种 Non-IID 划分策略
- **动态导入**: 基于数据库的模块动态导入系统，支持运行时数据集发现和加载
- **统一接口**: 所有数据集遵循统一的基类接口，易于扩展新数据集
- **联邦学习优化**: 专为联邦学习场景设计，支持客户端数据管理和分布统计
- **懒加载模式**: `FederatedDatasetManager` 支持按需数据准备，提高启动速度
- **划分持久化**: 支持划分结果的保存和加载，确保实验可复现
- **完整的数据访问**: 同时支持客户端训练数据加载器和全局测试数据加载器

## 📁 项目结构

```
.
├── __init__.py                 # 包入口，导出主要API
├── README.md                   # 本文档
├── AGENTS.md                   # AI Agent 指引文档
├── ARCHITECTURE.md             # 架构设计文档
│
├── core/                       # 核心基类模块
│   ├── raw_dataset_base.py     # 原始数据集基类
│   ├── preprocessor_base.py    # 预处理器基类
│   ├── partitioner_base.py     # 划分器基类（含 IID/Dirichlet/Pathological 实现）
│   └── dataset_manager_base.py # 管理器基类（含 FederatedDatasetManager 实现）
│
├── database/                   # 数据库模块
│   ├── models.py               # 数据模型定义
│   ├── dataset_registry.py     # 数据集注册中心
│   └── dynamic_importer.py     # 动态导入器
│
├── datasets/                   # 数据集实现模块
│   ├── mnist/                  # MNIST数据集
│   ├── cifar10/                # CIFAR-10数据集
│   ├── fashion_mnist/          # Fashion-MNIST数据集
│   └── __init__.py             # 导出数据集类和辅助函数
│
├── configs/                    # 配置模块
│   └── default_configs.py      # 默认配置
│
└── utils/                      # 工具模块
    └── helpers.py              # 辅助函数
```

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd dataset

# 安装依赖
pip install -r requirements.txt  # 或使用 pipenv
pipenv install
```

### 基本使用

#### 方式1：直接使用具体数据集

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

#### 方式2：使用 FederatedDatasetManager（推荐）

```python
from core import FederatedDatasetManager
from datasets.mnist import MNISTRawDataset, MNISTPreprocessor, MNISTPartitioner

# 定义管理器
class MNISTFederatedManager(FederatedDatasetManager):
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

# 获取客户端数据加载器（用于训练）
loader = manager.get_client_loader(0, batch_size=32)

# 获取测试数据加载器（用于全局评估）
test_loader = manager.get_test_loader(batch_size=256)

# 获取划分统计信息
partition_info = manager.get_partition_info()
print(partition_info["statistics"])

# 保存划分结果
manager.save_split("./splits/mnist_split.json")

# 加载划分结果
manager.load_split("./splits/mnist_split.json")
```

#### 方式3：通过工厂动态创建

```python
from database import DatasetFactory, DatasetRegistry

# 初始化注册中心
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

#### 方式4：使用数据集工具函数

```python
from datasets import (
    list_available_datasets,
    get_dataset_info,
    get_raw_dataset_class,
    get_preprocessor_class,
    get_partitioner_class,
)

# 列出所有可用数据集
datasets = list_available_datasets()
print(datasets)  # ['mnist', 'cifar10', 'fashion_mnist']

# 获取数据集信息
info = get_dataset_info("mnist")
print(info["num_classes"])      # 10
print(info["train_samples"])    # 60000
print(info["input_shape"])      # (1, 28, 28)

# 获取数据集类
RawDatasetClass = get_raw_dataset_class("mnist")
PreprocessorClass = get_preprocessor_class("mnist")
PartitionerClass = get_partitioner_class("mnist")
```

## 📊 支持的数据集

| 数据集 | 类别数 | 训练样本 | 测试样本 | 输入尺寸 | 数据类型 |
|--------|--------|----------|----------|----------|----------|
| MNIST | 10 | 60,000 | 10,000 | 1×28×28 | 图像 |
| CIFAR-10 | 10 | 50,000 | 10,000 | 3×32×32 | 图像 |
| Fashion-MNIST | 10 | 60,000 | 10,000 | 1×28×28 | 图像 |

## 🔀 支持的划分策略

| 策略 | 类型 | 描述 | 关键参数 |
|------|------|------|----------|
| **IID** | IID | 随机打乱后均匀分配 | 无 |
| **Dirichlet** | Non-IID | 基于 Dirichlet 分布的类别偏斜划分 | `alpha`: 浓度参数，越小越 Non-IID |
| **Pathological** | Non-IID | 按类别排序后分片，每个客户端获得特定数量的类别 | `shards_per_client`: 每个客户端的类别数 |

### 划分策略使用示例

```python
from core import IIDPartitioner, DirichletPartitioner, PathologicalPartitioner

# IID 划分
iid_partitioner = IIDPartitioner(num_clients=10, seed=42)
client_indices = iid_partitioner.partition(dataset)

# Dirichlet 划分 (alpha=0.5 会产生较明显的 Non-IID)
dirichlet_partitioner = DirichletPartitioner(num_clients=10, alpha=0.5, seed=42)
client_indices = dirichlet_partitioner.partition(dataset)

# Pathological 划分 (每个客户端获得 2 个类别)
pathological_partitioner = PathologicalPartitioner(num_clients=10, shards_per_client=2, seed=42)
client_indices = pathological_partitioner.partition(dataset)

# 获取划分统计信息
stats = dirichlet_partitioner.get_statistics(dataset, client_indices)
print(stats["samples_per_client"])  # 每个客户端的样本数
print(stats["distribution"])        # 每个客户端的类别分布
print(stats["statistics"])          # 详细统计信息（均值、标准差、不平衡比例等）

# 保存划分结果
dirichlet_partitioner.save_partition(client_indices, "./split.json")

# 加载划分结果
loaded_indices = dirichlet_partitioner.load_partition("./split.json")
```

## 🏗️ 架构设计

本框架遵循以下设计原则：

1. **单一职责原则 (SRP)**: 每个类只负责一个功能领域
2. **开闭原则 (OCP)**: 易于扩展新数据集，无需修改现有代码
3. **依赖倒置原则 (DIP)**: 高层模块依赖抽象基类，而非具体实现

详细架构说明请参见 [ARCHITECTURE.md](./ARCHITECTURE.md)。

## 🧩 添加新数据集

添加新数据集只需以下步骤：

1. 创建数据集目录：`mkdir datasets/my_dataset`
2. 实现原始数据集类（继承 `RawDatasetBase`）
   - 实现 `num_classes`, `num_features`, `input_shape`, `train_samples`, `test_samples` 属性
   - 实现 `download()`, `load_train_data()`, `load_test_data()` 方法
3. 实现预处理器类（继承 `PreprocessorBase`）
   - 实现 `fit()`, `get_train_transform()`, `get_test_transform()` 方法
4. 实现划分器类（继承 `IIDPartitioner`、`DirichletPartitioner` 或 `PathologicalPartitioner`）
   - 重写 `name` 属性
5. 在 `__init__.py` 中导出组件
6. 在 `configs/default_configs.py` 中添加配置
7. 注册到数据库（可选）

详细步骤请参见 [AGENTS.md#添加新数据集](./AGENTS.md#任务1-添加新数据集)。

## 📖 文档

- [AGENTS.md](./AGENTS.md) - AI Agent 指引文档
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 详细架构设计文档
- [core/README.md](./core/README.md) - 核心基类模块文档
- [core/AGENTS.md](./core/AGENTS.md) - Core 模块 AI Agent 指引
- [database/README.md](./database/README.md) - 数据库模块文档
- [database/AGENTS.md](./database/AGENTS.md) - Database 模块 AI Agent 指引
- [datasets/README.md](./datasets/README.md) - 数据集模块文档
- [datasets/AGENTS.md](./datasets/AGENTS.md) - Datasets 模块 AI Agent 指引
- [configs/README.md](./configs/README.md) - 配置模块文档
- [configs/AGENTS.md](./configs/AGENTS.md) - Configs 模块 AI Agent 指引
- [utils/README.md](./utils/README.md) - 工具模块文档
- [utils/AGENTS.md](./utils/AGENTS.md) - Utils 模块 AI Agent 指引

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢 PyTorch 团队提供优秀的深度学习框架
- 感谢联邦学习社区的开源贡献
