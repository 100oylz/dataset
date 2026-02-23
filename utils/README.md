# Utils 模块

> 联邦学习数据集管理框架的通用工具模块

## 概述

Utils 模块提供通用的辅助函数，用于随机种子设置、设备管理、文件操作、数据统计和可视化等功能。

## 模块结构

```
utils/
├── __init__.py              # 导出所有工具函数
└── helpers.py               # 工具函数实现
```

## 核心函数详解

### 1. 随机种子设置

#### set_seed(seed: int = 42) -> None

设置所有随机数生成器的种子，确保实验可复现。

**影响的库**:
- Python `random`
- NumPy
- PyTorch (CPU 和 CUDA)

**示例**:
```python
from utils import set_seed

# 设置随机种子
set_seed(42)

# 后续随机操作将产生确定性的结果
import torch
print(torch.rand(3))  # 每次运行结果相同
```

### 2. 设备管理

#### get_device(device: Optional[str] = None) -> torch.device

获取计算设备，自动检测可用设备或返回指定设备。

**参数**:
- `device`: 指定设备名称（"cuda", "cpu", "mps"），None 则自动选择

**返回值**: `torch.device` 对象

**设备优先级**:
1. CUDA (NVIDIA GPU)
2. MPS (Apple Silicon)
3. CPU

**示例**:
```python
from utils import get_device

# 自动选择设备
device = get_device()
print(device)  # cuda:0 或 cpu

# 指定设备
device = get_device("cuda")
device = get_device("cpu")
```

### 3. 文件操作

#### ensure_dir(path: str) -> str

确保目录存在，不存在则创建。

**示例**:
```python
from utils import ensure_dir

# 确保目录存在
data_dir = ensure_dir("./data/mnist")
# 如果不存在，自动创建目录
```

#### save_json(data: Dict[str, Any], path: str) -> None

保存字典到 JSON 文件。

**示例**:
```python
from utils import save_json

data = {"num_clients": 10, "alpha": 0.5}
save_json(data, "./config.json")
```

#### load_json(path: str) -> Dict[str, Any]

从 JSON 文件加载字典。

**示例**:
```python
from utils import load_json

data = load_json("./config.json")
print(data["num_clients"])  # 10
```

### 4. 数据统计

#### compute_class_distribution(labels: Union[List[int], np.ndarray]) -> Dict[int, int]

计算类别分布。

**参数**:
- `labels`: 标签列表或数组

**返回值**: `{label: count}` 字典

**示例**:
```python
from utils import compute_class_distribution
import numpy as np

labels = [0, 1, 0, 2, 1, 0, 0]
distribution = compute_class_distribution(labels)
print(distribution)  # {0: 4, 1: 2, 2: 1}
```

### 5. 可视化

#### visualize_distribution(distribution: Dict[int, Dict[int, int]], title: str = "Data Distribution", save_path: Optional[str] = None) -> None

可视化数据分布，绘制堆叠柱状图。

**参数**:
- `distribution`: 分布字典 `{client_id: {label: count}}`
- `title`: 图表标题
- `save_path`: 保存路径，None 则显示图表

**示例**:
```python
from utils import visualize_distribution

# 示例：3 个客户端，10 个类别的分布
distribution = {
    0: {0: 50, 1: 60, 2: 45, ...},  # 客户端 0 的分布
    1: {0: 40, 1: 55, 2: 50, ...},  # 客户端 1 的分布
    2: {0: 60, 1: 45, 2: 55, ...},  # 客户端 2 的分布
}

# 显示图表
visualize_distribution(distribution, title="Client Data Distribution")

# 保存图表
visualize_distribution(distribution, save_path="./distribution.png")
```

### 6. 格式化

#### format_bytes(size: int) -> str

格式化字节大小为人类可读格式。

**参数**:
- `size`: 字节数

**返回值**: 格式化字符串（如 "1.5 MB"）

**示例**:
```python
from utils import format_bytes

print(format_bytes(1024))        # "1.00 KB"
print(format_bytes(1536000))     # "1.46 MB"
print(format_bytes(1073741824))  # "1.00 GB"
```

### 7. 性能分析

#### timer(func)

计时装饰器，用于测量函数执行时间。

**示例**:
```python
from utils import timer

@timer
def my_function():
    # 耗时操作
    import time
    time.sleep(1)

my_function()
# 输出: my_function took 1.00 seconds
```

## 使用示例

### 完整示例: 实验初始化

```python
from utils import set_seed, get_device, ensure_dir, save_json
import time

# 1. 设置随机种子
set_seed(42)

# 2. 获取计算设备
device = get_device()
print(f"Using device: {device}")

# 3. 确保输出目录存在
output_dir = ensure_dir("./experiments/exp_001")

# 4. 保存配置
config = {
    "seed": 42,
    "device": str(device),
    "num_clients": 10,
    "timestamp": time.time(),
}
save_json(config, f"{output_dir}/config.json")
```

### 完整示例: 数据分布分析

```python
from utils import compute_class_distribution, visualize_distribution
from torch.utils.data import Dataset

# 假设有客户端数据
client_datasets: Dict[int, Dataset] = {...}

# 计算每个客户端的类别分布
distribution = {}
for client_id, dataset in client_datasets.items():
    # 提取标签
    labels = [label for _, label in dataset]
    distribution[client_id] = compute_class_distribution(labels)

# 可视化分布
visualize_distribution(
    distribution,
    title="Federated Data Distribution",
    save_path="./distribution.png"
)
```

### 完整示例: 性能分析

```python
from utils import timer, format_bytes
import sys

@timer
def load_large_dataset():
    # 模拟加载大数据集
    import time
    time.sleep(2)
    return [1] * 1000000

@timer
def process_data(data):
    # 模拟数据处理
    return [x * 2 for x in data]

# 执行
data = load_large_dataset()  # 输出: load_large_dataset took 2.00 seconds
result = process_data(data)   # 输出: process_data took X.XX seconds

# 查看内存占用
size = sys.getsizeof(result)
print(f"Result size: {format_bytes(size)}")
```

## 添加新工具函数

添加新工具函数时，请遵循以下步骤：

1. 在 `helpers.py` 中实现函数
2. 添加类型注解
3. 添加 docstring
4. 在 `__init__.py` 中导出

**示例**:
```python
# utils/helpers.py

def my_new_utility(param: str) -> int:
    """
    新工具函数的简短描述
    
    详细描述函数的功能、参数和返回值。
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
        
    Example:
        >>> my_new_utility("test")
        42
    """
    return 42

# utils/__init__.py
from .helpers import (
    # ... 现有导出
    my_new_utility,
)

__all__ = [
    # ... 现有导出
    "my_new_utility",
]
```

## 注意事项

1. **通用性**: 工具函数应具有通用性，不依赖于特定数据集或业务逻辑
2. **类型安全**: 所有函数都应使用类型注解
3. **异常处理**: 考虑边界情况（如目录创建失败、文件不存在等）
4. **性能**: 高频调用的函数应注意性能优化
