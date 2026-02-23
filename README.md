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

## 📁 项目结构

```
.
├── __init__.py                 # 包入口，导出主要API
├── README.md                   # 本文档
├── ARCHITECTURE.md             # 架构设计文档
│
├── core/                       # 核心基类模块
│   ├── raw_dataset_base.py     # 原始数据集基类
│   ├── preprocessor_base.py    # 预处理器基类
│   ├── partitioner_base.py     # 划分器基类
│   └── dataset_manager_base.py # 管理器基类
│
├── database/                   # 数据库模块
│   ├── models.py               # 数据模型定义
│   ├── dataset_registry.py     # 数据集注册中心
│   └── dynamic_importer.py     # 动态导入器
│
├── datasets/                   # 数据集实现模块
│   ├── mnist/                  # MNIST数据集
│   ├── cifar10/                # CIFAR-10数据集
│   └── fashion_mnist/          # Fashion-MNIST数据集
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

#### 方式2：通过工厂动态创建（推荐）

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

## 📊 支持的数据集

| 数据集 | 类别数 | 训练样本 | 测试样本 | 输入尺寸 |
|--------|--------|----------|----------|----------|
| MNIST | 10 | 60,000 | 10,000 | 1×28×28 |
| CIFAR-10 | 10 | 50,000 | 10,000 | 3×32×32 |
| Fashion-MNIST | 10 | 60,000 | 10,000 | 1×28×28 |

## 🔀 支持的划分策略

| 策略 | 类型 | 描述 | 关键参数 |
|------|------|------|----------|
| **IID** | IID | 独立同分布随机划分 | 无 |
| **Dirichlet** | Non-IID | 基于 Dirichlet 分布的划分 | `alpha`: 浓度参数，越小越 Non-IID |
| **Pathological** | Non-IID | 每个客户端只获得特定类别 | `shards_per_client`: 每个客户端的类别数 |

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
3. 实现预处理器类（继承 `PreprocessorBase`）
4. 实现划分器类（继承 `PartitionerBase`）
5. 在 `__init__.py` 中导出组件
6. 注册到数据库

详细步骤请参见 [ARCHITECTURE.md#添加新数据集的步骤](./ARCHITECTURE.md#添加新数据集的步骤)。

## 📖 文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 详细架构设计文档
- [core/README.md](./core/README.md) - 核心基类模块文档
- [database/README.md](./database/README.md) - 数据库模块文档
- [datasets/README.md](./datasets/README.md) - 数据集模块文档
- [configs/README.md](./configs/README.md) - 配置模块文档
- [utils/README.md](./utils/README.md) - 工具模块文档

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
