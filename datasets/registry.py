"""
数据集注册模块

提供从 JSON 配置文件导入数据集和划分策略到数据库的功能
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# 导入数据库连接
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.db_connection import get_db, DatabaseConfig

logger = logging.getLogger(__name__)

# 默认配置文件路径
DEFAULT_CONFIG_DIR = Path(__file__).parent / "configs"
DATASETS_JSON = DEFAULT_CONFIG_DIR / "datasets.json"
STRATEGIES_JSON = DEFAULT_CONFIG_DIR / "partition_strategies.json"


class DatasetRegistryImporter:
    """
    数据集注册导入器
    
    从 JSON 配置文件读取数据集信息并导入到数据库
    """
    
    def __init__(self, db_connection=None):
        """
        初始化导入器
        
        Args:
            db_connection: 数据库连接对象，默认使用全局连接
        """
        self._db = db_connection or get_db()
    
    def _load_json(self, json_path: Path) -> Dict[str, Any]:
        """
        加载 JSON 文件
        
        Args:
            json_path: JSON 文件路径
            
        Returns:
            解析后的字典
            
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        if not json_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _prepare_dataset_data(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备数据集数据，将 dict 转换为数据库格式
        
        Args:
            dataset: 原始数据集字典
            
        Returns:
            准备好的数据字典
        """
        data = dataset.copy()
        
        # 转换 JSON 字段
        if "extra_params" in data and isinstance(data["extra_params"], dict):
            data["extra_params"] = json.dumps(data["extra_params"], ensure_ascii=False)
        
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = json.dumps(data["tags"], ensure_ascii=False)
        
        return data
    
    def _prepare_strategy_data(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备划分策略数据，将 dict 转换为数据库格式
        
        Args:
            strategy: 原始策略字典
            
        Returns:
            准备好的数据字典
        """
        data = strategy.copy()
        
        # 转换 JSON 字段
        if "default_params" in data and isinstance(data["default_params"], dict):
            data["default_params"] = json.dumps(data["default_params"], ensure_ascii=False)
        
        if "param_schema" in data and isinstance(data["param_schema"], dict):
            data["param_schema"] = json.dumps(data["param_schema"], ensure_ascii=False)
        
        if "supported_datasets" in data and isinstance(data["supported_datasets"], list):
            data["supported_datasets"] = json.dumps(data["supported_datasets"], ensure_ascii=False)
        
        return data
    
    def import_datasets(
        self,
        json_path: Optional[Path] = None,
        overwrite: bool = True
    ) -> int:
        """
        导入数据集到数据库
        
        Args:
            json_path: 数据集 JSON 文件路径，默认使用 datasets.json
            overwrite: 是否覆盖已存在的数据
            
        Returns:
            导入的数据集数量
            
        Example:
            >>> importer = DatasetRegistryImporter()
            >>> count = importer.import_datasets()
            >>> print(f"Imported {count} datasets")
        """
        json_path = json_path or DATASETS_JSON
        data = self._load_json(json_path)
        
        datasets = data.get("datasets", [])
        if not datasets:
            logger.warning(f"没有找到数据集配置: {json_path}")
            return 0
        
        imported_count = 0
        
        for dataset in datasets:
            try:
                prepared_data = self._prepare_dataset_data(dataset)
                
                if overwrite:
                    # 使用 INSERT ... ON DUPLICATE KEY UPDATE
                    self._upsert_dataset(prepared_data)
                else:
                    # 仅插入新数据
                    try:
                        self._db.insert("dataset_registrations", prepared_data)
                    except Exception as e:
                        logger.warning(f"数据集 '{dataset['name']}' 已存在，跳过: {e}")
                        continue
                
                imported_count += 1
                logger.info(f"已导入数据集: {dataset['name']}")
                
            except Exception as e:
                logger.error(f"导入数据集 '{dataset.get('name', 'unknown')}' 失败: {e}")
                continue
        
        return imported_count
    
    def import_strategies(
        self,
        json_path: Optional[Path] = None,
        overwrite: bool = True
    ) -> int:
        """
        导入划分策略到数据库
        
        Args:
            json_path: 策略 JSON 文件路径，默认使用 partition_strategies.json
            overwrite: 是否覆盖已存在的策略
            
        Returns:
            导入的策略数量
            
        Example:
            >>> importer = DatasetRegistryImporter()
            >>> count = importer.import_strategies()
            >>> print(f"Imported {count} strategies")
        """
        json_path = json_path or STRATEGIES_JSON
        data = self._load_json(json_path)
        
        strategies = data.get("strategies", [])
        if not strategies:
            logger.warning(f"没有找到策略配置: {json_path}")
            return 0
        
        imported_count = 0
        
        for strategy in strategies:
            try:
                prepared_data = self._prepare_strategy_data(strategy)
                
                if overwrite:
                    # 使用 INSERT ... ON DUPLICATE KEY UPDATE
                    self._upsert_strategy(prepared_data)
                else:
                    # 仅插入新数据
                    try:
                        self._db.insert("partition_strategies", prepared_data)
                    except Exception as e:
                        logger.warning(f"策略 '{strategy['name']}' 已存在，跳过: {e}")
                        continue
                
                imported_count += 1
                logger.info(f"已导入策略: {strategy['name']}")
                
            except Exception as e:
                logger.error(f"导入策略 '{strategy.get('name', 'unknown')}' 失败: {e}")
                continue
        
        return imported_count
    
    def _upsert_dataset(self, data: Dict[str, Any]) -> None:
        """
        插入或更新数据集
        
        Args:
            data: 数据集数据
        """
        # 构建 INSERT ... ON DUPLICATE KEY UPDATE 语句
        columns = list(data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f"`{c}`" for c in columns])
        
        # ON DUPLICATE KEY UPDATE 部分（排除主键 name）
        update_clause = ', '.join([
            f"`{c}` = VALUES(`{c}`)"
            for c in columns if c != 'name'
        ])
        
        sql = f"""
            INSERT INTO `dataset_registrations` ({column_names})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}, `updated_at` = CURRENT_TIMESTAMP
        """
        
        with self._db.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
    
    def _upsert_strategy(self, data: Dict[str, Any]) -> None:
        """
        插入或更新策略
        
        Args:
            data: 策略数据
        """
        # 构建 INSERT ... ON DUPLICATE KEY UPDATE 语句
        columns = list(data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names = ', '.join([f"`{c}`" for c in columns])
        
        # ON DUPLICATE KEY UPDATE 部分（排除主键 name）
        update_clause = ', '.join([
            f"`{c}` = VALUES(`{c}`)"
            for c in columns if c != 'name'
        ])
        
        sql = f"""
            INSERT INTO `partition_strategies` ({column_names})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}, `updated_at` = CURRENT_TIMESTAMP
        """
        
        with self._db.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
    
    def import_all(
        self,
        datasets_json: Optional[Path] = None,
        strategies_json: Optional[Path] = None,
        overwrite: bool = True
    ) -> Dict[str, int]:
        """
        导入所有配置到数据库
        
        Args:
            datasets_json: 数据集 JSON 路径
            strategies_json: 策略 JSON 路径
            overwrite: 是否覆盖已有数据
            
        Returns:
            导入统计信息 {"datasets": int, "strategies": int}
            
        Example:
            >>> importer = DatasetRegistryImporter()
            >>> stats = importer.import_all()
            >>> print(f"Imported {stats['datasets']} datasets and {stats['strategies']} strategies")
        """
        return {
            "datasets": self.import_datasets(datasets_json, overwrite),
            "strategies": self.import_strategies(strategies_json, overwrite)
        }
    
    def export_datasets(
        self,
        output_path: Optional[Path] = None,
        include_inactive: bool = False
    ) -> Path:
        """
        从数据库导出数据集到 JSON
        
        Args:
            output_path: 输出路径，默认使用默认配置文件路径
            include_inactive: 是否包含非活跃状态的数据集
            
        Returns:
            输出文件路径
        """
        output_path = output_path or DATASETS_JSON
        
        sql = "SELECT * FROM dataset_registrations"
        if not include_inactive:
            sql += " WHERE status = 'active'"
        
        rows = self._db.fetchall(sql)
        
        datasets = []
        for row in rows:
            # 转换 JSON 字符串回对象
            dataset = dict(row)
            for key in ["extra_params", "tags"]:
                if dataset.get(key) and isinstance(dataset[key], str):
                    try:
                        dataset[key] = json.loads(dataset[key])
                    except json.JSONDecodeError:
                        pass
            datasets.append(dataset)
        
        output = {"datasets": datasets}
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出 {len(datasets)} 个数据集到: {output_path}")
        return output_path


def register_all(
    overwrite: bool = True,
    datasets_json: Optional[str] = None,
    strategies_json: Optional[str] = None
) -> Dict[str, int]:
    """
    便捷函数：导入所有数据集和策略到数据库
    
    Args:
        overwrite: 是否覆盖已有数据
        datasets_json: 数据集 JSON 文件路径（可选）
        strategies_json: 策略 JSON 文件路径（可选）
        
    Returns:
        导入统计信息
        
    Example:
        >>> from datasets.registry import register_all
        >>> stats = register_all()
        >>> print(f"Imported {stats['datasets']} datasets")
    """
    importer = DatasetRegistryImporter()
    
    ds_path = Path(datasets_json) if datasets_json else None
    st_path = Path(strategies_json) if strategies_json else None
    
    return importer.import_all(ds_path, st_path, overwrite)


def register_datasets(
    json_path: Optional[str] = None,
    overwrite: bool = True
) -> int:
    """
    便捷函数：仅导入数据集
    
    Args:
        json_path: JSON 文件路径（可选）
        overwrite: 是否覆盖已有数据
        
    Returns:
        导入数量
    """
    importer = DatasetRegistryImporter()
    path = Path(json_path) if json_path else None
    return importer.import_datasets(path, overwrite)


def register_strategies(
    json_path: Optional[str] = None,
    overwrite: bool = True
) -> int:
    """
    便捷函数：仅导入划分策略
    
    Args:
        json_path: JSON 文件路径（可选）
        overwrite: 是否覆盖已有数据
        
    Returns:
        导入数量
    """
    importer = DatasetRegistryImporter()
    path = Path(json_path) if json_path else None
    return importer.import_strategies(path, overwrite)


if __name__ == "__main__":
    # 命令行用法
    import argparse
    
    parser = argparse.ArgumentParser(description="导入数据集和策略到数据库")
    parser.add_argument("--datasets", "-d", help="数据集 JSON 文件路径")
    parser.add_argument("--strategies", "-s", help="策略 JSON 文件路径")
    parser.add_argument("--overwrite", "-o", action="store_true", default=True, help="覆盖已有数据")
    parser.add_argument("--no-overwrite", dest="overwrite", action="store_false", help="不覆盖已有数据")
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # 执行导入
    stats = register_all(
        overwrite=args.overwrite,
        datasets_json=args.datasets,
        strategies_json=args.strategies
    )
    
    print(f"\n导入完成:")
    print(f"  - 数据集: {stats['datasets']} 个")
    print(f"  - 划分策略: {stats['strategies']} 个")
