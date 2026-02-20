"""
数据库模型模块

定义数据集注册信息的数据库模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DatasetRegistration:
    """
    数据集注册信息
    
    用于数据库存储，支持动态模块导入
    """
    
    # 基本信息
    id: Optional[int] = None
    name: str = ""  # 数据集唯一标识名
    display_name: str = ""  # 显示名称
    description: str = ""  # 数据集描述
    
    # 数据特性
    num_classes: int = 0  # 类别数
    num_features: int = 0  # 特征维度
    input_shape: Tuple[int, ...] = field(default_factory=tuple)  # 输入形状
    data_type: str = "image"  # 数据类型（image/text/audio等）
    task_type: str = "classification"  # 任务类型
    
    # 模块路径信息（用于动态导入）
    raw_dataset_module: str = ""  # 原始数据集模块路径，如 "datasets.mnist.raw"
    raw_dataset_class: str = ""  # 原始数据集类名，如 "MNISTRawDataset"
    
    preprocessor_module: str = ""  # 预处理器模块路径，如 "datasets.mnist.preprocess"
    preprocessor_class: str = ""  # 预处理器类名，如 "MNISTPreprocessor"
    
    partitioner_module: str = ""  # 划分器模块路径，如 "datasets.mnist.partition"
    partitioner_class: str = ""  # 划分器类名，如 "MNISTPartitioner"
    
    manager_module: str = ""  # 管理器模块路径，如 "datasets.mnist.manager"
    manager_class: str = ""  # 管理器类名，如 "MNISTManager"
    
    # 元数据
    version: str = "1.0.0"  # 版本号
    author: str = ""  # 作者
    source_url: str = ""  # 数据来源URL
    paper_url: str = ""  # 论文链接
    license: str = ""  # 许可证
    
    # 统计信息
    train_samples: int = 0  # 训练样本数
    test_samples: int = 0  # 测试样本数
    
    # 扩展信息
    extra_params: Dict[str, Any] = field(default_factory=dict)  # 额外参数
    tags: List[str] = field(default_factory=list)  # 标签列表
    
    # 状态
    status: str = "active"  # active/deprecated/archived
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # TODO: 实现转换为字典的逻辑
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetRegistration":
        """从字典创建"""
        # TODO: 实现从字典创建的逻辑
        pass
    
    def get_module_import_info(self) -> Dict[str, Dict[str, str]]:
        """
        获取模块导入信息
        
        Returns:
            {
                "raw_dataset": {"module": "...", "class": "..."},
                "preprocessor": {"module": "...", "class": "..."},
                "partitioner": {"module": "...", "class": "..."},
                "manager": {"module": "...", "class": "..."},
            }
        """
        # TODO: 返回模块导入信息
        pass


# SQL表结构定义（供参考）
DATASET_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS dataset_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(128),
    description TEXT,
    
    num_classes INT DEFAULT 0,
    num_features INT DEFAULT 0,
    input_shape VARCHAR(64),
    data_type VARCHAR(32) DEFAULT 'image',
    task_type VARCHAR(32) DEFAULT 'classification',
    
    raw_dataset_module VARCHAR(256),
    raw_dataset_class VARCHAR(64),
    preprocessor_module VARCHAR(256),
    preprocessor_class VARCHAR(64),
    partitioner_module VARCHAR(256),
    partitioner_class VARCHAR(64),
    manager_module VARCHAR(256),
    manager_class VARCHAR(64),
    
    version VARCHAR(32) DEFAULT '1.0.0',
    author VARCHAR(128),
    source_url VARCHAR(512),
    paper_url VARCHAR(512),
    license VARCHAR(64),
    
    train_samples INT DEFAULT 0,
    test_samples INT DEFAULT 0,
    
    extra_params JSON,
    tags JSON,
    
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_data_type (data_type),
    INDEX idx_task_type (task_type),
    INDEX idx_status (status)
);
"""


@dataclass
class PartitionStrategy:
    """
    划分策略配置
    
    存储支持的划分策略及其默认参数
    """
    
    id: Optional[int] = None
    name: str = ""  # 策略名称（iid/dirichlet/pathological）
    display_name: str = ""  # 显示名称
    description: str = ""  # 策略描述
    
    # 默认参数
    default_params: Dict[str, Any] = field(default_factory=dict)
    
    # 参数说明
    param_schema: Dict[str, Any] = field(default_factory=dict)  # JSON Schema格式
    
    # 支持的最低和最高客户端数量
    min_clients: int = 2
    max_clients: int = 10000
    
    # 适用数据集
    supported_datasets: List[str] = field(default_factory=list)
    
    # 是否支持联邦学习
    is_federated: bool = True
    
    # 状态
    status: str = "active"
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # TODO: 实现转换为字典的逻辑
        pass
