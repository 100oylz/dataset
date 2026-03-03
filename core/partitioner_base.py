"""
数据划分基类模块

定义所有数据划分器必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset, Subset

from utils.helpers import load_json, save_json


class PartitionerBase(ABC):
    """
    数据划分抽象基类

    职责：
    1. 将训练数据划分为多个客户端子集
    2. 支持不同的划分策略（IID, Non-IID等）
    3. 提供划分结果的统计信息

    注意：只负责索引划分，不实际存储数据
    """

    def __init__(self, num_clients: int, seed: int = 42, **kwargs) -> None:
        """
        初始化划分器

        Args:
            num_clients: 客户端数量
            seed: 随机种子
            **kwargs: 其他划分特定参数
        """
        self.num_clients = num_clients
        self.seed = seed
        self.kwargs = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        """划分策略名称"""
        pass

    @property
    @abstractmethod
    def strategy_type(self) -> str:
        """
        划分策略类型

        Returns:
            "iid" 或 "non-iid"
        """
        pass

    @abstractmethod
    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行数据划分

        Args:
            dataset: 待划分的数据集

        Returns:
            {client_id: [indices]} 字典
        """
        pass

    def get_client_dataset(
        self, dataset: Dataset, client_id: int, client_indices: Dict[int, List[int]]
    ) -> Subset:
        """
        获取指定客户端的数据子集

        Args:
            dataset: 完整数据集
            client_id: 客户端ID
            client_indices: 划分结果字典

        Returns:
            客户端数据子集

        Raises:
            KeyError: 如果client_id不存在于划分结果中
        """
        if client_id not in client_indices:
            raise KeyError(f"Client ID {client_id} not found in partition results")

        indices = client_indices[client_id]
        return Subset(dataset, indices)

    def get_distribution(
        self, dataset: Dataset, client_indices: Dict[int, List[int]]
    ) -> Dict[int, Dict[int, int]]:
        """
        获取各客户端的数据分布

        Args:
            dataset: 完整数据集
            client_indices: 划分结果字典

        Returns:
            {client_id: {label: count}} 字典
        """
        distribution = {}

        for client_id, indices in client_indices.items():
            # 获取该客户端所有样本的标签
            labels = []
            for idx in indices:
                _, label = dataset[idx]
                # 处理tensor类型的label
                if isinstance(label, torch.Tensor):
                    label = label.item()
                labels.append(int(label))

            # 统计类别分布
            unique, counts = np.unique(labels, return_counts=True)
            client_dist = {
                int(label): int(count) for label, count in zip(unique, counts)
            }
            distribution[client_id] = client_dist

        return distribution

    def get_statistics(
        self, dataset: Dataset, client_indices: Dict[int, List[int]]
    ) -> Dict[str, Any]:
        """
        获取划分的统计信息

        Args:
            dataset: 完整数据集
            client_indices: 划分结果字典

        Returns:
            统计信息字典，包含：
            - num_clients: 客户端数量
            - total_samples: 总样本数
            - samples_per_client: 每个客户端的样本数
            - distribution: 类别分布
            - strategy: 划分策略名称
            - strategy_type: 划分策略类型
        """
        total_samples = sum(len(indices) for indices in client_indices.values())
        samples_per_client = {
            client_id: len(indices) for client_id, indices in client_indices.items()
        }

        distribution = self.get_distribution(dataset, client_indices)

        # 计算一些统计指标
        sample_counts = list(samples_per_client.values())
        mean_samples = np.mean(sample_counts)
        std_samples = np.std(sample_counts)
        min_samples = np.min(sample_counts)
        max_samples = np.max(sample_counts)

        return {
            "num_clients": self.num_clients,
            "total_samples": total_samples,
            "samples_per_client": samples_per_client,
            "distribution": distribution,
            "strategy": self.name,
            "strategy_type": self.strategy_type,
            "statistics": {
                "mean_samples_per_client": float(mean_samples),
                "std_samples_per_client": float(std_samples),
                "min_samples": int(min_samples),
                "max_samples": int(max_samples),
                "imbalance_ratio": float(max_samples / min_samples)
                if min_samples > 0
                else float("inf"),
            },
        }

    def save_partition(self, client_indices: Dict[int, List[int]], path: str) -> None:
        """
        保存划分结果

        Args:
            client_indices: 划分结果字典
            path: 保存路径
        """
        # 将client_indices转换为可序列化的格式
        serializable_indices = {str(k): v for k, v in client_indices.items()}
        save_json(serializable_indices, path)

    def load_partition(self, path: str) -> Dict[int, List[int]]:
        """
        加载划分结果

        Args:
            path: 划分结果文件路径

        Returns:
            划分结果字典
        """
        data = load_json(path)
        # 将字符串键转换回整数键
        return {int(k): v for k, v in data.items()}


class IIDPartitioner(PartitionerBase):
    """
    IID划分器（独立同分布）

    将数据随机均匀分配给所有客户端
    """

    def __init__(self, num_clients: int, seed: int = 42) -> None:
        """
        初始化IID划分器

        Args:
            num_clients: 客户端数量
            seed: 随机种子
        """
        super().__init__(num_clients, seed)

    @property
    def name(self) -> str:
        """返回划分器名称"""
        return "iid"

    @property
    def strategy_type(self) -> str:
        """返回策略类型"""
        return "iid"

    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行IID划分

        随机打乱数据索引，均匀分配给各客户端

        Args:
            dataset: 待划分的数据集

        Returns:
            {client_id: [indices]} 字典
        """
        np.random.seed(self.seed)

        num_samples = len(dataset)
        indices = np.arange(num_samples)
        np.random.shuffle(indices)

        # 均匀分配给各客户端
        samples_per_client = num_samples // self.num_clients
        client_indices = {}

        for client_id in range(self.num_clients):
            start_idx = client_id * samples_per_client
            # 最后一个客户端获得剩余的所有样本
            if client_id == self.num_clients - 1:
                end_idx = num_samples
            else:
                end_idx = (client_id + 1) * samples_per_client

            client_indices[client_id] = indices[start_idx:end_idx].tolist()

        return client_indices


class DirichletPartitioner(PartitionerBase):
    """
    Dirichlet划分器（Non-IID）

    基于Dirichlet分布的Non-IID划分

    Args:
        alpha: Dirichlet分布参数，越小越Non-IID
    """

    def __init__(self, num_clients: int, alpha: float = 0.5, seed: int = 42) -> None:
        """
        初始化Dirichlet划分器

        Args:
            num_clients: 客户端数量
            alpha: Dirichlet分布参数，越小越Non-IID
            seed: 随机种子
        """
        super().__init__(num_clients, seed, alpha=alpha)
        self.alpha = alpha

    @property
    def name(self) -> str:
        """返回划分器名称"""
        return "dirichlet"

    @property
    def strategy_type(self) -> str:
        """返回策略类型"""
        return "non-iid"

    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行Dirichlet划分

        按类别分组，然后使用Dirichlet分布分配样本给各客户端

        Args:
            dataset: 待划分的数据集

        Returns:
            {client_id: [indices]} 字典
        """
        np.random.seed(self.seed)

        # 获取所有标签
        labels = np.array([dataset[i][1] for i in range(len(dataset))])
        if isinstance(labels[0], torch.Tensor):
            labels = np.array([l.item() for l in labels])

        num_classes = len(np.unique(labels))
        num_samples = len(dataset)

        # 按类别组织样本索引
        class_indices = {c: np.where(labels == c)[0] for c in range(num_classes)}

        # 为每个类别打乱索引
        for c in class_indices:
            np.random.shuffle(class_indices[c])

        # 使用Dirichlet分布为每个类别分配样本比例
        client_indices = {i: [] for i in range(self.num_clients)}

        for c in range(num_classes):
            indices = class_indices[c]
            if len(indices) == 0:
                continue

            # 生成Dirichlet分布的采样比例
            proportions = np.random.dirichlet(np.repeat(self.alpha, self.num_clients))

            # 根据比例分配样本数
            split_points = (np.cumsum(proportions) * len(indices)).astype(int)[:-1]

            # 划分样本给各客户端
            splits = np.split(indices, split_points)

            for client_id, split in enumerate(splits):
                client_indices[client_id].extend(split.tolist())

        # 将列表转换为numpy数组并打乱（可选，保持客户端内部随机）
        for client_id in client_indices:
            indices = np.array(client_indices[client_id])
            np.random.shuffle(indices)
            client_indices[client_id] = indices.tolist()

        return client_indices


class PathologicalPartitioner(PartitionerBase):
    """
    病态划分器（Pathological Non-IID）

    每个客户端只获得特定数量的类别

    Args:
        shards_per_client: 每个客户端的类别数（shard数）
    """

    def __init__(
        self, num_clients: int, shards_per_client: int = 2, seed: int = 42
    ) -> None:
        """
        初始化病态划分器

        Args:
            num_clients: 客户端数量
            shards_per_client: 每个客户端的类别数（shard数）
            seed: 随机种子
        """
        super().__init__(num_clients, seed, shards_per_client=shards_per_client)
        self.shards_per_client = shards_per_client

    @property
    def name(self) -> str:
        """返回划分器名称"""
        return "pathological"

    @property
    def strategy_type(self) -> str:
        """返回策略类型"""
        return "non-iid"

    def partition(self, dataset: Dataset) -> Dict[int, List[int]]:
        """
        执行病态划分

        将数据按类别排序后分成num_clients*shards_per_client个shard，
        每个客户端获得shards_per_client个shard

        Args:
            dataset: 待划分的数据集

        Returns:
            {client_id: [indices]} 字典

        Raises:
            ValueError: 如果shard数量不足
        """
        np.random.seed(self.seed)

        # 获取所有标签
        labels = np.array([dataset[i][1] for i in range(len(dataset))])
        if isinstance(labels[0], torch.Tensor):
            labels = np.array([l.item() for l in labels])

        num_samples = len(dataset)
        total_shards = self.num_clients * self.shards_per_client

        # 按标签排序所有样本
        sorted_indices = np.argsort(labels)

        # 计算每个shard的大小
        shard_size = num_samples // total_shards

        if shard_size == 0:
            raise ValueError(
                f"Too many shards ({total_shards}) for {num_samples} samples. "
                f"Each shard would have {shard_size} samples."
            )

        # 创建shards
        shards = []
        for shard_id in range(total_shards):
            start_idx = shard_id * shard_size
            # 最后一个shard获得剩余样本
            if shard_id == total_shards - 1:
                end_idx = num_samples
            else:
                end_idx = (shard_id + 1) * shard_size

            shard = sorted_indices[start_idx:end_idx]
            shards.append(shard)

        # 随机打乱shards的分配顺序
        np.random.shuffle(shards)

        # 分配shards给客户端
        client_indices = {}
        for client_id in range(self.num_clients):
            client_shards = []
            for i in range(self.shards_per_client):
                shard_idx = client_id * self.shards_per_client + i
                if shard_idx < len(shards):
                    client_shards.append(shards[shard_idx])

            # 合并shards并打乱
            if client_shards:
                combined = np.concatenate(client_shards)
                np.random.shuffle(combined)
                client_indices[client_id] = combined.tolist()
            else:
                client_indices[client_id] = []

        return client_indices
