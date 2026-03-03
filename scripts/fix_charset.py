#!/usr/bin/env python3
"""
MySQL 字符集修复脚本

用于检查并修复数据库、表和列的字符集为 utf8mb4
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import get_db, DatabaseConfig


def check_charset():
    """检查当前数据库字符集设置"""
    db = get_db()
    
    print("=" * 60)
    print("MySQL 字符集检查")
    print("=" * 60)
    
    # 检查服务器字符集
    print("\n📋 服务器字符集设置:")
    result = db.fetchall("""
        SHOW VARIABLES WHERE Variable_name LIKE 'character_set_%' 
        OR Variable_name LIKE 'collation%'
    """)
    for row in result:
        print(f"  {row['Variable_name']}: {row['Value']}")
    
    # 检查数据库字符集
    print("\n📋 数据库字符集:")
    config = DatabaseConfig()
    result = db.fetchone("""
        SELECT SCHEMA_NAME as schema_name, DEFAULT_CHARACTER_SET_NAME as default_character_set_name, DEFAULT_COLLATION_NAME as default_collation_name
        FROM information_schema.schemata
        WHERE SCHEMA_NAME = %s
    """, (config.database,))
    if result:
        print(f"  数据库: {result.get('schema_name', config.database)}")
        print(f"  字符集: {result.get('default_character_set_name', 'N/A')}")
        print(f"  排序规则: {result.get('default_collation_name', 'N/A')}")
    
    # 检查表字符集
    print("\n📋 表字符集:")
    result = db.fetchall("""
        SELECT TABLE_NAME as table_name, TABLE_COLLATION as table_collation
        FROM information_schema.tables
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
    """, (config.database,))
    for row in result:
        collation = row.get('table_collation', '')
        status = "✅" if collation and 'utf8mb4' in collation else "⚠️"
        print(f"  {status} {row.get('table_name', 'N/A')}: {collation}")
    
    return True


def fix_database_charset():
    """修复数据库字符集"""
    db = get_db()
    config = DatabaseConfig()
    
    print("\n" + "=" * 60)
    print("修复数据库字符集")
    print("=" * 60)
    
    # 修改数据库字符集
    print(f"\n🔄 修改数据库 '{config.database}' 字符集...")
    db.execute(f"""
        ALTER DATABASE `{config.database}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """)
    print("✅ 数据库字符集已修改")


def fix_tables_charset():
    """修复所有表的字符集"""
    db = get_db()
    config = DatabaseConfig()
    
    print("\n🔄 修复表字符集...")
    
    # 获取所有表
    tables = db.fetchall("""
        SELECT TABLE_NAME as table_name
        FROM information_schema.tables
        WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
    """, (config.database,))
    
    for table in tables:
        table_name = table.get('table_name', '')
        print(f"  🔄 修改表: {table_name}")
        db.execute(f"""
            ALTER TABLE `{table_name}`
            CONVERT TO CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
        """)
    
    print(f"✅ 共修复 {len(tables)} 个表")


def fix_all():
    """执行完整修复流程"""
    try:
        # 先检查
        check_charset()
        
        # 询问是否修复
        print("\n" + "=" * 60)
        response = input("是否修复字符集? (y/N): ").strip().lower()
        
        if response == 'y':
            fix_database_charset()
            fix_tables_charset()
            
            print("\n" + "=" * 60)
            print("✅ 字符集修复完成!")
            print("=" * 60)
            
            # 再次检查
            check_charset()
        else:
            print("已取消")
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MySQL 字符集修复工具')
    parser.add_argument('--check', action='store_true', help='仅检查字符集')
    parser.add_argument('--fix', action='store_true', help='修复字符集')
    
    args = parser.parse_args()
    
    if args.check:
        check_charset()
    elif args.fix:
        fix_all()
    else:
        # 默认执行检查
        check_charset()
        print("\n提示: 使用 --fix 参数执行修复")
