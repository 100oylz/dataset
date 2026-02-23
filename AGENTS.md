# AI Agent 指引文档

> 本文档为 AI Agent 提供项目导航和最佳实践指导

## 🎯 项目核心目标

本项目是一个**联邦学习数据集管理框架**，旨在：
- 为联邦学习实验提供标准化的数据管理能力
- 支持多种数据集、预处理和划分策略的灵活组合
- 通过动态导入系统支持运行时数据集发现

## 📁 模块导航

### 1. Core 模块 (`core/`)
**定位**: 抽象基类定义

**核心类**:
- `RawDatasetBase`: 原始数据集基类
  - 职责: 数据下载、加载、提供元信息
  - 关键属性: `num_classes`, `input_shape`, `train_samples`
  
- `PreprocessorBase`: 预处理器基类
  - 职责: 数据预处理、增强、归一化
  - 关键方法: `fit()`, `get_train_transform()`, `get_test_transform()`
  
- `PartitionerBase`: 划分器基类
  - 职责: 将训练数据划分为多个客户端子集
  - 关键方法: `partition()`, 返回 `{client_id: [indices]}`
  
- `DatasetManagerBase`: 管理器基类
  - 职责: 协调 raw/preprocessor/partitioner
  - 关键方法: `prepare_data()`, `get_client_loader()`

**修改建议**:
- 修改基类会影响所有数据集实现，需谨慎
- 添加新的划分策略类型时，在此定义抽象接口

### 2. Database 模块 (`database/`)
**定位**: 数据注册和动态导入

**核心类**:
- `DatasetRegistration`: 数据集注册信息数据类
  - 包含模块路径和类名信息，用于动态导入
  - 字段: `raw_dataset_module`, `raw_dataset_class`, ...
  
- `DatasetRegistry`: 数据集注册中心（单例）
  - 管理所有已注册数据集的元数据
  - 关键方法: `register()`, `get()`, `list_datasets()`
  
- `DynamicImporter`: 动态导入器
  - 根据模块路径动态导入类
  - 关键方法: `import_class()`, `create_instance()`
  
- `DatasetFactory`: 数据集工厂
  - 通过数据集名称创建完整管理器
  - 关键方法: `create()`

**修改建议**:
- 添加新数据集时，需要在此注册
- 修改导入逻辑时需考虑缓存机制

### 3. Datasets 模块 (`datasets/`)
**定位**: 具体数据集实现

**每个数据集包含**:
- `raw.py`: 原始数据集类（继承 `RawDatasetBase`）
- `preprocess.py`: 预处理器类（继承 `PreprocessorBase`）
- `partition.py`: 划分器类（继承 `PartitionerBase` 的子类）

**现有数据集**:
- `mnist/`: MNIST 手写数字
- `cifar10/`: CIFAR-10 彩色图像
- `fashion_mnist/`: Fashion-MNIST 时尚物品

**修改建议**:
- 添加新数据集时，遵循现有目录结构
- 数据集特定常量（如 mean/std）在 preprocessor 中定义
- 划分器继承核心划分器基类，添加数据集特定逻辑

### 4. Configs 模块 (`configs/`)
**定位**: 配置管理

**核心类**:
- `DatasetConfig`: 数据集配置数据类
- `DEFAULT_DATASET_CONFIGS`: 默认数据集配置字典
- `DEFAULT_PARTITION_CONFIGS`: 默认划分策略配置

**修改建议**:
- 添加新数据集时，需在 `DEFAULT_DATASET_CONFIGS` 中添加配置
- 配置包含模块路径信息，用于动态导入

### 5. Utils 模块 (`utils/`)
**定位**: 通用工具函数

**核心函数**:
- `set_seed()`: 设置随机种子
- `get_device()`: 获取计算设备
- `compute_class_distribution()`: 计算类别分布
- `visualize_distribution()`: 可视化数据分布

**修改建议**:
- 添加通用的、与数据集无关的辅助函数
- 避免在此处添加数据集特定逻辑

## 🔧 常见任务指引

### 任务1: 添加新数据集

**步骤**:
1. 创建目录 `datasets/my_dataset/`
2. 实现 `raw.py`:
   ```python
   from core import RawDatasetBase
   class MyDatasetRawDataset(RawDatasetBase):
       @property
       def num_classes(self) -> int:
           return 10
       # ... 实现其他抽象方法
   ```
3. 实现 `preprocess.py`:
   ```python
   from core import PreprocessorBase
   class MyDatasetPreprocessor(PreprocessorBase):
       # ... 实现数据特定预处理
   ```
4. 实现 `partition.py`:
   ```python
   from core import IIDPartitioner
   class MyDatasetIIDPartitioner(IIDPartitioner):
       # ... 实现划分逻辑
   ```
5. 更新 `datasets/__init__.py` 导出组件
6. 在 `configs/default_configs.py` 添加配置
7. 注册到数据库（可选）

### 任务2: 添加新划分策略

**步骤**:
1. 在 `core/partitioner_base.py` 创建新的划分器基类（如需要）
2. 在 `core/__init__.py` 导出
3. 为每个数据集创建具体实现（如 `MNISTNewPartitioner`）
4. 在 `configs/default_configs.py` 添加策略配置
5. 更新 `database/models.py` 中的 `PartitionStrategy`

### 任务3: 修改数据预处理逻辑

**步骤**:
1. 定位到数据集的 `preprocess.py`
2. 修改相应数据集的预处理器类
3. 注意保持 `get_train_transform()` 和 `get_test_transform()` 接口一致
4. 如需添加新参数，更新配置和构造函数

### 任务4: 修复数据加载问题

**检查清单**:
- [ ] `raw.py` 中的 `download()` 是否正确实现
- [ ] `load_train_data()` 和 `load_test_data()` 是否返回 PyTorch Dataset
- [ ] 数据路径是否正确处理
- [ ] 检查 `data_root` 参数传递

## 🚨 注意事项

### 关键约束

1. **类型注解**: 所有公共 API 必须使用类型注解
2. **抽象方法**: 基类中的抽象方法必须全部实现
3. **模块路径**: 配置中的模块路径必须正确，否则动态导入会失败
4. **单例模式**: `DatasetRegistry` 是单例，注意状态管理

### 常见陷阱

1. **循环导入**: `core` 模块不应导入 `datasets` 模块
2. **硬编码路径**: 避免在代码中硬编码数据集路径，使用 `data_root` 参数
3. **状态管理**: 预处理器的状态（如 mean/std）需要正确处理
4. **随机种子**: 划分操作需要设置随机种子以保证可复现性

### 测试建议

- 每个数据集实现都应测试：
  - 数据下载是否正常
  - 数据加载是否正确
  - 预处理变换是否工作
  - 划分结果是否符合预期
  - 客户端数据加载器是否能正常迭代

## 🔗 相关文件速查

| 任务 | 相关文件 |
|------|----------|
| 添加数据集 | `datasets/new_dataset/`, `configs/default_configs.py` |
| 修改划分策略 | `core/partitioner_base.py`, `datasets/*/partition.py` |
| 修改预处理 | `datasets/*/preprocess.py` |
| 修改注册逻辑 | `database/dataset_registry.py`, `database/dynamic_importer.py` |
| 修改配置系统 | `configs/default_configs.py` |
| 添加工具函数 | `utils/helpers.py` |

## 📝 代码风格

- 使用 Python 3.8+ 类型注解
- 遵循 PEP 8 规范
- 所有类和方法都需要 docstring
- 使用 `TODO:` 标记待实现代码
