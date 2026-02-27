-- ============================================
-- 初始化默认数据
-- ============================================

USE fl_dataset_db;

-- ============================================
-- 插入默认划分策略
-- ============================================
INSERT INTO partition_strategies 
    (name, display_name, description, default_params, param_schema, min_clients, max_clients, supported_datasets, is_federated, status)
VALUES
    (
        'iid',
        'IID 划分',
        '独立同分布划分，将数据随机均匀分配给所有客户端',
        '{}',
        '{
            "type": "object",
            "properties": {},
            "description": "IID划分不需要额外参数"
        }',
        2, 10000,
        '["mnist", "cifar10", "fashion_mnist"]',
        TRUE, 'active'
    ),
    (
        'dirichlet',
        'Dirichlet 划分',
        '基于Dirichlet分布的Non-IID划分，控制数据异构程度',
        '{"alpha": 0.5}',
        '{
            "type": "object",
            "properties": {
                "alpha": {
                    "type": "number",
                    "default": 0.5,
                    "minimum": 0.01,
                    "maximum": 100,
                    "description": "Dirichlet参数，越小越Non-IID"
                }
            },
            "required": ["alpha"]
        }',
        2, 10000,
        '["mnist", "cifar10", "fashion_mnist"]',
        TRUE, 'active'
    ),
    (
        'pathological',
        'Pathological 划分',
        '病态划分，每个客户端只获得特定数量的类别',
        '{"shards_per_client": 2}',
        '{
            "type": "object",
            "properties": {
                "shards_per_client": {
                    "type": "integer",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 10,
                    "description": "每个客户端的类别数"
                }
            },
            "required": ["shards_per_client"]
        }',
        2, 10000,
        '["mnist", "cifar10", "fashion_mnist"]',
        TRUE, 'active'
    )
ON DUPLICATE KEY UPDATE
    display_name = VALUES(display_name),
    description = VALUES(description),
    default_params = VALUES(default_params),
    param_schema = VALUES(param_schema),
    updated_at = CURRENT_TIMESTAMP;

-- ============================================
-- 插入默认数据集注册信息
-- ============================================
INSERT INTO dataset_registrations
    (name, display_name, description, num_classes, num_features, input_shape, data_type, task_type,
     raw_dataset_module, raw_dataset_class,
     preprocessor_module, preprocessor_class,
     partitioner_module, partitioner_class,
     version, author, source_url, license,
     train_samples, test_samples,
     extra_params, tags, status)
VALUES
    (
        'mnist',
        'MNIST',
        'MNIST手写数字识别数据集，包含0-9的灰度手写数字图像',
        10, 784, '1,28,28', 'image', 'classification',
        'datasets.mnist.raw', 'MNISTRawDataset',
        'datasets.mnist.preprocess', 'MNISTPreprocessor',
        'datasets.mnist.partition', 'MNISTPartitioner',
        '1.0.0', 'Yann LeCun', 'http://yann.lecun.com/exdb/mnist/', 'Unknown',
        60000, 10000,
        '{"mean": [0.1307], "std": [0.3081]}',
        '["image", "classification", "grayscale", "handwritten"]', 'active'
    ),
    (
        'cifar10',
        'CIFAR-10',
        'CIFAR-10彩色图像分类数据集，包含10个类别的32x32彩色图像',
        10, 3072, '3,32,32', 'image', 'classification',
        'datasets.cifar10.raw', 'CIFAR10RawDataset',
        'datasets.cifar10.preprocess', 'CIFAR10Preprocessor',
        'datasets.cifar10.partition', 'CIFAR10Partitioner',
        '1.0.0', 'Alex Krizhevsky', 'https://www.cs.toronto.edu/~kriz/cifar.html', 'Unknown',
        50000, 10000,
        '{"mean": [0.4914, 0.4822, 0.4465], "std": [0.2470, 0.2435, 0.2616]}',
        '["image", "classification", "color", "natural"]', 'active'
    ),
    (
        'fashion_mnist',
        'Fashion-MNIST',
        'Fashion-MNIST时尚物品分类数据集，10个类别的灰度图像',
        10, 784, '1,28,28', 'image', 'classification',
        'datasets.fashion_mnist.raw', 'FashionMNISTRawDataset',
        'datasets.fashion_mnist.preprocess', 'FashionMNISTPreprocessor',
        'datasets.fashion_mnist.partition', 'FashionMNISTPartitioner',
        '1.0.0', 'Zalando Research', 'https://github.com/zalandoresearch/fashion-mnist', 'MIT',
        60000, 10000,
        '{"mean": [0.2860], "std": [0.3530]}',
        '["image", "classification", "grayscale", "fashion"]', 'active'
    )
ON DUPLICATE KEY UPDATE
    display_name = VALUES(display_name),
    description = VALUES(description),
    num_classes = VALUES(num_classes),
    num_features = VALUES(num_features),
    input_shape = VALUES(input_shape),
    train_samples = VALUES(train_samples),
    test_samples = VALUES(test_samples),
    extra_params = VALUES(extra_params),
    tags = VALUES(tags),
    updated_at = CURRENT_TIMESTAMP;
