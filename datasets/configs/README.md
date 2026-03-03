# 数据集配置目录

此目录包含数据集的 JSON 配置文件，用于将数据集和划分策略信息导入到数据库。

## 文件说明

| 文件 | 用途 | 对应数据库表 |
|------|------|-------------|
| `datasets.json` | 数据集配置 | `dataset_registrations` |
| `partition_strategies.json` | 划分策略配置 | `partition_strategies` |

## JSON 结构与数据库表结构对照

### datasets.json

JSON 字段与 `dataset_registrations` 表字段一一对应：

```json
{
  "datasets": [
    {
      "name": "mnist",                    // VARCHAR(64) - 数据集唯一名称
      "display_name": "MNIST",            // VARCHAR(128) - 显示名称
      "description": "...",               // TEXT - 描述
      "num_classes": 10,                  // INT - 类别数
      "num_features": 784,                // INT - 特征维度
      "input_shape": "1,28,28",           // VARCHAR(32) - 输入形状
      "data_type": "image",               // VARCHAR(32) - 数据类型
      "task_type": "classification",      // VARCHAR(32) - 任务类型
      "raw_dataset_module": "datasets.mnist.raw",      // VARCHAR(256)
      "raw_dataset_class": "MNISTRawDataset",          // VARCHAR(128)
      "preprocessor_module": "datasets.mnist.preprocess", // VARCHAR(256)
      "preprocessor_class": "MNISTPreprocessor",       // VARCHAR(128)
      "partitioner_module": "datasets.mnist.partition",  // VARCHAR(256)
      "partitioner_class": "MNISTPartitioner",         // VARCHAR(128)
      "version": "1.0.0",                 // VARCHAR(32)
      "author": "Yann LeCun",             // VARCHAR(256)
      "source_url": "http://...",         // VARCHAR(512)
      "license": "Unknown",               // VARCHAR(64)
      "train_samples": 60000,             // INT
      "test_samples": 10000,              // INT
      "extra_params": {                   // JSON
        "mean": [0.1307],
        "std": [0.3081]
      },
      "tags": ["image", "classification"], // JSON
      "status": "active"                  // VARCHAR(32) - active/deprecated/archived
    }
  ]
}
```

### partition_strategies.json

JSON 字段与 `partition_strategies` 表字段一一对应：

```json
{
  "strategies": [
    {
      "name": "iid",                      // VARCHAR(64) - 策略唯一名称
      "display_name": "IID 划分",          // VARCHAR(128)
      "description": "...",               // TEXT
      "default_params": {},               // JSON
      "param_schema": {                   // JSON - JSON Schema 格式
        "type": "object",
        "properties": {}
      },
      "min_clients": 2,                   // INT
      "max_clients": 10000,               // INT
      "supported_datasets": ["mnist"],    // JSON
      "is_federated": true,               // BOOLEAN
      "status": "active"                  // VARCHAR(32)
    }
  ]
}
```

## 使用方法

### 1. 命令行导入

```bash
# 使用默认配置导入
python scripts/register_datasets.py

# 强制覆盖已有数据
python scripts/register_datasets.py --overwrite

# 使用自定义配置文件
python scripts/register_datasets.py --datasets ./my_datasets.json --strategies ./my_strategies.json

# 显示详细日志
python scripts/register_datasets.py -v
```

### 2. Python 代码导入

```python
from datasets import register_all, register_datasets, register_strategies

# 导入所有配置
stats = register_all()
print(f"导入完成: {stats['datasets']} 个数据集, {stats['strategies']} 个策略")

# 仅导入数据集
count = register_datasets()

# 仅导入策略
count = register_strategies()

# 不覆盖已有数据
register_all(overwrite=False)
```

### 3. 高级用法

```python
from datasets.registry import DatasetRegistryImporter

importer = DatasetRegistryImporter()

# 导入指定文件
importer.import_datasets(json_path="./custom_datasets.json")
importer.import_strategies(json_path="./custom_strategies.json")

# 导出当前数据库配置到 JSON
importer.export_datasets("./backup_datasets.json")
```

## 添加新数据集

1. 在 `datasets.json` 中的 `datasets` 数组添加新条目：

```json
{
  "name": "my_dataset",
  "display_name": "My Dataset",
  "description": "我的自定义数据集",
  "num_classes": 10,
  "num_features": 784,
  "input_shape": "1,28,28",
  "data_type": "image",
  "task_type": "classification",
  "raw_dataset_module": "datasets.my_dataset.raw",
  "raw_dataset_class": "MyDatasetRawDataset",
  "preprocessor_module": "datasets.my_dataset.preprocess",
  "preprocessor_class": "MyDatasetPreprocessor",
  "partitioner_module": "datasets.my_dataset.partition",
  "partitioner_class": "MyDatasetPartitioner",
  "version": "1.0.0",
  "author": "Your Name",
  "source_url": "https://example.com",
  "license": "MIT",
  "train_samples": 50000,
  "test_samples": 10000,
  "extra_params": {"mean": [0.5], "std": [0.5]},
  "tags": ["image", "classification"],
  "status": "active"
}
```

2. 运行导入命令：

```bash
python scripts/register_datasets.py
```

## 注意事项

1. **编码**: JSON 文件必须使用 UTF-8 编码，确保中文正常显示
2. **字段类型**: JSON 中的 `extra_params`、`tags`、`param_schema`、`supported_datasets`、`default_params` 字段会自动转换为 JSON 字符串存储到数据库
3. **唯一性**: `name` 字段必须唯一，重复会触发更新（如果 `overwrite=True`）
4. **验证**: 导入前建议验证 JSON 格式正确性
