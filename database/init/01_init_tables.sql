-- ============================================
-- 联邦学习数据集管理框架 - 数据库初始化脚本
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS fl_dataset_db 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE fl_dataset_db;

-- ============================================
-- 数据集注册信息表
-- ============================================
CREATE TABLE IF NOT EXISTS dataset_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL COMMENT '数据集唯一标识名',
    display_name VARCHAR(128) COMMENT '显示名称',
    description TEXT COMMENT '数据集描述',
    
    -- 数据特性
    num_classes INT DEFAULT 0 COMMENT '类别数',
    num_features INT DEFAULT 0 COMMENT '特征维度',
    input_shape VARCHAR(64) COMMENT '输入形状，如 "1,28,28"',
    data_type VARCHAR(32) DEFAULT 'image' COMMENT '数据类型（image/text/audio等）',
    task_type VARCHAR(32) DEFAULT 'classification' COMMENT '任务类型',
    
    -- 模块路径信息（用于动态导入）
    raw_dataset_module VARCHAR(256) COMMENT '原始数据集模块路径',
    raw_dataset_class VARCHAR(64) COMMENT '原始数据集类名',
    preprocessor_module VARCHAR(256) COMMENT '预处理器模块路径',
    preprocessor_class VARCHAR(64) COMMENT '预处理器类名',
    partitioner_module VARCHAR(256) COMMENT '划分器模块路径',
    partitioner_class VARCHAR(64) COMMENT '划分器类名',
    manager_module VARCHAR(256) COMMENT '管理器模块路径',
    manager_class VARCHAR(64) COMMENT '管理器类名',
    
    -- 版本和元信息
    version VARCHAR(32) DEFAULT '1.0.0' COMMENT '版本号',
    author VARCHAR(128) COMMENT '作者',
    source_url VARCHAR(512) COMMENT '数据来源URL',
    paper_url VARCHAR(512) COMMENT '论文链接',
    license VARCHAR(64) COMMENT '许可证',
    
    -- 统计信息
    train_samples INT DEFAULT 0 COMMENT '训练样本数',
    test_samples INT DEFAULT 0 COMMENT '测试样本数',
    
    -- 扩展信息
    extra_params JSON COMMENT '额外参数',
    tags JSON COMMENT '标签列表',
    
    -- 状态
    status VARCHAR(32) DEFAULT 'active' COMMENT '状态：active/deprecated/archived',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_name (name),
    INDEX idx_data_type (data_type),
    INDEX idx_task_type (task_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据集注册信息表';

-- ============================================
-- 划分策略配置表
-- ============================================
CREATE TABLE IF NOT EXISTS partition_strategies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL COMMENT '策略名称（iid/dirichlet/pathological）',
    display_name VARCHAR(128) COMMENT '显示名称',
    description TEXT COMMENT '策略描述',
    
    -- 默认参数和模式
    default_params JSON COMMENT '默认参数',
    param_schema JSON COMMENT '参数说明（JSON Schema格式）',
    
    -- 限制
    min_clients INT DEFAULT 2 COMMENT '支持的最低客户端数量',
    max_clients INT DEFAULT 10000 COMMENT '支持的最高客户端数量',
    
    -- 适用数据集
    supported_datasets JSON COMMENT '适用数据集列表',
    
    -- 特性
    is_federated BOOLEAN DEFAULT TRUE COMMENT '是否支持联邦学习',
    
    -- 状态
    status VARCHAR(32) DEFAULT 'active' COMMENT '状态：active/deprecated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_name (name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='划分策略配置表';

-- ============================================
-- 划分结果存储表
-- ============================================
CREATE TABLE IF NOT EXISTS partition_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_name VARCHAR(64) NOT NULL COMMENT '数据集名称',
    strategy_name VARCHAR(64) NOT NULL COMMENT '划分策略名称',
    num_clients INT NOT NULL COMMENT '客户端数量',
    params JSON COMMENT '划分参数',
    
    -- 划分结果（索引列表的JSON）
    client_indices JSON NOT NULL COMMENT '划分结果 {client_id: [indices]}',
    
    -- 统计信息
    total_samples INT NOT NULL COMMENT '总样本数',
    samples_per_client JSON COMMENT '每个客户端的样本数',
    class_distribution JSON COMMENT '类别分布统计',
    
    -- 版本和标识
    version VARCHAR(32) DEFAULT '1.0.0' COMMENT '版本号',
    fingerprint VARCHAR(64) COMMENT '划分结果指纹（用于缓存）',
    
    -- 元信息
    created_by VARCHAR(128) COMMENT '创建者',
    description TEXT COMMENT '描述',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引
    INDEX idx_dataset_strategy (dataset_name, strategy_name),
    INDEX idx_fingerprint (fingerprint),
    INDEX idx_created_at (created_at),
    
    -- 同一数据集的相同划分只保留最新结果
    UNIQUE KEY uk_dataset_config (dataset_name, strategy_name, num_clients, fingerprint(32))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='划分结果存储表';

-- ============================================
-- 注：dataset_usage_logs 表已删除
-- 原用于记录数据集使用日志，但当前代码未使用
-- 如需添加日志功能，请重新创建此表
-- ============================================
