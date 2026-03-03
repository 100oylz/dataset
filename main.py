from database import DatasetFactory, DatasetRegistry
from torch.utils.data.dataloader import DataLoader

# 初始化注册中心
registry = DatasetRegistry()
registry.load_from_database()

# 使用工厂创建管理器
factory = DatasetFactory(registry)
manager = factory.create(
    dataset_name="mnist",
    data_root="./data",
    num_clients=100,
    partition_strategy="dirichlet",
    partition_params={"alpha": 0.05}
)

# 准备数据
manager.prepare_data()

# 获取客户端数据加载器
loader = manager.get_client_loader(0, batch_size=3)
print(manager.dataset_name)
print(manager.get_data_info())
print(manager.get_partition_info())
dataloader=DataLoader(manager.get_client_dataset(0),batch_size=32)
for data,label in dataloader:
    print(data)
    print(label)
    break

# ========== 新增：可视化客户端类别分布 ==========
print("\n" + "=" * 50)
print("生成客户端类别分布图...")
print("=" * 50)

# 方式1: 保存为图片文件
manager.visualize_client_distribution(
    title="MNIST - Dirichlet Partition (alpha=0.05)",
    save_path="./results/client_distribution.png"
)

# 方式2: 直接显示（不保存）
# manager.visualize_client_distribution(title="MNIST Distribution")

print("\n分布图已保存至: ./results/client_distribution.png")
print("图表说明:")
print("  - 左图: 堆叠柱状图 - 显示每个客户端各类别的样本数量")
print("  - 右图: 热力图 - 显示每个客户端各类别的比例（Non-IID程度）")
