#!/usr/bin/env python3
"""
数据集注册脚本

将 datasets/configs/ 下的 JSON 配置导入到数据库

用法:
    python scripts/register_datasets.py
    python scripts/register_datasets.py --overwrite
    python scripts/register_datasets.py --datasets ./custom/datasets.json
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from datasets import register_all


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="将数据集和划分策略配置导入到数据库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置导入
  python scripts/register_datasets.py
  
  # 强制覆盖已有数据
  python scripts/register_datasets.py --overwrite
  
  # 使用自定义配置文件
  python scripts/register_datasets.py --datasets ./my_datasets.json --strategies ./my_strategies.json
        """
    )
    
    parser.add_argument(
        "--datasets", "-d",
        help="数据集 JSON 配置文件路径 (默认: datasets/configs/datasets.json)"
    )
    parser.add_argument(
        "--strategies", "-s",
        help="划分策略 JSON 配置文件路径 (默认: datasets/configs/partition_strategies.json)"
    )
    parser.add_argument(
        "--overwrite", "-o",
        action="store_true",
        default=True,
        help="覆盖数据库中已存在的数据 (默认: True)"
    )
    parser.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        help="不覆盖已有数据，跳过已存在的记录"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    args = parser.parse_args()
    
    # 配置日志
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    print("=" * 60)
    print("数据集注册导入工具")
    print("=" * 60)
    
    # 显示配置
    datasets_path = args.datasets or "datasets/configs/datasets.json"
    strategies_path = args.strategies or "datasets/configs/partition_strategies.json"
    
    print(f"\n配置:")
    print(f"  数据集配置: {datasets_path}")
    print(f"  策略配置: {strategies_path}")
    print(f"  覆盖模式: {args.overwrite}")
    print()
    
    # 执行导入
    try:
        stats = register_all(
            overwrite=args.overwrite,
            datasets_json=args.datasets,
            strategies_json=args.strategies
        )
        
        print("\n" + "=" * 60)
        print("导入完成!")
        print("=" * 60)
        print(f"  数据集: {stats['datasets']} 个")
        print(f"  划分策略: {stats['strategies']} 个")
        print()
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: 配置文件不存在 - {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
