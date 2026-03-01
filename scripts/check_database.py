#!/usr/bin/env python3
"""
数据库检查工具

用于查看数据库中的表结构和数据
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import ftfy
from database import get_db, DatabaseConfig


def fix_encoding(text):
    """修复编码问题 - 使用 ftfy 修复 mojibake"""
    if text is None:
        return ""
    if isinstance(text, str):
        # 使用 ftfy 修复乱码
        fixed = ftfy.fix_text(text)
        # 如果修复后仍有乱码特征（如 â€œ），说明是截断的乱码，无法完全修复
        if 'â' in fixed or 'Ã' in fixed:
            # 尝试部分修复 - 移除无法识别的字符
            import re
            # 保留可打印字符和中文字符
            fixed = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\-\_\.\/\:\,\(\)\[\]\{\}\"\'\;\@\#\$\%\&\*\+\=\?\!\<\>\\\|\`\~]', '', fixed)
        return fixed
    return str(text)


def print_separator(title: str = ""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")


def check_connection():
    """检查数据库连接"""
    config = DatabaseConfig()
    print_separator("数据库连接信息")
    print(f"主机: {config.host}:{config.port}")
    print(f"数据库: {config.database}")
    print(f"用户: {config.user}")
    
    db = get_db()
    try:
        if db.is_connected():
            print("✓ 数据库连接正常")
        else:
            print("✗ 数据库未连接，尝试连接...")
            db.connect()
            # 设置字符集为 utf8mb4
            with db.cursor() as cursor:
                cursor.execute("SET NAMES utf8mb4")
                cursor.execute("SET CHARACTER SET utf8mb4")
            print("✓ 连接成功")
        return True
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def list_tables():
    """列出所有表"""
    db = get_db()
    
    print_separator("数据库表列表")
    
    try:
        tables = db.fetchall("""
            SELECT TABLE_NAME, TABLE_COMMENT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
        """)
        
        if not tables:
            print("数据库中没有表")
            return
        
        print(f"{'表名':<30} {'注释':<30}")
        print("-" * 60)
        for table in tables:
            name = fix_encoding(table['TABLE_NAME'])
            comment = fix_encoding(table['TABLE_COMMENT']) or "(无)"
            print(f"{name:<30} {comment:<30}")
        
        return [t['TABLE_NAME'] for t in tables]
    except Exception as e:
        print(f"查询表列表失败: {e}")
        return []


def show_table_structure(table_name: str):
    """显示表结构"""
    db = get_db()
    
    print_separator(f"表结构: {table_name}")
    
    try:
        columns = db.fetchall(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_COMMENT,
                EXTRA
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, (table_name,))
        
        if not columns:
            print(f"表 '{table_name}' 不存在或没有列")
            return
        
        print(f"{'列名':<25} {'类型':<15} {'可空':<6} {'默认值':<15} {'注释'}")
        print("-" * 100)
        
        for col in columns:
            name = fix_encoding(col['COLUMN_NAME'])
            data_type = fix_encoding(col['DATA_TYPE'])
            nullable = fix_encoding(col['IS_NULLABLE'])
            default = fix_encoding(col['COLUMN_DEFAULT']) if col['COLUMN_DEFAULT'] else ""
            comment = fix_encoding(col['COLUMN_COMMENT']) or ""
            extra = fix_encoding(col['EXTRA'])
            
            if len(default) > 12:
                default = default[:12] + "..."
            
            print(f"{name:<25} {data_type:<15} {nullable:<6} {default:<15} {comment}")
            if extra:
                print(f"  └─ {extra}")
        
        # 显示索引信息
        indexes = db.fetchall(f"""
            SELECT 
                INDEX_NAME,
                COLUMN_NAME,
                NON_UNIQUE
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """, (table_name,))
        
        if indexes:
            print(f"\n索引:")
            print(f"{'索引名':<25} {'列名':<25} {'唯一'}")
            print("-" * 60)
            for idx in indexes:
                unique = "否" if idx['NON_UNIQUE'] else "是"
                idx_name = fix_encoding(idx['INDEX_NAME'])
                col_name = fix_encoding(idx['COLUMN_NAME'])
                print(f"{idx_name:<25} {col_name:<25} {unique}")
                
    except Exception as e:
        print(f"查询表结构失败: {e}")


def show_table_data(table_name: str, limit: int = 10):
    """显示表数据"""
    db = get_db()
    
    print_separator(f"表数据: {table_name} (前 {limit} 条)")
    
    try:
        # 获取总数
        count_result = db.fetchone(f"SELECT COUNT(*) as count FROM {table_name}")
        total = count_result['count'] if count_result else 0
        print(f"总记录数: {total}\n")
        
        if total == 0:
            print("表中没有数据")
            return
        
        # 获取数据
        rows = db.fetchall(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
        
        if not rows:
            print("没有数据")
            return
        
        # 打印表头
        columns = list(rows[0].keys())
        fixed_columns = [fix_encoding(c) for c in columns]
        print(f"{' | '.join(fixed_columns)}")
        print("-" * 100)
        
        # 打印数据
        for row in rows:
            values = []
            for col in columns:
                val = row[col]
                if val is None:
                    val = "NULL"
                elif isinstance(val, (dict, list)):
                    val = str(val)[:30] + "..." if len(str(val)) > 30 else str(val)
                else:
                    val = str(val)
                    if len(val) > 30:
                        val = val[:30] + "..."
                values.append(fix_encoding(val))
            print(f"{' | '.join(values)}")
        
        if total > limit:
            print(f"\n... 还有 {total - limit} 条记录 ...")
            
    except Exception as e:
        print(f"查询表数据失败: {e}")


def show_dataset_registrations():
    """显示数据集注册信息"""
    show_table_data("dataset_registrations")


def show_partition_strategies():
    """显示划分策略"""
    show_table_data("partition_strategies")


def show_partition_results():
    """显示划分结果"""
    show_table_data("partition_results")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库检查工具")
    parser.add_argument("--structure", "-s", action="store_true", help="显示表结构")
    parser.add_argument("--data", "-d", action="store_true", help="显示表数据")
    parser.add_argument("--table", "-t", type=str, help="指定表名")
    parser.add_argument("--limit", "-l", type=int, default=10, help="限制显示的记录数")
    parser.add_argument("--all", "-a", action="store_true", help="显示所有信息")
    
    args = parser.parse_args()
    
    # 检查连接
    if not check_connection():
        sys.exit(1)
    
    # 如果没有指定任何选项，默认显示表列表
    if not any([args.structure, args.data, args.table, args.all]):
        tables = list_tables()
        if tables:
            print(f"\n使用 -s 查看表结构，-d 查看表数据")
            print(f"例如: python {sys.argv[0]} -s -t dataset_registrations")
        sys.exit(0)
    
    # 列出所有表
    if args.all:
        tables = list_tables()
        for table in tables:
            show_table_structure(table)
            show_table_data(table, args.limit)
        return
    
    # 显示指定表
    if args.table:
        if args.structure:
            show_table_structure(args.table)
        if args.data:
            show_table_data(args.table, args.limit)
        if not args.structure and not args.data:
            # 默认同时显示结构和数据
            show_table_structure(args.table)
            show_table_data(args.table, args.limit)
    else:
        # 显示所有表
        tables = list_tables()
        
        if args.structure:
            for table in tables:
                show_table_structure(table)
        
        if args.data:
            for table in tables:
                show_table_data(table, args.limit)


if __name__ == "__main__":
    main()
