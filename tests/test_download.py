"""
数据集下载测试脚本

验证所有数据集可以正确通过torchvision下载
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datasets import (
    MNISTRawDataset,
    CIFAR10RawDataset,
    FashionMNISTRawDataset,
    list_available_datasets,
)


def test_dataset_download(dataset_name: str, data_root: str = "./data") -> bool:
    """
    测试单个数据集下载
    
    Args:
        dataset_name: 数据集名称
        data_root: 数据根目录
        
    Returns:
        是否成功
    """
    print(f"\n{'='*60}")
    print(f"测试数据集: {dataset_name.upper()}")
    print(f"{'='*60}")
    
    try:
        # 获取对应的数据集类
        dataset_map = {
            "mnist": MNISTRawDataset,
            "cifar10": CIFAR10RawDataset,
            "fashion_mnist": FashionMNISTRawDataset,
        }
        
        if dataset_name not in dataset_map:
            print(f"❌ 未知数据集: {dataset_name}")
            return False
        
        dataset_class = dataset_map[dataset_name]
        
        # 创建数据集实例（使用torchvision下载）
        print(f"1. 创建数据集实例...")
        dataset = dataset_class(data_root=data_root, download=True)
        print(f"   ✓ 数据集名称: {dataset.name}")
        print(f"   ✓ 类别数: {dataset.num_classes}")
        print(f"   ✓ 特征维度: {dataset.num_features}")
        print(f"   ✓ 输入形状: {dataset.input_shape}")
        print(f"   ✓ 训练样本数: {dataset.train_samples}")
        print(f"   ✓ 测试样本数: {dataset.test_samples}")
        
        # 下载数据
        print(f"\n2. 下载数据（使用torchvision）...")
        dataset.download()
        print(f"   ✓ 下载完成")
        
        # 加载训练数据
        print(f"\n3. 加载训练数据...")
        train_data = dataset.load_train_data()
        print(f"   ✓ 训练集大小: {len(train_data)}")
        
        # 加载测试数据
        print(f"\n4. 加载测试数据...")
        test_data = dataset.load_test_data()
        print(f"   ✓ 测试集大小: {len(test_data)}")
        
        # 获取一个样本
        print(f"\n5. 验证数据样本...")
        sample, label = train_data[0]
        print(f"   ✓ 样本类型: {type(sample)}")
        print(f"   ✓ 标签类型: {type(label)}")
        print(f"   ✓ 标签值: {label}")
        
        # 获取类别名称
        class_names = dataset.get_class_names()
        if class_names:
            print(f"   ✓ 类别名称: {class_names[:5]}..." if len(class_names) > 5 else f"   ✓ 类别名称: {class_names}")
        
        print(f"\n✅ {dataset_name.upper()} 测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ {dataset_name.upper()} 测试失败!")
        print(f"   错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试数据集下载")
    parser.add_argument(
        "--dataset",
        type=str,
        default="all",
        help="要测试的数据集名称 (mnist, cifar10, fashion_mnist, all)",
    )
    parser.add_argument(
        "--data-root",
        type=str,
        default="./data",
        help="数据根目录",
    )
    args = parser.parse_args()
    
    print(f"\n{'#'*70}")
    print(f"# 联邦学习数据集下载测试")
    print(f"# 数据根目录: {args.data_root}")
    print(f"# 使用torchvision自动下载")
    print(f"{'#'*70}")
    
    # 确定要测试的数据集
    if args.dataset == "all":
        datasets_to_test = list_available_datasets()
    else:
        datasets_to_test = [args.dataset]
    
    # 测试每个数据集
    results = {}
    for dataset_name in datasets_to_test:
        success = test_dataset_download(dataset_name, args.data_root)
        results[dataset_name] = success
    
    # 打印总结
    print(f"\n{'#'*70}")
    print(f"# 测试结果总结")
    print(f"{'#'*70}")
    
    total = len(results)
    passed = sum(results.values())
    
    for dataset_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {dataset_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    # 返回退出码
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
