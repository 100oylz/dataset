# Utils 模块 - AI Agent 指引

> 为 AI Agent 提供的工具函数开发和维护指南

## 🎯 模块定位

Utils 模块是框架的**通用工具库**，提供与数据集无关的辅助功能：
1. 随机种子设置（确保实验可复现）
2. 设备管理（自动检测 GPU/CPU）
3. 文件操作（JSON 读写、目录创建）
4. 数据统计（类别分布计算）
5. 可视化（分布图表生成）
6. 性能分析（计时装饰器）

## 📁 文件职责

| 文件 | 职责 | 内容 |
|------|------|------|
| `helpers.py` | 工具函数实现 | 所有辅助函数的实现 |
| `__init__.py` | 统一导出 | 导出所有工具函数 |

## 🔧 常见任务

### 任务1: 添加新的工具函数

**步骤**:

1. 在 `helpers.py` 中实现函数

```python
# utils/helpers.py

def my_utility(param: str, option: bool = False) -> int:
    """
    工具函数的简短描述
    
    详细描述函数的用途、参数和返回值。
    可以包含使用示例。
    
    Args:
        param: 参数说明
        option: 可选参数说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 参数无效时抛出
        
    Example:
        >>> my_utility("test")
        42
        >>> my_utility("test", option=True)
        100
    """
    if not param:
        raise ValueError("param cannot be empty")
    
    result = 42
    if option:
        result = 100
    
    return result
```

2. 在 `__init__.py` 中导出

```python
# utils/__init__.py

from .helpers import (
    # ... 现有导出
    my_utility,  # 新添加
)

__all__ = [
    # ... 现有导出
    "my_utility",  # 新添加
]
```

### 任务2: 实现新的可视化功能

**场景**: 需要添加新的数据可视化功能

**示例**: 添加客户端数据量分布图

```python
# utils/helpers.py

def visualize_client_data_sizes(
    client_sizes: Dict[int, int],
    title: str = "Client Data Sizes",
    save_path: Optional[str] = None
) -> None:
    """
    可视化各客户端的数据量分布
    
    Args:
        client_sizes: {client_id: num_samples} 字典
        title: 图表标题
        save_path: 保存路径，None则显示
    """
    import matplotlib.pyplot as plt
    
    clients = list(client_sizes.keys())
    sizes = list(client_sizes.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(clients, sizes)
    plt.xlabel("Client ID")
    plt.ylabel("Number of Samples")
    plt.title(title)
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()
```

### 任务3: 实现数据验证功能

**示例**: 添加配置验证函数

```python
# utils/helpers.py

from typing import Dict, Any, List

def validate_config(config: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    验证配置字典是否包含所有必需字段
    
    Args:
        config: 配置字典
        required_fields: 必需字段列表
        
    Returns:
        验证是否通过
        
    Raises:
        ValueError: 缺少必需字段
    """
    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True
```

### 任务4: 修复设备检测问题

**症状**: `get_device()` 没有正确检测 GPU

**排查代码**:
```python
# 检查 PyTorch 是否能看到 GPU
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
```

**修复 `get_device()`**:
```python
def get_device(device: Optional[str] = None) -> torch.device:
    """
    获取计算设备
    
    优先级: CUDA > MPS (Apple Silicon) > CPU
    """
    if device is not None:
        return torch.device(device)
    
    # 检查 CUDA
    if torch.cuda.is_available():
        return torch.device("cuda")
    
    # 检查 MPS (Apple Silicon)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    
    # 默认 CPU
    return torch.device("cpu")
```

### 任务5: 修复随机种子设置不生效

**症状**: 设置种子后结果仍不固定

**完整修复**:
```python
def set_seed(seed: int = 42) -> None:
    """
    设置所有随机数生成器的种子
    """
    import random
    import numpy as np
    import torch
    
    # Python random
    random.seed(seed)
    
    # NumPy
    np.random.seed(seed)
    
    # PyTorch CPU
    torch.manual_seed(seed)
    
    # PyTorch CUDA
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)  # 多 GPU
        
        # 确保确定性行为
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

## 🚨 重要约束

### 1. 通用性原则

工具函数**必须**是通用的，不能依赖特定数据集或业务逻辑：

```python
# ✅ 正确 - 通用工具
def compute_class_distribution(labels):
    # 适用于任何标签列表
    pass

# ❌ 错误 - 与 MNIST 耦合
def compute_mnist_distribution(dataset):
    # 只适用于 MNIST
    pass
```

### 2. 异常处理

工具函数应妥善处理异常情况：

```python
# ✅ 正确 - 有异常处理
def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(path, 'r') as f:
        return json.load(f)

# ❌ 错误 - 无异常处理
def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:  # 可能抛出 FileNotFoundError
        return json.load(f)
```

### 3. 类型注解

所有工具函数都应有完整的类型注解：

```python
# ✅ 正确
def process_data(data: List[int], threshold: float = 0.5) -> List[int]:
    pass

# ❌ 错误
def process_data(data, threshold=0.5):
    pass
```

### 4. 文档字符串

使用 Google 风格的 docstring：

```python
def my_function(param1: int, param2: str) -> bool:
    """
    简短描述
    
    详细描述。
    
    Args:
        param1: 参数1说明
        param2: 参数2说明
        
    Returns:
        返回值说明
        
    Raises:
        ValueError: 参数无效时抛出
    """
    pass
```

## 🔗 模块关系

```
utils/
    └── helpers.py
            ├── set_seed() → 被所有模块使用（确保可复现性）
            ├── get_device() → 被 database/DynamicImporter 使用
            ├── ensure_dir() → 被 raw.py 使用（创建数据目录）
            ├── save_json/load_json() → 被 database 使用
            ├── compute_class_distribution() → 被 partitioner_base.py 使用
            ├── visualize_distribution() → 被用户代码使用
            └── timer() → 被开发调试使用
```

## 🐛 调试技巧

### 检查随机种子是否生效

```python
from utils import set_seed

set_seed(42)

import torch
import numpy as np
import random

# 这些值应该每次运行都相同
print(f"random: {random.random()}")
print(f"numpy: {np.random.rand()}")
print(f"torch: {torch.rand(1)}")
```

### 检查设备检测

```python
from utils import get_device

device = get_device()
print(f"Selected device: {device}")

# 测试是否能在设备上运行
import torch
x = torch.rand(3, 3).to(device)
print(f"Tensor device: {x.device}")
```

### 性能分析

```python
from utils import timer
import cProfile
import pstats

# 方法1: 使用装饰器
@timer
def slow_function():
    import time
    time.sleep(1)

slow_function()

# 方法2: 使用 cProfile（更详细）
def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 你的代码
    result = some_expensive_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 打印前10个
    
    return result
```

## 📚 相关文档

- [../README.md](../README.md) - 项目总览
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - 架构设计
- [../core/AGENTS.md](../core/AGENTS.md) - Core 模块指引
