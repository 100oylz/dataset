"""
数据库模型模块

定义数据集注册信息的数据库模型
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


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
        """
        转换为字典
        
        Returns:
            包含所有字段的字典
        """
        data = asdict(self)
        
        # 处理 datetime 字段
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        
        # 将 input_shape tuple 转换为字符串
        if self.input_shape:
            data['input_shape'] = ','.join(map(str, self.input_shape))
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetRegistration":
        """
        从字典创建实例
        
        Args:
            data: 数据字典
            
        Returns:
            DatasetRegistration 实例
        """
        # 处理 datetime 字段
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            if isinstance(data['updated_at'], str):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # 处理 input_shape 字符串为 tuple
        if 'input_shape' in data and isinstance(data['input_shape'], str):
            if data['input_shape']:
                data['input_shape'] = tuple(map(int, data['input_shape'].split(',')))
            else:
                data['input_shape'] = ()
        
        # 处理 JSON 字段
        if 'extra_params' in data and isinstance(data['extra_params'], str):
            data['extra_params'] = json.loads(data['extra_params'])
        if 'tags' in data and isinstance(data['tags'], str):
            data['tags'] = json.loads(data['tags'])
        
        # 过滤掉不在 dataclass 中的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "DatasetRegistration":
        """
        从数据库行创建实例
        
        Args:
            row: 数据库查询结果行
            
        Returns:
            DatasetRegistration 实例
        """
        data = dict(row)
        
        # 解析 JSON 字段
        for field_name in ['extra_params', 'tags']:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    try:
                        data[field_name] = json.loads(data[field_name])
                    except json.JSONDecodeError:
                        data[field_name] = {}
        
        return cls.from_dict(data)
    
    def to_db_dict(self) -> Dict[str, Any]:
        """
        转换为数据库插入/更新用的字典
        
        Returns:
            适合数据库存储的字典
        """
        data = self.to_dict()
        
        # JSON 字段序列化
        if self.extra_params:
            data['extra_params'] = json.dumps(self.extra_params)
        if self.tags:
            data['tags'] = json.dumps(self.tags)
        
        # 移除 None 值和 id（让数据库自动生成）
        if 'id' in data:
            del data['id']
        
        return {k: v for k, v in data.items() if v is not None}
    
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
        return {
            "raw_dataset": {
                "module": self.raw_dataset_module,
                "class": self.raw_dataset_class
            },
            "preprocessor": {
                "module": self.preprocessor_module,
                "class": self.preprocessor_class
            },
            "partitioner": {
                "module": self.partitioner_module,
                "class": self.partitioner_class
            },
            "manager": {
                "module": self.manager_module,
                "class": self.manager_class
            },
        }
    
    def is_valid(self) -> bool:
        """
        检查注册信息是否有效
        
        Returns:
            是否包含必要的字段
        """
        return bool(
            self.name and
            self.raw_dataset_module and
            self.raw_dataset_class and
            self.preprocessor_module and
            self.preprocessor_class and
            self.partitioner_module and
            self.partitioner_class
        )


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
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            包含所有字段的字典
        """
        data = asdict(self)
        
        # 处理 datetime 字段
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PartitionStrategy":
        """
        从字典创建实例
        
        Args:
            data: 数据字典
            
        Returns:
            PartitionStrategy 实例
        """
        # 处理 datetime 字段
        if 'created_at' in data and data['created_at']:
            if isinstance(data['created_at'], str):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            if isinstance(data['updated_at'], str):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # 处理 JSON 字段
        for field_name in ['default_params', 'param_schema', 'supported_datasets']:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = json.loads(data[field_name])
                except json.JSONDecodeError:
                    data[field_name] = {} if field_name != 'supported_datasets' else []
        
        # 过滤掉不在 dataclass 中的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "PartitionStrategy":
        """
        从数据库行创建实例
        
        Args:
            row: 数据库查询结果行
            
        Returns:
            PartitionStrategy 实例
        """
        data = dict(row)
        
        # 解析 JSON 字段
        for field_name in ['default_params', 'param_schema', 'supported_datasets']:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    try:
                        data[field_name] = json.loads(data[field_name])
                    except json.JSONDecodeError:
                        data[field_name] = {} if field_name != 'supported_datasets' else []
        
        return cls.from_dict(data)
    
    def to_db_dict(self) -> Dict[str, Any]:
        """
        转换为数据库插入/更新用的字典
        
        Returns:
            适合数据库存储的字典
        """
        data = self.to_dict()
        
        # JSON 字段序列化
        for field_name in ['default_params', 'param_schema', 'supported_datasets']:
            if field_name in data and data[field_name]:
                data[field_name] = json.dumps(data[field_name])
        
        # 移除 None 值和 id
        if 'id' in data:
            del data['id']
        
        return {k: v for k, v in data.items() if v is not None}
    
    def is_valid_for_dataset(self, dataset_name: str, num_clients: int) -> Tuple[bool, str]:
        """
        检查策略是否适用于指定数据集和客户端数量
        
        Args:
            dataset_name: 数据集名称
            num_clients: 客户端数量
            
        Returns:
            (是否有效, 错误信息)
        """
        if self.status != "active":
            return False, f"策略 '{self.name}' 未激活"
        
        if dataset_name not in self.supported_datasets:
            return False, f"策略 '{self.name}' 不支持数据集 '{dataset_name}'"
        
        if num_clients < self.min_clients:
            return False, f"客户端数量 {num_clients} 小于最小值 {self.min_clients}"
        
        if num_clients > self.max_clients:
            return False, f"客户端数量 {num_clients} 大于最大值 {self.max_clients}"
        
        return True, ""


@dataclass
class PartitionResult:
    """
    划分结果存储
    """
    
    id: Optional[int] = None
    dataset_name: str = ""
    strategy_name: str = ""
    num_clients: int = 0
    params: Dict[str, Any] = field(default_factory=dict)
    client_indices: Dict[int, List[int]] = field(default_factory=dict)
    total_samples: int = 0
    samples_per_client: Dict[int, int] = field(default_factory=dict)
    class_distribution: Dict[int, Dict[int, int]] = field(default_factory=dict)
    version: str = "1.0.0"
    fingerprint: str = ""
    created_by: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        
        return data
    
    def to_db_dict(self) -> Dict[str, Any]:
        """转换为数据库字典"""
        data = {
            'dataset_name': self.dataset_name,
            'strategy_name': self.strategy_name,
            'num_clients': self.num_clients,
            'params': json.dumps(self.params),
            'client_indices': json.dumps(self.client_indices),
            'total_samples': self.total_samples,
            'samples_per_client': json.dumps(self.samples_per_client),
            'class_distribution': json.dumps(self.class_distribution),
            'version': self.version,
            'fingerprint': self.fingerprint,
            'created_by': self.created_by,
            'description': self.description,
        }
        return data
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "PartitionResult":
        """从数据库行创建实例"""
        data = dict(row)
        
        # 解析 JSON 字段
        for field_name in ['params', 'client_indices', 'samples_per_client', 'class_distribution']:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    try:
                        # JSON 键是字符串，需要转换为 int
                        parsed = json.loads(data[field_name])
                        if field_name in ['client_indices', 'samples_per_client', 'class_distribution']:
                            parsed = {int(k): v for k, v in parsed.items()}
                        data[field_name] = parsed
                    except json.JSONDecodeError:
                        data[field_name] = {} if field_name != 'client_indices' else {}
        
        return cls(**data)
