# Database 模块 - AI Agent 指引

> 为 AI Agent 提供的 Database 模块开发和维护指南

## 🎯 模块定位

Database 模块是框架的**元数据管理中心**和**动态导入引擎**。它负责：
1. 存储和管理数据集的注册信息
2. 支持运行时动态发现和加载数据集
3. 提供工厂模式创建完整的数据集组件

## 📁 文件职责

| 文件 | 核心职责 | 关键类/函数 |
|------|----------|-------------|
| `models.py` | 数据模型定义 | `DatasetRegistration`, `PartitionStrategy` |
| `dataset_registry.py` | 注册中心管理 | `DatasetRegistry`, `PartitionStrategyRegistry` |
| `dynamic_importer.py` | 动态导入逻辑 | `DynamicImporter`, `DatasetFactory` |
| `__init__.py` | 统一导出接口 | - |

## 🔧 常见任务

### 任务1: 添加新数据集到注册表

**场景**: 在 `datasets/` 下实现了新数据集，需要注册到数据库

**步骤**:
1. 确保数据集组件已实现（raw/preprocess/partition）
2. 在 `configs/default_configs.py` 添加配置
3. 创建 `DatasetRegistration` 实例
4. 使用 `DatasetRegistry` 注册
5. 保存到数据库

**示例**:
```python
from database import DatasetRegistration, DatasetRegistry

registration = DatasetRegistration(
    name="my_dataset",
    display_name="My Dataset",
    description="自定义数据集",
    num_classes=10,
    input_shape=(3, 32, 32),
    # 模块路径 - 必须正确！
    raw_dataset_module="datasets.my_dataset.raw",
    raw_dataset_class="MyDatasetRawDataset",
    preprocessor_module="datasets.my_dataset.preprocess",
    preprocessor_class="MyDatasetPreprocessor",
    partitioner_module="datasets.my_dataset.partition",
    partitioner_class="MyDatasetPartitioner",
)

registry = DatasetRegistry()
registry.register(registration)
registry.save_to_database()
```

### 任务2: 修复动态导入失败问题

**症状**: `ImportError` 或 `AttributeError` 在动态导入时抛出

**排查步骤**:
1. 检查模块路径是否正确
2. 检查类名是否拼写正确
3. 确保模块在 Python 路径中
4. 检查是否有循环导入

**调试代码**:
```python
from database import DynamicImporter

# 测试导入
try:
    cls = DynamicImporter.import_class(
        "datasets.mnist.raw",
        "MNISTRawDataset"
    )
    print(f"成功导入: {cls}")
except ImportError as e:
    print(f"导入失败: {e}")
except AttributeError as e:
    print(f"类不存在: {e}")
```

### 任务3: 修改数据集注册信息

**场景**: 需要更新已注册数据集的元信息

**方法**:
```python
from database import DatasetRegistry

registry = DatasetRegistry()
registry.load_from_database()

# 更新字段
registry.update("mnist", {
    "description": "新的描述",
    "num_classes": 10,
})

# 保存
registry.save_to_database()
```

### 任务4: 实现数据库持久化

**当前状态**: `load_from_database()` 和 `save_to_database()` 是 TODO 状态

**实现建议**:
```python
# dataset_registry.py

class DatasetRegistry:
    def load_from_database(self) -> int:
        """从数据库加载"""
        # 使用 SQLAlchemy 或原始 SQL
        import sqlite3  # 或其他数据库驱动
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dataset_registrations WHERE status='active'")
        
        for row in cursor.fetchall():
            registration = DatasetRegistration(
                id=row[0],
                name=row[1],
                # ... 映射其他字段
            )
            self._datasets[registration.name] = registration
        
        conn.close()
        return len(self._datasets)
```

### 任务5: 扩展 DatasetRegistration 字段

**场景**: 需要存储更多数据集元信息

**步骤**:
1. 在 `models.py` 的 `DatasetRegistration` 中添加新字段
2. 更新 `to_dict()` 和 `from_dict()` 方法
3. 更新数据库表结构（`DATASET_TABLE_SQL`）
4. 更新所有使用 `DatasetRegistration` 的地方

**示例**:
```python
# models.py

@dataclass
class DatasetRegistration:
    # ... 现有字段
    
    # 新字段
    dataset_url: str = ""  # 数据集下载URL
    paper_title: str = ""  # 相关论文标题
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            # ... 现有字段
            "dataset_url": self.dataset_url,
            "paper_title": self.paper_title,
        }
```

## 🚨 重要约束

### 1. 模块路径规范

模块路径必须使用**点分表示法**，相对于项目根目录：

```python
# ✅ 正确
raw_dataset_module="datasets.mnist.raw"

# ❌ 错误
raw_dataset_module="datasets/mnist/raw.py"
raw_dataset_module="./datasets/mnist/raw"
```

### 2. 单例模式注意事项

`DatasetRegistry` 和 `PartitionStrategyRegistry` 都是单例：

```python
# 这两个是同一个实例
registry1 = DatasetRegistry()
registry2 = DatasetRegistry()
assert registry1 is registry2  # True
```

**注意**: 在测试时需要重置状态：
```python
# 测试后清理
registry = DatasetRegistry()
registry.clear()
```

### 3. 动态导入缓存

`DynamicImporter` 使用类级缓存：

```python
# 第一次导入 - 实际执行导入
cls1 = DynamicImporter.import_class("datasets.mnist.raw", "MNISTRawDataset")

# 第二次导入 - 从缓存返回
cls2 = DynamicImporter.import_class("datasets.mnist.raw", "MNISTRawDataset")

assert cls1 is cls2  # True
```

如需重新导入（如代码更新后）：
```python
DynamicImporter.clear_cache()
```

### 4. 数据库连接管理

如果实现数据库持久化，注意连接管理：

```python
# 推荐：使用上下文管理器
class DatasetRegistry:
    def __enter__(self):
        self.conn = create_connection()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# 使用
with DatasetRegistry() as registry:
    registry.load_from_database()
```

## 🔗 模块关系

```
database/
    ├── models.py
    │       ├── DatasetRegistration
    │       └── PartitionStrategy
    │
    ├── dataset_registry.py
    │       ├── DatasetRegistry (使用 DatasetRegistration)
    │       └── PartitionStrategyRegistry (使用 PartitionStrategy)
    │
    └── dynamic_importer.py
            ├── DynamicImporter (导入 core/ 中的类)
            └── DatasetFactory (使用 DatasetRegistry 和 DynamicImporter)
```

## 📝 数据流向

```
configs/default_configs.py
        ↓
DatasetRegistration (创建)
        ↓
DatasetRegistry.register() (注册)
        ↓
DatasetRegistry.save_to_database() (持久化)
        ↓
DatasetRegistry.load_from_database() (加载)
        ↓
DatasetFactory.create() (使用)
        ↓
DynamicImporter.import_class() (动态导入)
        ↓
core/ 中的类实例化
```

## 🐛 常见问题

### Q: 动态导入返回 None

**原因**: 
- 模块路径错误
- 类名拼写错误
- 模块不在 Python 路径中

**解决**:
```python
import sys
print(sys.path)  # 检查路径

# 手动测试导入
try:
    import datasets.mnist.raw as mod
    print(dir(mod))  # 查看可用属性
    print(hasattr(mod, "MNISTRawDataset"))
except ImportError as e:
    print(e)
```

### Q: 注册中心数据在程序重启后丢失

**原因**: 未实现数据库持久化，只保存在内存中

**解决**: 在程序启动时调用 `load_from_database()`，结束时调用 `save_to_database()`

### Q: 单例导致测试相互影响

**解决**: 在每个测试后清理状态
```python
def tearDown(self):
    registry = DatasetRegistry()
    registry.clear()
```

## 📚 相关文档

- [../README.md](../README.md) - 项目总览
- [../core/AGENTS.md](../core/AGENTS.md) - Core 模块指引
- [../datasets/AGENTS.md](../datasets/AGENTS.md) - Datasets 模块指引
