"""
数据集测试脚本

测试所有数据集的核心功能：
1. 原始数据集下载和加载（使用torchvision）
2. 预处理器
3. 划分器
4. 数据集管理器
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import torch
from torch.utils.data import Dataset

from core import (
    RawDatasetBase,
    PreprocessorBase,
    PartitionerBase,
    FederatedDatasetManager,
    IIDPartitioner,
)
from datasets import (
    MNISTRawDataset,
    MNISTPreprocessor,
    MNISTFederatedManager,
    CIFAR10RawDataset,
    CIFAR10Preprocessor,
    CIFAR10FederatedManager,
    FashionMNISTRawDataset,
    FashionMNISTPreprocessor,
    FashionMNISTFederatedManager,
    list_available_datasets,
    get_dataset_info,
    get_federated_manager_class,
    create_federated_manager,
)


class TestRawDatasets(unittest.TestCase):
    """测试原始数据集"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.test_dir = tempfile.mkdtemp()
        cls.data_root = Path(cls.test_dir) / "data"
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def _test_raw_dataset_basic(self, raw_class, expected_name):
        """测试原始数据集基本属性"""
        dataset = raw_class(data_root=self.data_root, download=False)
        
        # 测试基本信息
        self.assertEqual(dataset.name, expected_name)
        self.assertIsInstance(dataset.num_classes, int)
        self.assertIsInstance(dataset.num_features, int)
        self.assertIsInstance(dataset.input_shape, tuple)
        self.assertIsInstance(dataset.train_samples, int)
        self.assertIsInstance(dataset.test_samples, int)
        
        # 测试数据集信息
        info = dataset.get_dataset_info()
        self.assertEqual(info["name"], expected_name)
        self.assertIn("num_classes", info)
        self.assertIn("num_features", info)
        self.assertIn("input_shape", info)
        self.assertIn("train_samples", info)
        self.assertIn("test_samples", info)
        
        # 测试类别名称
        class_names = dataset.get_class_names()
        if class_names is not None:
            self.assertIsInstance(class_names, list)
            self.assertEqual(len(class_names), dataset.num_classes)
    
    def _test_raw_dataset_loading(self, raw_class):
        """测试原始数据集加载（使用torchvision下载）"""
        dataset = raw_class(data_root=self.data_root, download=True)
        
        # 测试下载（使用torchvision）
        dataset.download()
        
        # 测试加载训练集
        train_data = dataset.load_train_data()
        self.assertIsInstance(train_data, Dataset)
        
        # 测试加载测试集
        test_data = dataset.load_test_data()
        self.assertIsInstance(test_data, Dataset)
        
        # 验证样本数
        self.assertEqual(len(train_data), dataset.train_samples)
        self.assertEqual(len(test_data), dataset.test_samples)
        
        # 验证可以获取一个样本
        sample, label = train_data[0]
        self.assertIsNotNone(sample)
        self.assertIsInstance(label, int)
    
    def test_mnist_raw_dataset(self):
        """测试MNIST原始数据集"""
        self._test_raw_dataset_basic(MNISTRawDataset, "mnist")
        self._test_raw_dataset_loading(MNISTRawDataset)
    
    def test_cifar10_raw_dataset(self):
        """测试CIFAR-10原始数据集"""
        self._test_raw_dataset_basic(CIFAR10RawDataset, "cifar10")
        self._test_raw_dataset_loading(CIFAR10RawDataset)
    
    def test_fashion_mnist_raw_dataset(self):
        """测试Fashion-MNIST原始数据集"""
        self._test_raw_dataset_basic(FashionMNISTRawDataset, "fashion_mnist")
        self._test_raw_dataset_loading(FashionMNISTRawDataset)


class TestPreprocessors(unittest.TestCase):
    """测试预处理器"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.test_dir = tempfile.mkdtemp()
        cls.data_root = Path(cls.test_dir) / "data"
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def _test_preprocessor_basic(self, raw_class, preprocessor_class):
        """测试预处理器基本功能"""
        # 创建原始数据集（使用torchvision下载）
        raw_dataset = raw_class(data_root=self.data_root, download=True)
        train_data = raw_dataset.load_train_data()
        
        # 创建预处理器
        preprocessor = preprocessor_class()
        
        # 测试fit
        fitted_preprocessor = preprocessor.fit(train_data)
        self.assertIsInstance(fitted_preprocessor, PreprocessorBase)
        
        # 测试获取变换
        train_transform = preprocessor.get_train_transform()
        test_transform = preprocessor.get_test_transform()
        self.assertIsNotNone(train_transform)
        self.assertIsNotNone(test_transform)
        
        # 测试参数保存和加载
        params = preprocessor.get_params()
        self.assertIsInstance(params, dict)
        
        # 测试设置参数
        preprocessor.set_params(params)
    
    def test_mnist_preprocessor(self):
        """测试MNIST预处理器"""
        self._test_preprocessor_basic(MNISTRawDataset, MNISTPreprocessor)
    
    def test_cifar10_preprocessor(self):
        """测试CIFAR-10预处理器"""
        self._test_preprocessor_basic(CIFAR10RawDataset, CIFAR10Preprocessor)
    
    def test_fashion_mnist_preprocessor(self):
        """测试Fashion-MNIST预处理器"""
        self._test_preprocessor_basic(FashionMNISTRawDataset, FashionMNISTPreprocessor)


class TestPartitioners(unittest.TestCase):
    """测试划分器"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.test_dir = tempfile.mkdtemp()
        cls.data_root = Path(cls.test_dir) / "data"
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def _test_partitioner(self, raw_class, num_clients=5):
        """测试划分器 - 使用IIDPartitioner基类"""
        # 创建原始数据集（使用torchvision下载）
        raw_dataset = raw_class(data_root=self.data_root, download=True)
        train_data = raw_dataset.load_train_data()
        
        # 使用IIDPartitioner基类进行测试
        partitioner = IIDPartitioner(num_clients=num_clients, seed=42)
        
        # 测试划分
        partition_result = partitioner.partition(train_data)
        
        # 验证划分结果格式
        self.assertIsInstance(partition_result, dict)
        self.assertEqual(len(partition_result), num_clients)
        
        # 验证每个客户端都有数据索引
        for client_id in range(num_clients):
            self.assertIn(client_id, partition_result)
            self.assertIsInstance(partition_result[client_id], list)
        
        # 验证统计信息
        stats = partitioner.get_statistics(train_data, partition_result)
        self.assertIsInstance(stats, dict)
        
        # 验证分布信息
        distribution = partitioner.get_distribution(train_data, partition_result)
        self.assertIsInstance(distribution, dict)
    
    def test_mnist_partitioner(self):
        """测试MNIST划分器"""
        self._test_partitioner(MNISTRawDataset)
    
    def test_cifar10_partitioner(self):
        """测试CIFAR-10划分器"""
        self._test_partitioner(CIFAR10RawDataset)
    
    def test_fashion_mnist_partitioner(self):
        """测试Fashion-MNIST划分器"""
        self._test_partitioner(FashionMNISTRawDataset)


class TestFederatedManager(unittest.TestCase):
    """测试联邦学习管理器"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.test_dir = tempfile.mkdtemp()
        cls.data_root = Path(cls.test_dir) / "data"
        
    @classmethod
    def tearDownClass(cls):
        """清理测试环境"""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        manager = create_federated_manager(
            dataset_name="mnist",
            data_root=self.data_root,
            num_clients=5,
            partition_strategy="iid",
            seed=42
        )
        
        self.assertIsNotNone(manager)
        self.assertEqual(manager.dataset_name, "mnist")
        self.assertEqual(manager._num_clients, 5)
    
    def test_manager_data_preparation(self):
        """测试管理器数据准备"""
        manager = create_federated_manager(
            dataset_name="mnist",
            data_root=self.data_root,
            num_clients=5,
            partition_strategy="iid",
            seed=42
        )
        
        # 准备数据（使用torchvision下载）
        manager.prepare_data()
        
        # 验证可以获取客户端数据加载器
        for client_id in range(5):
            loader = manager.get_client_loader(client_id, batch_size=32)
            self.assertIsNotNone(loader)
            
            # 验证可以迭代
            batch = next(iter(loader))
            self.assertEqual(len(batch), 2)  # (data, target)
        
        # 验证测试加载器
        test_loader = manager.get_test_loader(batch_size=32)
        self.assertIsNotNone(test_loader)
        
        # 验证划分信息
        partition_info = manager.get_partition_info()
        self.assertIsInstance(partition_info, dict)
    
    def test_different_strategies(self):
        """测试不同划分策略"""
        strategies = ["iid", "dirichlet", "pathological"]
        
        for strategy in strategies:
            manager = create_federated_manager(
                dataset_name="mnist",
                data_root=self.data_root,
                num_clients=3,
                partition_strategy=strategy,
                partition_params={"alpha": 0.5} if strategy == "dirichlet" else {"shards_per_client": 2} if strategy == "pathological" else {},
                seed=42
            )
            
            manager.prepare_data()
            
            info = manager.get_partition_info()
            self.assertEqual(info["partition_strategy"], strategy)
            self.assertIn("partitioner_name", info)
    
    def test_all_datasets(self):
        """测试所有数据集的管理器"""
        for dataset_name in list_available_datasets():
            manager_class = get_federated_manager_class(dataset_name)
            self.assertIsNotNone(manager_class, f"{dataset_name} should have a manager class")
            
            # 创建实例
            manager = create_federated_manager(
                dataset_name=dataset_name,
                data_root=self.data_root,
                num_clients=3,
                partition_strategy="iid",
                seed=42
            )
            
            self.assertIsNotNone(manager)
            self.assertEqual(manager.dataset_name, dataset_name)


class TestUtilityFunctions(unittest.TestCase):
    """测试工具函数"""
    
    def test_list_available_datasets(self):
        """测试列出可用数据集"""
        datasets = list_available_datasets()
        self.assertIsInstance(datasets, list)
        self.assertIn("mnist", datasets)
        self.assertIn("cifar10", datasets)
        self.assertIn("fashion_mnist", datasets)
    
    def test_get_dataset_info(self):
        """测试获取数据集信息"""
        for dataset_name in ["mnist", "cifar10", "fashion_mnist"]:
            info = get_dataset_info(dataset_name)
            self.assertIsNotNone(info)
            self.assertIn("name", info)
            self.assertIn("num_classes", info)
            self.assertIn("num_features", info)
            self.assertIn("input_shape", info)
            self.assertIn("train_samples", info)
            self.assertIn("test_samples", info)
    
    def test_get_federated_manager_class(self):
        """测试获取联邦学习管理器类"""
        for dataset_name in list_available_datasets():
            manager_class = get_federated_manager_class(dataset_name)
            self.assertIsNotNone(manager_class)
            # 验证是FederatedDatasetManager的子类
            self.assertTrue(issubclass(manager_class, FederatedDatasetManager))


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestRawDatasets))
    suite.addTests(loader.loadTestsFromTestCase(TestPreprocessors))
    suite.addTests(loader.loadTestsFromTestCase(TestPartitioners))
    suite.addTests(loader.loadTestsFromTestCase(TestFederatedManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
