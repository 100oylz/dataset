# 添加新数据集示例

## 步骤1: 准备数据集实现代码

确保你已经在 `datasets/` 目录下实现了新数据集：

```
datasets/
└── my_dataset/
    ├── __init__.py
    ├── raw.py           # MyDatasetRawDataset
    ├── preprocess.py    # MyDatasetPreprocessor
    └── partition.py     # MyDatasetPartitioner
```

## 步骤2: 在 datasets.json 中添加配置

编辑 `datasets/configs/datasets.json`，在 `datasets` 数组中添加：

```json
{
  "name": "my_dataset",
  "display_name": "My Dataset 中文名",
  "description": "数据集的中文描述，介绍数据集的特点和用途",
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
  "author": "作者名",
  "source_url": "https://example.com/my-dataset",
  "license": "MIT",
  "train_samples": 50000,
  "test_samples": 10000,
  "extra_params": {
    "mean": [0.5],
    "std": [0.5]
  },
  "tags": ["image", "classification", "custom"],
  "status": "active"
}
```

## 步骤3: 更新划分策略支持的数据集列表

编辑 `datasets/configs/partition_strategies.json`，在每个策略的 `supported_datasets` 中添加新数据集名称：

```json
{
  "name": "iid",
  "display_name": "IID 划分",
  ...
  "supported_datasets": ["mnist", "cifar10", "fashion_mnist", "femnist", "my_dataset"]
}
```

## 步骤4: 导入到数据库

```bash
# 命令行方式
python scripts/register_datasets.py

# 或在 Python 代码中
from datasets import register_all
register_all()
```

## 步骤5: 验证

```python
from datasets import list_available_datasets, get_dataset_info

# 查看是否包含新数据集
print(list_available_datasets())

# 查看新数据集信息
info = get_dataset_info("my_dataset")
print(info)
```

## 完整示例

假设要添加一个名为 "SVHN" 的数据集：

1. 创建 `datasets/svhn/` 目录并实现相关类
2. 在 `datasets.json` 中添加 SVHN 配置
3. 在 `partition_strategies.json` 的 `supported_datasets` 中添加 "svhn"
4. 运行 `python scripts/register_datasets.py`
5. 完成！
