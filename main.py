from database import DatasetFactory, DatasetRegistry

# 初始化注册中心
registry = DatasetRegistry()
registry.load_from_database()

# 使用工厂创建管理器
factory = DatasetFactory(registry)
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
loader = manager.get_client_loader(0, batch_size=32)

print(manager.dataset_name)
print(manager.get_data_info())