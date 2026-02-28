"""
数据集使用示例

展示如何使用联邦学习数据集管理框架
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datasets import create_federated_manager


def example_basic_usage():
    """示例1: 基本使用 - 使用create_federated_manager便捷函数"""
    print("\n" + "="*70)
    print("示例1: 使用create_federated_manager便捷函数")
    print("="*70)
    
    # 创建MNIST联邦学习管理器（自动使用torchvision下载）
    manager = create_federated_manager(
        dataset_name="mnist",
        data_root="./data",
        num_clients=5,
        partition_strategy="iid",
        seed=42
    )
    
    # 准备数据（自动下载、预处理、划分）
    print("\n准备数据（torchvision下载）...")
    manager.prepare_data()
    
    # 获取数据集信息
    info = manager.get_data_info()
    print(f"\n数据集信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 获取各客户端的数据加载器
    print(f"\n各客户端数据:")
    for client_id in range(5):
        loader = manager.get_client_loader(client_id, batch_size=32)
        print(f"  客户端 {client_id}: {len(loader.dataset)} 样本")
    
    # 获取测试数据加载器
    test_loader = manager.get_test_loader(batch_size=256)
    print(f"\n测试集: {len(test_loader.dataset)} 样本")


def example_different_strategies():
    """示例2: 不同划分策略对比"""
    print("\n" + "="*70)
    print("示例2: 不同划分策略对比")
    print("="*70)
    
    strategies = [
        ("iid", {}),
        ("dirichlet", {"alpha": 0.5}),
        ("pathological", {"shards_per_client": 2}),
    ]
    
    for strategy, params in strategies:
        print(f"\n{'-'*50}")
        print(f"策略: {strategy}, 参数: {params}")
        print(f"{'-'*50}")
        
        # 创建管理器
        manager = create_federated_manager(
            dataset_name="mnist",
            data_root="./data",
            num_clients=5,
            partition_strategy=strategy,
            partition_params=params,
            seed=42
        )
        
        # 准备数据
        manager.prepare_data()
        
        # 获取划分信息
        info = manager.get_partition_info()
        print(f"  划分器: {info['partitioner_name']}")
        print(f"  策略类型: {info['strategy_type']}")


def example_all_datasets():
    """示例3: 所有数据集"""
    print("\n" + "="*70)
    print("示例3: 测试所有数据集")
    print("="*70)
    
    datasets = ["mnist", "cifar10", "fashion_mnist"]
    
    for dataset_name in datasets:
        print(f"\n测试 {dataset_name.upper()}...")
        
        manager = create_federated_manager(
            dataset_name=dataset_name,
            data_root="./data",
            num_clients=3,
            partition_strategy="iid",
            seed=42
        )
        
        manager.prepare_data()
        
        info = manager.get_data_info()
        print(f"  ✓ {info['dataset_name']}")
        print(f"    类别数: {info['num_classes']}")
        print(f"    训练样本: {info['train_samples']}")
        print(f"    测试样本: {info['test_samples']}")


def example_direct_import():
    """示例4: 直接导入Manager类"""
    print("\n" + "="*70)
    print("示例4: 直接导入Manager类")
    print("="*70)
    
    from datasets import MNISTFederatedManager
    
    # 直接使用Manager类
    manager = MNISTFederatedManager(
        data_root="./data",
        num_clients=3,
        partition_strategy="dirichlet",
        partition_params={"alpha": 0.5},
        seed=42
    )
    
    manager.prepare_data()
    
    print(f"✓ 使用MNISTFederatedManager直接创建")
    print(f"  数据集: {manager.dataset_name}")
    print(f"  客户端数: {manager._num_clients}")
    print(f"  划分策略: {manager._partition_strategy}")


def main():
    """主函数"""
    print("\n" + "#"*70)
    print("# 联邦学习数据集使用示例")
    print("# 默认使用torchvision下载数据")
    print("#"*70)
    
    # 运行示例
    example_basic_usage()
    example_different_strategies()
    example_all_datasets()
    example_direct_import()
    
    print("\n" + "#"*70)
    print("# 所有示例运行完成!")
    print("#"*70)


if __name__ == "__main__":
    main()
