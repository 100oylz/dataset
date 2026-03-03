# Database 模块使用说明

本模块提供基于 MySQL 的数据集注册、管理和动态导入功能。

## 快速开始

### 1. 启动 MySQL 容器

使用 docker-compose 启动 MySQL 服务：

```bash
# 启动 MySQL
docker-compose up -d mysql

# 查看日志
docker-compose logs -f mysql

# 停止服务
docker-compose down

# 可选：启动 Adminer 数据库管理界面
docker-compose --profile admin up -d
```

### 2. 环境变量配置

环境变量通过 `.envrc` 自动加载（需要安装 [direnv](https://direnv.net/)）：

```bash
# 重新加载环境变量
direnv allow

# 查看当前配置
echo $DATABASE_URL
echo $MYSQL_HOST
echo $MYSQL_PORT
echo $MYSQL_DATABASE
```

可配置的环境变量：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MYSQL_HOST` | localhost | MySQL 主机地址 |
| `MYSQL_PORT` | 3306 | MySQL 端口 |
| `MYSQL_DATABASE` | fl_dataset_db | 数据库名 |
| `MYSQL_USER` | fl_user | 数据库用户 |
| `MYSQL_PASSWORD` | flpassword | 用户密码 |
| `MYSQL_ROOT_PASSWORD` | rootpassword | root 密码 |
| `MYSQL_POOL_SIZE` | 5 | 连接池大小 |
| `MYSQL_MAX_OVERFLOW` | 10 | 最大溢出连接 |

### 3. 使用示例

#### 初始化数据库连接

```python
from database import init_database, get_db

# 测试连接
if init_database():
    print("数据库连接成功")
    
    # 获取数据库连接
    db = get_db()
    
    # 执行查询
    result = db.fetchone("SELECT VERSION() as version")
    print(f"MySQL 版本: {result['version']}")
```

#### 数据集注册

```python
from database import DatasetRegistry, DatasetRegistration

# 获取注册中心
registry = DatasetRegistry()

# 加载数据库中的数据集
registry.load_from_database()

# 获取数据集信息
mnist = registry.get("mnist")
print(f"MNIST 训练样本数: {mnist.train_samples}")

# 列出所有数据集
datasets = registry.list_datasets()
for ds in datasets:
    print(f"- {ds.name}: {ds.description}")
```

#### 动态导入组件

```python
from database import DynamicImporter, DatasetRegistration

# 假设已有注册信息
registration = registry.get("mnist")

# 创建原始数据集实例
raw_dataset = DynamicImporter.create_raw_dataset(
    registration=registration,
    data_root="./data"
)

# 创建预处理器
preprocessor = DynamicImporter.create_preprocessor(
    registration=registration
)

# 创建划分器
partitioner = DynamicImporter.create_partitioner(
    registration=registration,
    num_clients=10,
    strategy="dirichlet",
    alpha=0.5
)
```

#### 使用数据集工厂

```python
from database import DatasetFactory

# 创建工厂
factory = DatasetFactory()

# 列出可用数据集
print(factory.list_available_datasets())

# 创建完整的管理器
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=10,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.5}
)

# 准备数据
manager.prepare_data()

# 获取客户端数据加载器
loader = manager.get_client_loader(client_id=0, batch_size=32)
```

#### 划分策略管理

```python
from database import PartitionStrategyRegistry

# 获取策略注册中心
strategy_registry = PartitionStrategyRegistry()

# 获取策略
iid_strategy = strategy_registry.get("iid")
print(f"IID 策略: {iid_strategy.description}")

# 列出所有策略
strategies = strategy_registry.list_strategies()

# 获取数据集支持的策略
supported = strategy_registry.get_supported_strategies("mnist")
```

#### 划分结果存储

```python
from database import PartitionResultRegistry, PartitionResult

# 获取结果注册中心
result_registry = PartitionResultRegistry()

# 保存划分结果
result = PartitionResult(
    dataset_name="mnist",
    strategy_name="dirichlet",
    num_clients=10,
    params={"alpha": 0.5},
    client_indices={0: [1, 2, 3], 1: [4, 5, 6]},
    total_samples=60000,
    fingerprint="abc123"
)
result_id = result_registry.save(result)

# 获取划分结果
saved_result = result_registry.get(
    dataset_name="mnist",
    strategy_name="dirichlet",
    num_clients=10,
    fingerprint="abc123"
)
```

## 数据库表结构

### dataset_registrations
存储数据集注册信息

### partition_strategies
存储支持的划分策略

### partition_results
存储划分结果（用于缓存）

## 故障排除

### 连接失败

```bash
# 检查 MySQL 容器状态
docker-compose ps

# 查看日志
docker-compose logs mysql

# 重新启动
docker-compose restart mysql
```

### 数据库未初始化

首次启动时会自动执行 `database/init/` 目录下的 SQL 文件初始化数据库。

如需手动初始化：

```bash
docker-compose exec mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "source /docker-entrypoint-initdb.d/01_init_tables.sql"
docker-compose exec mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} -e "source /docker-entrypoint-initdb.d/02_seed_data.sql"
```

## 数据库检查工具

项目提供了数据库检查工具 `scripts/check_database.py`，用于诊断和修复数据库问题：

```bash
# 检查数据库表结构和内容
python scripts/check_database.py

# 修复中文乱码问题（使用 ftfy 库）
python scripts/check_database.py --fix-mojibake

# 显示帮助
python scripts/check_database.py --help
```

### 功能说明

- **表结构检查**: 验证所有必需的表是否存在
- **数据集记录检查**: 显示数据集注册信息
- **划分策略检查**: 显示支持的划分策略
- **乱码修复**: 自动检测并修复数据库中的 mojibake 乱码

### 中文乱码问题

如果遇到中文显示乱码，可以使用 `--fix-mojibake` 选项修复：

```bash
python scripts/check_database.py --fix-mojibake
```

修复过程会：
1. 扫描所有可能包含乱码的字段
2. 使用 ftfy 库尝试修复乱码
3. 显示修复前后的对比
4. 将修复后的内容更新到数据库
