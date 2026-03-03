# 联邦学习数据集管理框架 - API 文档

> 快速参考手册，便于日常开发调用

## 📚 目录

- [1. 快速开始](#1-快速开始)
- [2. 数据集管理器 API](#2-数据集管理器-api)
- [3. 数据库 API](#3-数据库-api)
- [4. 动态导入 API](#4-动态导入-api)
- [5. 基类 API](#5-基类-api)
- [6. 工具函数 API](#6-工具函数-api)
- [7. 配置 API](#7-配置-api)
- [8. 数据集信息](#8-数据集信息)
- [9. 完整示例](#9-完整示例)

---

## 1. 快速开始

### 1.1 创建管理器（推荐方式）

```python
from datasets import create_federated_manager

manager = create_federated_manager(
    dataset_name="mnist",          # 数据集名称
    data_root="./data",            # 数据根目录
    num_clients=10,                # 客户端数量
    partition_strategy="iid",      # 划分策略: iid / dirichlet / pathological
    partition_params={},           # 策略参数
    seed=42                        # 随机种子
)
```

### 1.2 直接使用具体管理器

```python
from datasets import MNISTFederatedManager, CIFAR10FederatedManager
from datasets import FashionMNISTFederatedManager, FEMNISTFederatedManager

manager = MNISTFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    seed=42
)
```

### 1.3 通过数据库工厂创建

```python
from database import DatasetFactory

factory = DatasetFactory()
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)
```

### 1.4 常用工作流

```python
# 1. 创建管理器
manager = create_federated_manager(
    dataset_name="cifar10",
    data_root="./data",
    num_clients=100,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.1}  # alpha越小越Non-IID
)

# 2. 准备数据（懒加载，首次调用时执行）
manager.prepare_data()

# 3. 获取客户端训练数据
client_loader = manager.get_client_loader(client_id=0, batch_size=32)

# 4. 获取测试数据
test_loader = manager.get_test_loader(batch_size=256)

# 5. 训练模型...
```

---

## 2. 数据集管理器 API

### 2.1 构造函数

```python
FederatedDatasetManager(
    data_root: str,                    # 数据根目录
    num_clients: int,                  # 客户端数量
    partition_strategy: str,           # 划分策略
    partition_params: dict = None,     # 划分参数
    seed: int = 42,                    # 随机种子
    **kwargs                            # 其他参数（传递给各组件）
)
```

### 2.2 数据准备

| 方法 | 说明 | 参数 |
|------|------|------|
| `prepare_data(force_download=False, force_preprocess=False)` | 准备数据流程：下载→预处理→划分 | `force_download`: 强制重新下载；`force_preprocess`: 强制重新预处理 |

### 2.3 数据加载器

| 方法 | 返回 | 参数 |
|------|------|------|
| `get_client_loader(client_id, batch_size=32, shuffle=True, **kwargs)` | `DataLoader` | `client_id`: 客户端ID；`batch_size`: 批次大小；`shuffle`: 是否打乱 |
| `get_test_loader(batch_size=256, **kwargs)` | `DataLoader` | `batch_size`: 批次大小 |

### 2.4 数据集获取

| 方法 | 返回 | 说明 |
|------|------|------|
| `get_client_dataset(client_id)` | `Dataset` | 获取指定客户端的预处理后数据集 |
| `get_test_dataset()` | `Dataset` | 获取预处理后测试数据集 |

### 2.5 信息获取

| 方法 | 返回 | 说明 |
|------|------|------|
| `get_data_info()` | `dict` | 获取数据集基本信息（类别数、样本数、形状等） |
| `get_partition_info()` | `dict` | 获取划分信息（策略、统计信息等） |

**`get_data_info()` 返回示例：**

```python
{
    "dataset_name": "mnist",
    "num_classes": 10,
    "num_features": 784,
    "input_shape": (1, 28, 28),
    "train_samples": 60000,
    "test_samples": 10000,
    "class_names": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
    "num_clients": 10,
    "partition_strategy": "dirichlet",
    "partition_params": {"alpha": 0.5},
    "seed": 42
}
```

**`get_partition_info()` 返回示例：**

```python
{
    "num_clients": 10,
    "partition_strategy": "dirichlet",
    "partition_params": {"alpha": 0.5},
    "partitioner_name": "mnist_dirichlet",
    "strategy_type": "non-iid",
    "statistics": {
        "client_samples": {0: 6001, 1: 5998, ...},  # 各客户端样本数
        "class_distribution": {0: {0: 123, 1: 456, ...}, ...},  # 类别分布
        "mean_samples_per_client": 6000.0,
        "std_samples_per_client": 123.4,
        "min_samples": 5800,
        "max_samples": 6200,
        "imbalance_ratio": 1.07
    }
}
```

### 2.6 划分结果持久化

| 方法 | 说明 | 参数 |
|------|------|------|
| `save_split(path=None)` | 保存划分结果到JSON | `path`: 保存路径，默认为 `{data_root}/{dataset_name}_split.json` |
| `load_split(path=None)` | 从JSON加载划分结果 | `path`: 加载路径 |

### 2.7 可视化

| 方法 | 说明 | 参数 |
|------|------|------|
| `visualize_client_distribution(title=None, save_path=None, figsize=(12,5), cmap="viridis", max_clients=10, max_classes=10)` | 可视化客户端类别分布 | `title`: 图表标题；`save_path`: 保存路径（None则显示）；`figsize`: 图像尺寸；`cmap`: 颜色映射；`max_clients`: 最多显示客户端数；`max_classes`: 最多显示类别数 |

**可视化效果：**
- 左图：堆叠柱状图（各类别样本数）
- 右图：热力图（各类别占比）

---

## 3. 数据库 API

### 3.1 DatasetRegistry（数据集注册中心）

```python
from database import DatasetRegistry, DatasetRegistration

# 获取单例实例
registry = DatasetRegistry()

# 注册数据集
registration = DatasetRegistration(
    name="mnist",
    display_name="MNIST",
    description="手写数字数据集",
    num_classes=10,
    num_features=784,
    input_shape=(1, 28, 28),
    raw_dataset_module="datasets.mnist.raw",
    raw_dataset_class="MNISTRawDataset",
    preprocessor_module="datasets.mnist.preprocess",
    preprocessor_class="MNISTPreprocessor",
    partitioner_module="datasets.mnist.partition",
    partitioner_class="MNISTPartitioner",
    train_samples=60000,
    test_samples=10000,
)
registry.register(registration)

# 获取数据集注册信息
reg = registry.get("mnist")

# 列出所有数据集
datasets = registry.list_datasets(data_type="image", status="active")

# 检查数据集是否存在
exists = registry.exists("mnist")

# 更新数据集信息
registry.update("mnist", {"description": "新的描述"})

# 注销数据集
registry.unregister("mnist")

# 从数据库加载/保存
registry.load_from_database()
registry.save_to_database()

# 清空内存缓存
registry.clear()
```

**DatasetRegistration 数据类：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | str | 数据集唯一标识名 |
| `display_name` | str | 显示名称 |
| `description` | str | 数据集描述 |
| `num_classes` | int | 类别数 |
| `num_features` | int | 特征维度 |
| `input_shape` | tuple | 输入形状 |
| `data_type` | str | 数据类型（image/text/audio等） |
| `task_type` | str | 任务类型 |
| `raw_dataset_module` | str | 原始数据集模块路径 |
| `raw_dataset_class` | str | 原始数据集类名 |
| `preprocessor_module` | str | 预处理器模块路径 |
| `preprocessor_class` | str | 预处理器类名 |
| `partitioner_module` | str | 划分器模块路径 |
| `partitioner_class` | str | 划分器类名 |
| `train_samples` | int | 训练样本数 |
| `test_samples` | int | 测试样本数 |
| `version` | str | 版本号 |
| `status` | str | 状态（active/deprecated/archived） |

### 3.2 PartitionStrategyRegistry（划分策略注册中心）

```python
from database import PartitionStrategyRegistry, PartitionStrategy

# 获取单例实例
strategy_registry = PartitionStrategyRegistry()

# 注册划分策略
strategy = PartitionStrategy(
    name="dirichlet",
    display_name="Dirichlet划分",
    description="基于Dirichlet分布的Non-IID划分",
    default_params={"alpha": 0.5},
    supported_datasets=["mnist", "cifar10", "fashion_mnist"],
    min_clients=2,
    max_clients=10000,
)
strategy_registry.register(strategy)

# 获取策略
strategy = strategy_registry.get("dirichlet")

# 列出所有策略
strategies = strategy_registry.list_strategies()

# 获取数据集支持的策略
supported = strategy_registry.get_supported_strategies("mnist")
```

### 3.3 PartitionResultRegistry（划分结果注册中心）

```python
from database import PartitionResultRegistry, PartitionResult

# 获取单例实例
result_registry = PartitionResultRegistry()

# 保存划分结果
result = PartitionResult(
    dataset_name="mnist",
    strategy_name="dirichlet",
    num_clients=10,
    params={"alpha": 0.5},
    client_indices={0: [1, 2, 3], 1: [4, 5, 6]},
    total_samples=60000,
)
result_id = result_registry.save(result)

# 获取划分结果
result = result_registry.get("mnist", "dirichlet", num_clients=10)

# 列出划分结果
results = result_registry.list_results(dataset_name="mnist")
```

---

## 4. 动态导入 API

### 4.1 DynamicImporter（动态导入器）

```python
from database import DynamicImporter, DatasetRegistration

# 动态导入类
RawDatasetClass = DynamicImporter.import_class(
    module_path="datasets.mnist.raw",
    class_name="MNISTRawDataset"
)

# 动态创建实例
raw_dataset = DynamicImporter.create_instance(
    module_path="datasets.mnist.raw",
    class_name="MNISTRawDataset",
    data_root="./data"  # 传递给构造函数的参数
)

# 从注册信息导入所有组件
registration = DatasetRegistration(...)
components = DynamicImporter.import_dataset_components(registration)
# 返回: {"raw_dataset": ..., "preprocessor": ..., "partitioner": ..., "manager": ...}

# 创建特定组件实例
raw_dataset = DynamicImporter.create_raw_dataset(registration, data_root="./data")
preprocessor = DynamicImporter.create_preprocessor(registration)
partitioner = DynamicImporter.create_partitioner(
    registration, 
    num_clients=10, 
    strategy="iid"
)
manager = DynamicImporter.create_manager(
    registration,
    data_root="./data",
    num_clients=10,
    partition_strategy="iid"
)

# 缓存管理
DynamicImporter.clear_cache()
info = DynamicImporter.get_cache_info()
is_cached = DynamicImporter.is_cached("datasets.mnist.raw", "MNISTRawDataset")
```

### 4.2 DatasetFactory（数据集工厂）

```python
from database import DatasetFactory

# 创建工厂
factory = DatasetFactory()

# 创建管理器
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)

# 创建所有组件
components = factory.create_components(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="iid"
)

# 获取可用数据集
available_datasets = factory.list_available_datasets()

# 获取数据集信息
info = factory.get_dataset_info("mnist")

# 获取支持的划分策略
strategies = factory.get_supported_strategies("mnist")
```

---

## 5. 基类 API

### 5.1 RawDatasetBase（原始数据集基类）

```python
from core import RawDatasetBase

class MyRawDataset(RawDatasetBase):
    # 必须实现的属性
    @property
    def num_classes(self) -> int: ...
    
    @property
    def num_features(self) -> int: ...
    
    @property
    def input_shape(self) -> Tuple[int, ...]: ...
    
    @property
    def train_samples(self) -> int: ...
    
    @property
    def test_samples(self) -> int: ...
    
    # 必须实现的方法
    def download(self) -> None: ...
    def load_train_data(self) -> Dataset: ...
    def load_test_data(self) -> Dataset: ...
    
    # 可选实现的方法
    def get_class_names(self) -> Optional[List[str]]: ...
    def get_dataset_info(self) -> Dict[str, Any]: ...
```

**主要方法：**

| 方法 | 返回 | 说明 |
|------|------|------|
| `download()` | None | 下载原始数据 |
| `load_train_data()` | Dataset | 加载训练数据集 |
| `load_test_data()` | Dataset | 加载测试数据集 |
| `get_class_names()` | List[str] \| None | 获取类别名称列表 |
| `get_dataset_info()` | dict | 获取数据集完整信息 |

**主要属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `num_classes` | int | 类别数量 |
| `num_features` | int | 特征维度 |
| `input_shape` | tuple | 输入数据形状 |
| `train_samples` | int | 训练样本数 |
| `test_samples` | int | 测试样本数 |
| `data_root` | Path | 数据根目录 |
| `dataset_name` | str | 数据集名称 |

### 5.2 PreprocessorBase（预处理器基类）

```python
from core import PreprocessorBase

class MyPreprocessor(PreprocessorBase):
    # 必须实现的属性
    @property
    def name(self) -> str: ...
    
    # 必须实现的方法
    def fit(self, dataset: Dataset) -> "MyPreprocessor": ...
    def get_train_transform(self) -> Callable: ...
    def get_test_transform(self) -> Callable: ...
    
    # 可选实现的方法
    def inverse_transform(self, data: Any) -> Any: ...
    def save_params(self, path: str) -> None: ...
    def load_params(self, path: str) -> "PreprocessorBase": ...
    def get_params(self) -> Dict[str, Any]: ...
    def set_params(self, params: Dict[str, Any]) -> "PreprocessorBase": ...
```

**主要方法：**

| 方法 | 返回 | 说明 |
|------|------|------|
| `fit(dataset)` | self | 根据数据拟合预处理参数 |
| `get_train_transform()` | Callable | 获取训练数据变换函数 |
| `get_test_transform()` | Callable | 获取测试数据变换函数 |
| `inverse_transform(data)` | Any | 逆向变换（反归一化） |
| `save_params(path)` | None | 保存预处理参数 |
| `load_params(path)` | self | 加载预处理参数 |
| `get_params()` | dict | 获取预处理参数字典 |
| `set_params(params)` | self | 设置预处理参数 |

**ComposePreprocessor（组合预处理器）：**

```python
from core import ComposePreprocessor

# 组合多个预处理器
composed = ComposePreprocessor([preprocessor1, preprocessor2, preprocessor3])

# 使用方式与普通预处理器相同
transform = composed.get_train_transform()
```

### 5.3 PartitionerBase（划分器基类）

```python
from core import PartitionerBase

class MyPartitioner(PartitionerBase):
    # 必须实现的属性
    @property
    def name(self) -> str: ...
    
    @property
    def strategy_type(self) -> str: ...  # "iid" 或 "non-iid"
    
    # 必须实现的方法
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]: ...
```

**主要方法：**

| 方法 | 返回 | 说明 |
|------|------|------|
| `partition(dataset)` | Dict[int, List[int]] | 执行数据划分，返回 {client_id: [indices]} |
| `get_client_dataset(dataset, client_id, client_indices)` | Subset | 获取指定客户端的数据子集 |
| `get_distribution(dataset, client_indices)` | Dict[int, Dict[int, int]] | 获取各类别的分布 |
| `get_statistics(dataset, client_indices)` | dict | 获取划分统计信息 |
| `save_partition(client_indices, path)` | None | 保存划分结果 |
| `load_partition(path)` | Dict[int, List[int]] | 加载划分结果 |

**内置划分器：**

| 划分器 | 类型 | 参数 | 说明 |
|--------|------|------|------|
| `IIDPartitioner` | IID | `num_clients`, `seed` | 随机均匀分配 |
| `DirichletPartitioner` | Non-IID | `num_clients`, `alpha`, `seed` | Dirichlet分布分配 |
| `PathologicalPartitioner` | Non-IID | `num_clients`, `shards_per_client`, `seed` | 病态划分 |

**使用示例：**

```python
from core import IIDPartitioner, DirichletPartitioner, PathologicalPartitioner

# IID划分
partitioner = IIDPartitioner(num_clients=10, seed=42)
client_indices = partitioner.partition(train_dataset)

# Dirichlet划分（alpha越小越Non-IID）
partitioner = DirichletPartitioner(num_clients=10, alpha=0.5, seed=42)
client_indices = partitioner.partition(train_dataset)

# 病态划分（每个客户端只获得指定数量的类别）
partitioner = PathologicalPartitioner(
    num_clients=10, 
    shards_per_client=2,  # 每个客户端2个类别
    seed=42
)
client_indices = partitioner.partition(train_dataset)

# 获取统计信息
stats = partitioner.get_statistics(train_dataset, client_indices)
print(stats["samples_per_client"])  # 各客户端样本数
print(stats["distribution"])        # 类别分布

# 保存/加载划分结果
partitioner.save_partition(client_indices, "./split.json")
loaded_indices = partitioner.load_partition("./split.json")
```

---

## 6. 工具函数 API

### 6.1 随机种子设置

```python
from utils import set_seed

worker_init_fn = set_seed(seed=42)
# 返回的 worker_init_fn 可用于 DataLoader 的 worker_init_fn 参数
```

### 6.2 设备获取

```python
from utils import get_device

device = get_device()           # 自动选择最优设备（CUDA > MPS > CPU）
device = get_device("cuda")     # 强制使用 CUDA
device = get_device("cpu")      # 强制使用 CPU
device = get_device("cuda:1")   # 指定使用第2张GPU
```

### 6.3 JSON 操作

```python
from utils import save_json, load_json

# 保存数据
save_json(data, path="./results/metrics.json", indent=2, ensure_ascii=False)

# 加载数据
data = load_json(path="./results/metrics.json")
```

### 6.4 目录操作

```python
from utils import ensure_dir

path = ensure_dir("./experiments/run_1/logs")  # 递归创建目录
```

### 6.5 类别分布计算

```python
from utils import compute_class_distribution

distribution = compute_class_distribution(labels=[0, 1, 0, 2, 1, 0])
# 返回: {0: 3, 1: 2, 2: 1}
```

### 6.6 分布可视化（通用）

```python
from utils import visualize_distribution

# 通用分布可视化（不依赖管理器）
visualize_distribution(
    distribution={
        0: {0: 100, 1: 200, 2: 50},   # client_id: {class: count}
        1: {0: 150, 1: 100, 2: 80},
    },
    title="Custom Distribution",
    save_path="./results/dist.png",
    figsize=(12, 5),
    cmap="viridis",
    max_clients=10,
    max_classes=10
)
```

### 6.7 字节格式化

```python
from utils import format_bytes

format_bytes(1536000)   # 返回: "1.46 MB"
format_bytes(1023)      # 返回: "1023 B"
```

### 6.8 计时装饰器

```python
from utils import timer

@timer
def train_model():
    time.sleep(1)

train_model()  # 输出: [timer] train_model executed in 1.0023s
```

---

## 7. 配置 API

### 7.1 数据集配置

```python
from configs import DatasetConfig, build_config

# 方式1: 直接创建配置对象
config = DatasetConfig(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    batch_size=32,
    seed=42
)

# 方式2: 使用 build_config 从配置目录加载
config = build_config(
    dataset_name="mnist",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    save_path="./configs/my_config.json"  # 可选：保存配置
)
```

**DatasetConfig 字段：**

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dataset_name` | str | "" | 数据集名称 |
| `data_root` | str | "./data" | 数据根目录 |
| `num_clients` | int | 10 | 客户端数量 |
| `partition_strategy` | str | "iid" | 划分策略 |
| `partition_params` | dict | {} | 划分参数 |
| `augment` | bool | True | 是否数据增强 |
| `normalize` | bool | True | 是否归一化 |
| `batch_size` | int | 32 | 批次大小 |
| `num_workers` | int | 0 | 数据加载线程数 |
| `pin_memory` | bool | False | 是否锁页内存 |
| `seed` | int | 42 | 随机种子 |
| `download` | bool | True | 是否自动下载 |
| `force_preprocess` | bool | False | 是否强制重新预处理 |

### 7.2 配置转字典

```python
config_dict = config.to_dict()      # DatasetConfig → dict
config = DatasetConfig.from_dict(config_dict)  # dict → DatasetConfig

# 更新配置
config.update(batch_size=64, num_clients=20)
```

---

## 8. 数据集信息

### 8.1 可用数据集列表

```python
from datasets import list_available_datasets

datasets = list_available_datasets()
# 返回: ['mnist', 'cifar10', 'fashion_mnist', 'femnist']
```

### 8.2 获取数据集信息

```python
from datasets import get_dataset_info

info = get_dataset_info("mnist")
```

### 8.3 获取数据集组件类

```python
from datasets import (
    get_raw_dataset_class,      # 获取原始数据集类
    get_preprocessor_class,      # 获取预处理器类
    get_partitioner_class,       # 获取划分器类
    get_federated_manager_class  # 获取联邦管理器类
)

RawDatasetClass = get_raw_dataset_class("mnist")
PreprocessorClass = get_preprocessor_class("mnist")
PartitionerClass = get_partitioner_class("mnist")
ManagerClass = get_federated_manager_class("mnist")
```

### 8.4 各数据集参数对照表

| 数据集 | 类别数 | 图像尺寸 | 训练样本 | 测试样本 |
|--------|--------|----------|----------|----------|
| MNIST | 10 | 1×28×28 | 60,000 | 10,000 |
| CIFAR-10 | 10 | 3×32×32 | 50,000 | 10,000 |
| Fashion-MNIST | 10 | 1×28×28 | 60,000 | 10,000 |
| FEMNIST | 62 | 1×28×28 | 697,932 | 116,323 |

### 8.5 划分策略参数

| 策略 | 类型 | 参数 | 说明 |
|------|------|------|------|
| `iid` | IID | 无 | 数据随机均匀分配 |
| `dirichlet` | Non-IID | `alpha` (默认0.5) | alpha越小越Non-IID |
| `pathological` | Non-IID | `shards_per_client` (默认2) | 每个客户端的类别数 |

**FEMNIST默认shards_per_client为5（因其有62个类别）**

---

## 9. 完整示例

### 9.1 基础训练流程

```python
import torch
import torch.nn as nn
from datasets import create_federated_manager

# 1. 创建管理器
manager = create_federated_manager(
    dataset_name="cifar10",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5},
    seed=42
)

# 2. 准备数据
manager.prepare_data()

# 3. 获取数据信息
info = manager.get_data_info()
print(f"Dataset: {info['dataset_name']}")
print(f"Classes: {info['num_classes']}")
print(f"Input shape: {info['input_shape']}")

# 4. 联邦学习训练
for round in range(10):
    for client_id in range(manager._num_clients):
        # 获取客户端数据
        loader = manager.get_client_loader(client_id, batch_size=32)
        
        # 训练客户端模型...
        for batch_idx, (data, target) in enumerate(loader):
            # 训练代码...
            pass
    
    # 聚合模型...
    
    # 评估（使用测试集）
    test_loader = manager.get_test_loader(batch_size=256)
    # 评估代码...

# 5. 保存划分结果
manager.save_split("./splits/cifar10_split.json")

# 6. 可视化分布
manager.visualize_client_distribution(
    title="CIFAR-10 Client Distribution",
    save_path="./results/cifar10_dist.png"
)
```

### 9.2 加载已有划分

```python
from datasets import MNISTFederatedManager

manager = MNISTFederatedManager(
    data_root="./data",
    num_clients=10,
    partition_strategy="iid",
    seed=42
)

# 加载之前保存的划分
manager.load_split("./splits/mnist_split.json")

# 准备数据（会使用加载的划分）
manager.prepare_data()

# 继续使用...
```

### 9.3 对比不同划分策略

```python
from datasets import create_federated_manager

strategies = [
    ("iid", {}),
    ("dirichlet", {"alpha": 0.5}),
    ("dirichlet", {"alpha": 0.1}),
    ("pathological", {"shards_per_client": 2}),
]

for strategy, params in strategies:
    manager = create_federated_manager(
        dataset_name="mnist",
        data_root="./data",
        num_clients=10,
        partition_strategy=strategy,
        partition_params=params,
        seed=42
    )
    manager.prepare_data()
    
    # 可视化并保存
    param_str = "_".join([f"{k}={v}" for k, v in params.items()]) if params else "default"
    manager.visualize_client_distribution(
        title=f"MNIST {strategy} ({param_str})",
        save_path=f"./results/mnist_{strategy}_{param_str}.png"
    )
```

### 9.4 大规模客户端设置

```python
# FEMNIST适合大规模联邦学习场景
manager = create_federated_manager(
    dataset_name="femnist",
    data_root="./data",
    num_clients=100,           # 更多客户端
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.1},
    seed=42
)

manager.prepare_data()

# 可视化（自动只显示样本量最多的前10个客户端）
manager.visualize_client_distribution(
    max_clients=10,    # 最多显示10个客户端
    max_classes=10     # 最多显示10个类别
)
```

### 9.5 自定义数据集注册

```python
from database import DatasetRegistry, DatasetRegistration, DatasetFactory

# 创建注册信息
registration = DatasetRegistration(
    name="my_dataset",
    display_name="My Dataset",
    description="自定义数据集",
    num_classes=10,
    num_features=784,
    input_shape=(1, 28, 28),
    raw_dataset_module="datasets.my_dataset.raw",
    raw_dataset_class="MyRawDataset",
    preprocessor_module="datasets.my_dataset.preprocess",
    preprocessor_class="MyPreprocessor",
    partitioner_module="datasets.my_dataset.partition",
    partitioner_class="MyPartitioner",
)

# 注册到注册中心
registry = DatasetRegistry()
registry.register(registration)

# 使用工厂创建管理器
factory = DatasetFactory(registry)
manager = factory.create(
    dataset_name="my_dataset",
    data_root="./data",
    num_clients=10,
    partition_strategy="iid"
)
```

---

## 附录：快速参考卡

```python
# ===== 导入 =====
from datasets import (
    create_federated_manager,      # 创建管理器
    list_available_datasets,       # 列出数据集
    get_dataset_info,              # 获取数据集信息
    MNISTFederatedManager,         # MNIST管理器
    CIFAR10FederatedManager,       # CIFAR-10管理器
    FashionMNISTFederatedManager,  # Fashion-MNIST管理器
    FEMNISTFederatedManager,       # FEMNIST管理器
)

from database import (
    DatasetRegistry,               # 数据集注册中心
    PartitionStrategyRegistry,     # 划分策略注册中心
    PartitionResultRegistry,       # 划分结果注册中心
    DynamicImporter,               # 动态导入器
    DatasetFactory,                # 数据集工厂
    DatasetRegistration,           # 数据集注册信息
    PartitionStrategy,             # 划分策略配置
    PartitionResult,               # 划分结果
)

from core import (
    RawDatasetBase,                # 原始数据集基类
    PreprocessorBase,              # 预处理器基类
    PartitionerBase,               # 划分器基类
    IIDPartitioner,                # IID划分器
    DirichletPartitioner,          # Dirichlet划分器
    PathologicalPartitioner,       # 病态划分器
    FederatedDatasetManager,       # 联邦学习管理器基类
)

from utils import (
    set_seed,                      # 设置随机种子
    get_device,                    # 获取设备
    save_json, load_json,          # JSON操作
    ensure_dir,                    # 创建目录
    visualize_distribution,        # 分布可视化
    timer,                         # 计时装饰器
)

from configs import (
    DatasetConfig,                 # 数据集配置
    build_config,                  # 构建配置
)

# ===== 创建管理器 =====
manager = create_federated_manager(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",  # iid / dirichlet / pathological
    partition_params={"alpha": 0.5},
    seed=42
)

# ===== 数据准备 =====
manager.prepare_data()

# ===== 数据加载 =====
train_loader = manager.get_client_loader(client_id=0, batch_size=32)
test_loader = manager.get_test_loader(batch_size=256)

# ===== 信息获取 =====
data_info = manager.get_data_info()
partition_info = manager.get_partition_info()

# ===== 持久化 =====
manager.save_split("./splits/split.json")
manager.load_split("./splits/split.json")

# ===== 可视化 =====
manager.visualize_client_distribution(
    save_path="./results/dist.png"
)
```

---

*文档版本: 1.1*  
*最后更新: 2026-03-03*
