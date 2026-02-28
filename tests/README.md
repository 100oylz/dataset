# 测试脚本说明

本目录包含联邦学习数据集管理框架的测试脚本。

## 测试脚本列表

### 1. test_download.py - 数据集下载测试

测试所有数据集是否能正确通过torchvision下载。

```bash
# 测试所有数据集
python tests/test_download.py

# 测试指定数据集
python tests/test_download.py --dataset mnist
python tests/test_download.py --dataset cifar10
python tests/test_download.py --dataset fashion_mnist

# 指定数据目录
python tests/test_download.py --data-root /path/to/data
```

### 2. test_datasets.py - 完整功能测试

使用unittest框架测试所有核心功能：
- 原始数据集（下载、加载、属性）
- 预处理器（拟合、变换、参数）
- 划分器（划分、统计、分布）
- 联邦学习管理器（准备数据、数据加载器、不同策略）
- 工具函数（获取Manager类、创建Manager实例）

```bash
# 运行所有测试
python tests/test_datasets.py

# 使用unittest直接运行
python -m unittest tests.test_datasets -v
```

### 3. example_usage.py - 使用示例

展示框架的各种使用方式：
- 使用 `create_federated_manager` 便捷函数
- 不同划分策略对比
- 所有数据集测试
- 直接导入Manager类

```bash
python tests/example_usage.py
```

## 快速开始

### 使用便捷函数创建Manager

```python
from datasets import create_federated_manager

# 创建MNIST联邦学习管理器
manager = create_federated_manager(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",  # iid, dirichlet, pathological
    partition_params={"alpha": 0.5},
    seed=42
)

# 准备数据（自动下载、预处理、划分）
manager.prepare_data()

# 获取客户端数据加载器
loader = manager.get_client_loader(client_id=0, batch_size=32)

# 获取测试数据加载器
test_loader = manager.get_test_loader(batch_size=256)

# 获取划分信息
info = manager.get_partition_info()
print(info["statistics"])
```

### 直接导入Manager类

```python
from datasets import MNISTFederatedManager

# 直接使用Manager类
manager = MNISTFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="iid",
    seed=42
)

manager.prepare_data()
```

### 获取Manager类

```python
from datasets import get_federated_manager_class

# 动态获取Manager类
ManagerClass = get_federated_manager_class("cifar10")
manager = ManagerClass(
    data_root="./data",
    num_clients=5,
    partition_strategy="pathological",
    partition_params={"shards_per_client": 2},
    seed=42
)
```

## 数据集下载说明

所有数据集默认使用 **torchvision** 进行下载：

- **MNIST**: `torchvision.datasets.MNIST`
- **CIFAR-10**: `torchvision.datasets.CIFAR10`
- **Fashion-MNIST**: `torchvision.datasets.FashionMNIST`

数据将自动下载到指定的 `data_root` 目录。

## FederatedManager 实现

每个数据集模块现在都包含完整的FederatedManager实现：

```
datasets/
├── mnist/
│   ├── __init__.py          # 导出 MNISTFederatedManager
│   ├── raw.py
│   ├── preprocess.py
│   └── partition.py
├── cifar10/
│   ├── __init__.py          # 导出 CIFAR10FederatedManager
│   ├── raw.py
│   ├── preprocess.py
│   └── partition.py
└── fashion_mnist/
    ├── __init__.py          # 导出 FashionMNISTFederatedManager
    ├── raw.py
    ├── preprocess.py
    └── partition.py
```

`datasets/__init__.py` 提供以下便捷函数：
- `create_federated_manager()` - 创建Manager实例
- `get_federated_manager_class()` - 获取Manager类
- `list_available_datasets()` - 列出可用数据集
- `get_dataset_info()` - 获取数据集信息
