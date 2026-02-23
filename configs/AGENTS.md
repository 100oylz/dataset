# Configs 模块 - AI Agent 指引

> 为 AI Agent 提供的配置管理开发和维护指南

## 🎯 模块定位

Configs 模块是框架的**配置管理中心**，负责：
1. 存储数据集的默认元信息（类别数、样本数、模块路径等）
2. 存储划分策略的默认参数
3. 提供配置构建和验证功能

## 📁 文件职责

| 文件 | 职责 | 关键内容 |
|------|------|----------|
| `default_configs.py` | 默认配置定义 | `DatasetConfig`, `DEFAULT_DATASET_CONFIGS`, `DEFAULT_PARTITION_CONFIGS` |
| `__init__.py` | 导出接口 | 导出所有配置类和函数 |

## 🔧 常见任务

### 任务1: 添加新数据集的配置

**场景**: 在 `datasets/` 下实现了新数据集，需要添加配置

**步骤**:

1. 在 `DEFAULT_DATASET_CONFIGS` 中添加新条目

```python
# configs/default_configs.py

DEFAULT_DATASET_CONFIGS = {
    # ... 现有配置
    
    "my_dataset": {
        # 数据特性
        "num_classes": 10,
        "num_features": 3072,
        "input_shape": (3, 32, 32),
        "train_samples": 50000,
        "test_samples": 10000,
        "data_type": "image",  # image/text/audio
        "task_type": "classification",  # classification/detection/segmentation
        "class_names": ['class0', 'class1', 'class2', 'class3', 'class4',
                        'class5', 'class6', 'class7', 'class8', 'class9'],
        
        # 模块路径 - 必须与文件路径一致
        "raw_dataset_module": "datasets.my_dataset.raw",
        "raw_dataset_class": "MyDatasetRawDataset",
        "preprocessor_module": "datasets.my_dataset.preprocess",
        "preprocessor_class": "MyDatasetPreprocessor",
        "partitioner_module": "datasets.my_dataset.partition",
        "partitioner_class": "MyDatasetPartitioner",
    },
}
```

**检查清单**:
- [ ] `num_classes` 与实际类别数一致
- [ ] `input_shape` 格式为 (C, H, W)
- [ ] `*_module` 路径使用点分表示法
- [ ] `*_class` 类名拼写正确
- [ ] `class_names` 列表长度等于 `num_classes`

### 任务2: 修改现有数据集配置

**场景**: 需要更新已有数据集的元信息

**示例**: 更新 MNIST 的模块路径

```python
DEFAULT_DATASET_CONFIGS = {
    "mnist": {
        # ... 其他字段保持不变
        
        # 修改模块路径
        "raw_dataset_module": "datasets.mnist.raw",
        "raw_dataset_class": "MNISTRawDataset",
        # ...
    },
}
```

**注意**: 修改模块路径会影响 `database/DynamicImporter` 的功能，需确保路径正确。

### 任务3: 添加新划分策略配置

**场景**: 添加了新的划分策略，需要配置参数信息

**步骤**:

```python
# configs/default_configs.py

DEFAULT_PARTITION_CONFIGS = {
    # ... 现有配置
    
    "my_strategy": {
        "description": "自定义划分策略的描述",
        "strategy_type": "non-iid",  # 或 "iid"
        "default_params": {
            "alpha": 0.5,
            "beta": 10,
        },
        "param_schema": {
            "alpha": {
                "type": "float",
                "default": 0.5,
                "description": "浓度参数，控制Non-IID程度",
                "min": 0.01,
                "max": 100.0,
            },
            "beta": {
                "type": "int",
                "default": 10,
                "description": "整数参数",
                "min": 1,
                "max": 100,
            },
        },
    },
}
```

**参数模式 (`param_schema`) 字段**:
- `type`: 参数类型（"int", "float", "bool", "string"）
- `default`: 默认值
- `description`: 参数描述
- `min`/`max`: 数值范围（可选）
- `enum`: 枚举值列表（可选）

### 任务4: 扩展 DatasetConfig 字段

**场景**: 需要添加新的配置参数

**步骤**:

1. 在 `DatasetConfig` 数据类中添加新字段

```python
@dataclass
class DatasetConfig:
    # ... 现有字段
    
    # 新字段
    validation_split: float = 0.1  # 验证集比例
    early_stopping_patience: int = 10  # 早停耐心值
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            # ... 现有字段
            "validation_split": self.validation_split,
            "early_stopping_patience": self.early_stopping_patience,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "DatasetConfig":
        return cls(
            # ... 现有字段
            validation_split=config_dict.get("validation_split", 0.1),
            early_stopping_patience=config_dict.get("early_stopping_patience", 10),
        )
```

### 任务5: 修复配置相关问题

**症状1**: `get_dataset_config` 返回 None 或 KeyError

**原因**: 数据集名称不在 `DEFAULT_DATASET_CONFIGS` 中

**解决**:
```python
# 检查配置是否存在
if dataset_name not in DEFAULT_DATASET_CONFIGS:
    available = list(DEFAULT_DATASET_CONFIGS.keys())
    raise ValueError(f"Unknown dataset: {dataset_name}. Available: {available}")
```

**症状2**: 动态导入失败，提示找不到模块

**原因**: 模块路径配置错误

**调试**:
```python
from configs import get_dataset_config

config = get_dataset_config("mnist")
module_path = config["raw_dataset_module"]
class_name = config["raw_dataset_class"]

print(f"尝试导入: {module_path}.{class_name}")

# 手动测试导入
try:
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    print(f"成功导入: {cls}")
except ImportError as e:
    print(f"导入失败: {e}")
except AttributeError as e:
    print(f"类不存在: {e}")
```

## 🚨 重要约束

### 1. 模块路径格式

```python
# ✅ 正确 - 点分表示法，相对于项目根目录
"datasets.mnist.raw"

# ❌ 错误 - 使用斜杠
"datasets/mnist/raw"

# ❌ 错误 - 使用文件扩展名
"datasets.mnist.raw.py"

# ❌ 错误 - 相对路径
"./datasets.mnist.raw"
```

### 2. 类名匹配

配置中的类名必须与代码中的类名**完全一致**（包括大小写）：

```python
# configs/default_configs.py
"raw_dataset_class": "MNISTRawDataset"

# datasets/mnist/raw.py
class MNISTRawDataset(RawDatasetBase):  # ✅ 匹配
    pass

class MnistRawDataset(RawDatasetBase):  # ❌ 不匹配（大小写不同）
    pass
```

### 3. 配置数据一致性

```python
# ✅ 正确 - 信息一致
"num_classes": 10,
"class_names": ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],  # 10个

# ❌ 错误 - 信息不一致
"num_classes": 10,
"class_names": ['0', '1', '2'],  # 只有3个！
```

### 4. input_shape 格式

```python
# ✅ 正确 - PyTorch 格式 (C, H, W)
"input_shape": (3, 32, 32)

# ❌ 错误 - TensorFlow 格式 (H, W, C)
"input_shape": (32, 32, 3)
```

## 🔗 模块关系

```
configs/
    └── default_configs.py
            ├── DatasetConfig (配置数据类)
            ├── DEFAULT_DATASET_CONFIGS (数据集配置字典)
            │       └── 被 database/DatasetRegistration 使用
            │       └── 被 database/DatasetFactory 使用
            │
            ├── DEFAULT_PARTITION_CONFIGS (划分策略配置字典)
            │       └── 被 database/PartitionStrategy 使用
            │
            └── 辅助函数
                    ├── get_dataset_config()
                    ├── get_partition_config()
                    └── build_config()
```

## 📝 配置验证

添加新配置后，建议运行验证代码：

```python
# 验证配置完整性
def validate_dataset_config(dataset_name: str):
    from configs import get_dataset_config
    
    config = get_dataset_config(dataset_name)
    required_fields = [
        "num_classes", "num_features", "input_shape",
        "train_samples", "test_samples",
        "raw_dataset_module", "raw_dataset_class",
        "preprocessor_module", "preprocessor_class",
        "partitioner_module", "partitioner_class",
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing field: {field}")
    
    # 验证列表长度
    if len(config.get("class_names", [])) != config["num_classes"]:
        raise ValueError("class_names length doesn't match num_classes")
    
    print(f"✅ {dataset_name} 配置验证通过")

# 验证所有数据集
from configs import DEFAULT_DATASET_CONFIGS

for dataset_name in DEFAULT_DATASET_CONFIGS:
    validate_dataset_config(dataset_name)
```

## 📚 相关文档

- [../README.md](../README.md) - 项目总览
- [../database/AGENTS.md](../database/AGENTS.md) - Database 模块指引
- [../datasets/AGENTS.md](../datasets/AGENTS.md) - Datasets 模块指引
