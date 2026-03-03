"""
工具函数模块

提供通用的辅助函数
"""

import os
import random
import functools
from typing import Any, Dict, List, Optional, Tuple, Union,Callable
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import torch
import json
import warnings

def set_seed(seed: int = 42) -> None:
    # 基础库种子
    random.seed(seed)
    np.random.seed(seed)
    
    # PyTorch 种子
    torch.manual_seed(seed)
    
    # GPU 种子（如果有 CUDA）
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        
        # 确保 CUDA 卷积确定性
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    
    # 设置 Python 哈希种子（影响字典顺序、sets 等）
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    # 设置多进程数据加载的种子（关键！）
    def worker_init_fn(worker_id):
        np.random.seed(seed + worker_id)
        random.seed(seed + worker_id)
    
    return worker_init_fn  # 返回给 DataLoader 使用


def get_device(device: Optional[str] = None) -> torch.device:
    """
    获取计算设备
    
    Args:
        device: 指定设备（'cuda', 'cuda:0', 'mps', 'cpu' 等），None则自动选择最优设备
        
    Returns:
        torch.device 对象
        
    Examples:
        >>> get_device()  # 自动选择
        device(type='cuda', index=0)
        >>> get_device("cpu")  # 强制使用CPU
        device(type='cpu')
    """
    if device is not None:
        # 用户指定了设备，检查是否可用
        if device.startswith("cuda"):
            if not torch.cuda.is_available():
                raise RuntimeError(f"请求了 {device} 但 CUDA 不可用")
            # 检查具体的GPU编号是否存在
            if ":" in device:
                gpu_id = int(device.split(":")[1])
                if gpu_id >= torch.cuda.device_count():
                    raise RuntimeError(f"GPU {gpu_id} 不存在，只有 {torch.cuda.device_count()} 张卡")
        elif device == "mps" and not torch.backends.mps.is_available():
            raise RuntimeError("请求了 MPS (Apple Silicon) 但不可用")
        
        return torch.device(device)
    
    # 自动选择：CUDA > MPS > CPU
    if torch.cuda.is_available():
        # 默认使用 cuda:0，也可以改成自动选择显存最多的
        return torch.device("cuda:0")
    
    if torch.backends.mps.is_available():
        # Apple Silicon (M1/M2/M3)
        return torch.device("mps")
    
    return torch.device("cpu")


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    递归创建目录（如果不存在则创建所有父目录）
    
    Args:
        path: 目录路径（相对或绝对路径）
        
    Returns:
        Path: 创建后的目录路径对象
        
    Raises:
        PermissionError: 无权限创建目录
        NotADirectoryError: 路径存在但不是目录（是文件）
        
    Example:
        >>> ensure_dir("experiments/run_1/logs")
        PosixPath('/home/user/experiments/run_1/logs')
    """
    path_obj = Path(path).expanduser().resolve()
    
    # exist_ok=True: 目录已存在时不报错
    # parents=True:  自动创建所有不存在的父目录（递归关键）
    path_obj.mkdir(parents=True, exist_ok=True)
    
    return path_obj


def save_json(data: Any, path: Union[str, Path], indent: int = 2, ensure_ascii: bool = False) -> None:
    """
    保存数据为JSON文件
    
    Args:
        data: 要保存的数据（字典、列表等）
        path: 保存路径（自动创建父目录）
        indent: 格式化缩进（None表示紧凑格式，默认2空格）
        ensure_ascii: False保留中文，True转义为Unicode
        
    Raises:
        TypeError: 数据无法JSON序列化
        PermissionError: 无写入权限
        
    Example:
        >>> save_json({"name": "模型", "acc": 0.95}, "./results/metrics.json")
    """
    path_obj = Path(path)
    
    # 自动创建父目录
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件（使用 utf-8 编码支持中文）
    with open(path_obj, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)
        # default=str 处理非标准类型（如 datetime、numpy 等）

def load_json(path: Union[str, Path]) -> Any:
    """
    加载JSON文件
    
    Args:
        path: 文件路径
        
    Returns:
        解析后的数据（字典、列表等）
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON格式错误
        
    Example:
        >>> config = load_json("./config.json")
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        raise FileNotFoundError(f"JSON文件不存在: {path}")
    
    with open(path_obj, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_class_distribution(
    labels: Union[List[int], np.ndarray]
) -> Dict[int, int]:
    """
    计算类别分布
    
    Args:
        labels: 标签列表或数组
        
    Returns:
        {类别: 数量} 字典（按类别值排序）
        
    Example:
        >>> compute_class_distribution([0, 1, 0, 2, 1, 0])
        {0: 3, 1: 2, 2: 1}
    """
    if len(labels) == 0:
        return {}
    
    # np.unique 自动处理重复值，return_counts=True 直接返回计数
    # 比循环快 10-100 倍
    labels = np.asarray(labels)
    unique, counts = np.unique(labels, return_counts=True)
    
    return dict(zip(unique.tolist(), counts.tolist()))
        



def visualize_distribution(
    distribution: Dict[int, Dict[int, int]],
    title: str = "Data Distribution",
    save_path: Optional[str] = None,
    figsize: tuple = (12, 5),
    cmap: str = "viridis",
    max_clients: int = 10,
    max_classes: int = 10
) -> None:
    """
    可视化联邦学习客户端数据分布（限制最多10个客户端和10个类别）
    
    Args:
        distribution: 分布字典 {client_id: {label: count}}
        title: 图表标题
        save_path: 保存路径，None则显示
        figsize: 图像尺寸
        cmap: 颜色映射
        max_clients: 最大显示客户端数（默认10，防止过多影响观感）
        max_classes: 最大显示类别数（默认10，防止过多影响观感）
        
    Example:
        >>> dist = {i: {j: np.random.randint(10, 100) for j in range(15)} 
        ...         for i in range(20)}
        >>> visualize_distribution(dist, "Large Scale Dist", max_clients=8)
    """
    if not distribution:
        print("Warning: Empty distribution")
        return
    
    # 转换为DataFrame
    df = pd.DataFrame(distribution).T.fillna(0).astype(int)
    df.index.name = 'Client'
    df.columns.name = 'Class'
    
    original_shape = df.shape
    truncation_info = []
    
    # 限制客户端数量：选择样本量最多的前N个
    if len(df) > max_clients:
        top_clients = df.sum(axis=1).nlargest(max_clients).index
        df = df.loc[top_clients]
        truncation_info.append(f"Top {max_clients} clients by sample count (of {original_shape[0]} total)")
    
    # 限制类别数量：选择全局出现频率最高的前N个类别
    if len(df.columns) > max_classes:
        top_classes = df.sum().nlargest(max_classes).index
        # 将其他类别合并为"Others"
        other_cols = [c for c in df.columns if c not in top_classes]
        if other_cols:
            df['Others'] = df[other_cols].sum(axis=1)
            df = df[list(top_classes) + ['Others']]
            truncation_info.append(f"Top {max_classes} classes by frequency (of {original_shape[1]} total)")
    else:
        top_classes = df.columns
    
    # 如果有截断，添加警告并在标题中注明
    if truncation_info:
        warn_msg = "; ".join(truncation_info)
        warnings.warn(f"Data truncated: {warn_msg}", UserWarning)
        title = f"{title}\n(Truncated: {warn_msg})"
    
    # 调整图像大小：根据实际显示的数据量动态调整
    adjusted_figsize = (
        min(figsize[0], 4 + len(df.columns) * 0.8),  # 根据类别数调整宽度
        min(figsize[1], 3 + len(df) * 0.4)           # 根据客户端数调整高度
    )
    
    fig, axes = plt.subplots(1, 2, figsize=adjusted_figsize)
    
    # 左图：堆叠柱状图
    ax1 = axes[0]
    # 如果类别过多，调整颜色映射
    colors = plt.cm.get_cmap(cmap)(np.linspace(0, 1, len(df.columns)))
    
    df.plot(kind='bar', stacked=True, ax=ax1, color=colors, width=0.8, edgecolor='black', linewidth=0.5)
    ax1.set_title(f"{title}\n(Absolute Count)", fontsize=11)
    ax1.set_xlabel(f"Client ID (Showing {len(df)} of {original_shape[0]})" if len(df) != original_shape[0] else "Client ID")
    ax1.set_ylabel("Sample Count")
    ax1.legend(title="Class", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.tick_params(axis='x', rotation=45)
    
    # 添加总计标签
    totals = df.sum(axis=1)
    for i, total in enumerate(totals):
        ax1.text(i, total + max(totals)*0.02, f'{int(total)}', 
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 右图：热力图（归一化显示Non-IID程度）
    ax2 = axes[1]
    df_norm = df.div(df.sum(axis=1), axis=0)
    
    # 调整注释字体大小，防止类别过多时重叠
    annot_fontsize = max(6, min(10, 200 // (len(df) * len(df.columns))))
    
    sns.heatmap(df_norm, annot=True, fmt='.2f', cmap='YlOrRd', 
                ax=ax2, cbar_kws={'label': 'Ratio'}, 
                linewidths=0.5, linecolor='gray',
                annot_kws={"size": annot_fontsize},
                vmin=0, vmax=1)
    ax2.set_title(f"{title}\n(Normalized per Client)", fontsize=11)
    ax2.set_xlabel(f"Class (Showing {len(df.columns)} of {original_shape[1]})" 
                   if len(df.columns) != original_shape[1] else "Class")
    ax2.set_ylabel("Client ID")
    
    # 调整布局防止标签重叠
    plt.tight_layout()
    
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved to: {save_path}")
        if truncation_info:
            print(f"Note: {warn_msg}")
    else:
        plt.show()


def format_bytes(size: int, precision: int = 2) -> str:
    """
    格式化字节大小为人类可读字符串
    
    Args:
        size: 字节数（支持负数，用于显示差异）
        precision: 小数位数
        
    Returns:
        格式化字符串（如 "1.53 MB", "1023 B"）
        
    Example:
        >>> format_bytes(1536000)
        '1.46 MB'
        >>> format_bytes(1023)
        '1023 B'
    """
    if size == 0:
        return "0 B"
    
    abs_size = abs(size)
    sign = "-" if size < 0 else ""
    
    # 定义单位（二进制标准，1024进制）
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    
    while abs_size >= 1024 and unit_index < len(units) - 1:
        abs_size /= 1024
        unit_index += 1
    
    # 如果是字节级别，不显示小数
    if unit_index == 0:
        return f"{sign}{int(abs_size)} {units[unit_index]}"
    
    return f"{sign}{abs_size:.{precision}f} {units[unit_index]}"

def timer(func: Callable) -> Callable:
    """
    计时装饰器 - 测量函数执行时间
    
    Args:
        func: 被装饰的函数
        
    Returns:
        包装后的函数
        
    Example:
        >>> @timer
        ... def slow_func():
        ...     time.sleep(1)
        ...     
        >>> slow_func()
        [timer] slow_func executed in 1.0023s
    """
    @functools.wraps(func)  # 保留原函数的元数据
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()  # 高精度计时
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 确保即使发生异常也打印时间
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            print(f"[timer] {func.__name__} executed in {elapsed:.4f}s")
    
    return wrapper