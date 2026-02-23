# Database 模块

> 联邦学习数据集管理框架的数据注册和动态导入模块

## 概述

Database 模块提供数据集的**元数据管理**和**动态导入**功能。通过数据库存储数据集的注册信息，支持运行时发现和动态加载数据集组件。

## 模块结构

```
database/
├── __init__.py              # 导出数据库相关类
├── models.py                # 数据模型定义
├── dataset_registry.py      # 数据集注册中心
└── dynamic_importer.py      # 动态导入器
```

## 核心类详解

### 1. DatasetRegistration

**位置**: `models.py`

**职责**: 数据集注册信息的数据类，用于存储数据集的完整元数据

**关键字段**:

| 字段类别 | 字段名 | 说明 |
|----------|--------|------|
| 基本信息 | `name` | 数据集唯一标识名 |
| | `display_name` | 显示名称 |
| | `description` | 数据集描述 |
| 数据特性 | `num_classes` | 类别数 |
| | `num_features` | 特征维度 |
| | `input_shape` | 输入形状 |
| | `data_type` | 数据类型（image/text/audio） |
| | `task_type` | 任务类型（classification/detection） |
| **模块路径** | `raw_dataset_module` | 原始数据集模块路径 |
| | `raw_dataset_class` | 原始数据集类名 |
| | `preprocessor_module` | 预处理器模块路径 |
| | `preprocessor_class` | 预处理器类名 |
| | `partitioner_module` | 划分器模块路径 |
| | `partitioner_class` | 划分器类名 |
| 统计信息 | `train_samples` | 训练样本数 |
| | `test_samples` | 测试样本数 |
| 元数据 | `version` | 版本号 |
| | `created_at` | 创建时间 |

**方法**:
- `to_dict()`: 转换为字典
- `from_dict(data)`: 从字典创建
- `get_module_import_info()`: 获取模块导入信息

**示例**:
```python
from database import DatasetRegistration

registration = DatasetRegistration(
    name="mnist",
    display_name="MNIST",
    description="手写数字数据集",
    num_classes=10,
    input_shape=(1, 28, 28),
    raw_dataset_module="datasets.mnist.raw",
    raw_dataset_class="MNISTRawDataset",
    preprocessor_module="datasets.mnist.preprocess",
    preprocessor_class="MNISTPreprocessor",
    partitioner_module="datasets.mnist.partition",
    partitioner_class="MNISTPartitioner",
)
```

### 2. DatasetRegistry

**位置**: `dataset_registry.py`

**职责**: 数据集注册中心，管理所有已注册数据集的元数据

**设计模式**: 单例模式（Singleton）

**关键方法**:

| 方法 | 说明 |
|------|------|
| `register(registration)` | 注册数据集 |
| `unregister(dataset_name)` | 注销数据集 |
| `get(dataset_name)` | 获取数据集注册信息 |
| `list_datasets(...)` | 列出所有数据集 |
| `exists(dataset_name)` | 检查数据集是否已注册 |
| `load_from_database()` | 从数据库加载注册信息 |
| `save_to_database()` | 保存注册信息到数据库 |

**示例**:
```python
from database import DatasetRegistry, DatasetRegistration

# 获取注册中心实例（单例）
registry = DatasetRegistry()

# 从数据库加载
registry.load_from_database()

# 注册新数据集
registration = DatasetRegistration(name="my_dataset", ...)
registry.register(registration)

# 查询数据集
info = registry.get("mnist")
all_datasets = registry.list_datasets()
```

### 3. PartitionStrategy

**位置**: `models.py`

**职责**: 划分策略配置，存储支持的划分策略及其默认参数

**关键字段**:
- `name`: 策略名称（iid/dirichlet/pathological）
- `display_name`: 显示名称
- `description`: 策略描述
- `default_params`: 默认参数
- `param_schema`: 参数 JSON Schema
- `min_clients`/`max_clients`: 支持的客户端数量范围
- `supported_datasets`: 支持的数据集列表

### 4. PartitionStrategyRegistry

**位置**: `dataset_registry.py`

**职责**: 划分策略注册中心，管理所有支持的划分策略

**设计模式**: 单例模式

**关键方法**:
- `register(strategy)`: 注册划分策略
- `get(strategy_name)`: 获取划分策略
- `list_strategies()`: 列出所有策略
- `get_supported_strategies(dataset_name)`: 获取数据集支持的策略

### 5. DynamicImporter

**位置**: `dynamic_importer.py`

**职责**: 根据模块路径和类名动态导入类

**关键方法**:

| 方法 | 说明 |
|------|------|
| `import_class(module_path, class_name)` | 动态导入类 |
| `import_dataset_components(registration)` | 导入数据集的所有组件 |
| `create_instance(module_path, class_name, ...)` | 动态创建类实例 |
| `create_raw_dataset(registration, ...)` | 创建原始数据集实例 |
| `create_preprocessor(registration, ...)` | 创建预处理器实例 |
| `create_partitioner(registration, ...)` | 创建划分器实例 |
| `create_manager(registration, ...)` | 创建管理器实例 |
| `clear_cache()` | 清除导入缓存 |

**缓存机制**: 已导入的类会被缓存，避免重复导入

**示例**:
```python
from database import DynamicImporter, DatasetRegistration

# 动态导入类
importer = DynamicImporter()
RawDatasetClass = DynamicImporter.import_class(
    module_path="datasets.mnist.raw",
    class_name="MNISTRawDataset"
)

# 创建实例
dataset = DynamicImporter.create_instance(
    "datasets.mnist.raw",
    "MNISTRawDataset",
    data_root="./data"
)
```

### 6. DatasetFactory

**位置**: `dynamic_importer.py`

**职责**: 通过数据集名称创建完整的数据集管理器

**关键方法**:

| 方法 | 说明 |
|------|------|
| `create(dataset_name, data_root, num_clients, ...)` | 创建数据集管理器 |
| `list_available_datasets()` | 列出所有可用数据集 |
| `get_dataset_info(dataset_name)` | 获取数据集信息 |

**示例**:
```python
from database import DatasetFactory, DatasetRegistry

# 初始化
registry = DatasetRegistry()
registry.load_from_database()

# 创建工厂
factory = DatasetFactory(registry)

# 创建管理器
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)

# 准备数据
manager.prepare_data()
```

## 数据库表结构

### dataset_registrations 表

```sql
CREATE TABLE IF NOT EXISTS dataset_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(128),
    description TEXT,
    
    num_classes INT DEFAULT 0,
    num_features INT DEFAULT 0,
    input_shape VARCHAR(64),
    data_type VARCHAR(32) DEFAULT 'image',
    task_type VARCHAR(32) DEFAULT 'classification',
    
    raw_dataset_module VARCHAR(256),
    raw_dataset_class VARCHAR(64),
    preprocessor_module VARCHAR(256),
    preprocessor_class VARCHAR(64),
    partitioner_module VARCHAR(256),
    partitioner_class VARCHAR(64),
    
    version VARCHAR(32) DEFAULT '1.0.0',
    author VARCHAR(128),
    source_url VARCHAR(512),
    
    train_samples INT DEFAULT 0,
    test_samples INT DEFAULT 0,
    
    extra_params JSON,
    tags JSON,
    
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_data_type (data_type),
    INDEX idx_task_type (task_type)
);
```

## 使用流程

### 完整使用示例

```python
from database import (
    DatasetRegistry,
    DatasetFactory,
    DatasetRegistration
)

# 步骤1: 初始化注册中心
registry = DatasetRegistry()
registry.load_from_database()

# 步骤2: 创建工厂
factory = DatasetFactory(registry)

# 步骤3: 创建管理器
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)

# 步骤4: 准备数据
manager.prepare_data()

# 步骤5: 使用数据
for batch in manager.get_client_loader(0, batch_size=32):
    # 训练逻辑
    pass
```

### 手动注册新数据集

```python
from database import DatasetRegistry, DatasetRegistration

# 创建注册信息
registration = DatasetRegistration(
    name="my_dataset",
    display_name="My Dataset",
    description="我的自定义数据集",
    num_classes=10,
    num_features=784,
    input_shape=(1, 28, 28),
    data_type="image",
    task_type="classification",
    raw_dataset_module="datasets.my_dataset.raw",
    raw_dataset_class="MyDatasetRawDataset",
    preprocessor_module="datasets.my_dataset.preprocess",
    preprocessor_class="MyDatasetPreprocessor",
    partitioner_module="datasets.my_dataset.partition",
    partitioner_class="MyDatasetPartitioner",
    train_samples=60000,
    test_samples=10000,
)

# 注册
registry = DatasetRegistry()
registry.register(registration)
registry.save_to_database()
```

## 注意事项

1. **模块路径正确性**: 确保 `*_module` 字段的路径正确，否则动态导入会失败
2. **类名正确性**: 确保 `*_class` 字段的类名存在且可导入
3. **单例模式**: `DatasetRegistry` 是单例，注意在多线程环境中的使用
4. **缓存机制**: `DynamicImporter` 会缓存已导入的类，如需重新导入需调用 `clear_cache()`
