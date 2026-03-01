"""
客户端类别分布可视化示例

展示如何使用 FederatedDatasetManager 生成客户端类别分布图
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import DatasetFactory, DatasetRegistry


def main():
    # 初始化注册中心
    registry = DatasetRegistry()
    registry.load_from_database()
    
    # 使用工厂创建管理器
    factory = DatasetFactory(registry)
    
    print("=" * 60)
    print("示例 1: Dirichlet 划分 (Non-IID) 的分布图")
    print("=" * 60)
    
    manager_dirichlet = factory.create(
        dataset_name="mnist",
        data_root="./data",
        num_clients=10,
        partition_strategy="dirichlet",
        partition_params={"alpha": 0.5}  # alpha越小越Non-IID
    )
    
    # 准备数据
    manager_dirichlet.prepare_data()
    
    # 获取划分信息
    partition_info = manager_dirichlet.get_partition_info()
    print(f"\n划分策略: {partition_info['partition_strategy']}")
    print(f"策略类型: {partition_info['strategy_type']}")
    print(f"客户端数量: {partition_info['num_clients']}")
    
    # 显示统计信息
    stats = partition_info.get("statistics", {})
    if "statistics" in stats:
        s = stats["statistics"]
        print(f"\n样本统计:")
        print(f"  - 平均每客户端样本数: {s.get('mean_samples_per_client', 'N/A'):.1f}")
        print(f"  - 样本标准差: {s.get('std_samples_per_client', 'N/A'):.1f}")
        print(f"  - 最小样本数: {s.get('min_samples', 'N/A')}")
        print(f"  - 最大样本数: {s.get('max_samples', 'N/A')}")
        print(f"  - 不平衡比例: {s.get('imbalance_ratio', 'N/A'):.2f}")
    
    # 生成并保存分布图
    print("\n生成分布图...")
    manager_dirichlet.visualize_client_distribution(
        title="MNIST - Dirichlet Partition (alpha=0.5)",
        save_path="./results/mnist_dirichlet_dist.png"
    )
    print("保存至: ./results/mnist_dirichlet_dist.png")
    
    print("\n" + "=" * 60)
    print("示例 2: IID 划分的分布图")
    print("=" * 60)
    
    manager_iid = factory.create(
        dataset_name="mnist",
        data_root="./data",
        num_clients=10,
        partition_strategy="iid"
    )
    
    manager_iid.prepare_data()
    
    # 直接显示（不保存）
    print("\n显示 IID 分布图...")
    manager_iid.visualize_client_distribution(
        title="MNIST - IID Partition",
        save_path="./results/mnist_iid_dist.png"
    )
    print("保存至: ./results/mnist_iid_dist.png")
    
    print("\n" + "=" * 60)
    print("示例 3: Pathological 划分 (极端 Non-IID)")
    print("=" * 60)
    
    manager_path = factory.create(
        dataset_name="mnist",
        data_root="./data",
        num_clients=10,
        partition_strategy="pathological",
        partition_params={"shards_per_client": 2}  # 每个客户端只有2个类别
    )
    
    manager_path.prepare_data()
    
    print("\n生成分布图...")
    manager_path.visualize_client_distribution(
        title="MNIST - Pathological Partition (2 shards/client)",
        save_path="./results/mnist_pathological_dist.png",
        figsize=(14, 6),  # 自定义图像尺寸
        cmap="tab10"      # 使用不同颜色映射
    )
    print("保存至: ./results/mnist_pathological_dist.png")
    
    print("\n" + "=" * 60)
    print("示例 4: 使用 CIFAR-10")
    print("=" * 60)
    
    try:
        manager_cifar = factory.create(
            dataset_name="cifar10",
            data_root="./data",
            num_clients=5,
            partition_strategy="dirichlet",
            partition_params={"alpha": 0.3}
        )
        
        manager_cifar.prepare_data()
        
        print("\n生成 CIFAR-10 分布图...")
        manager_cifar.visualize_client_distribution(
            title="CIFAR-10 - Dirichlet Partition (alpha=0.3)",
            save_path="./results/cifar10_dirichlet_dist.png"
        )
        print("保存至: ./results/cifar10_dirichlet_dist.png")
    except Exception as e:
        print(f"CIFAR-10 示例失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
