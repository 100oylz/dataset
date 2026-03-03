#!/bin/bash
# ============================================
# 数据库初始化脚本（带 UTF-8 字符集支持）
# ============================================

set -e

echo "========================================"
echo "Initializing Database with UTF-8"
echo "========================================"

# 等待 MySQL 就绪
echo "Waiting for MySQL to be ready..."
until docker exec fl_dataset_mysql mysqladmin -u root -prootpassword ping --silent 2>/dev/null; do
    echo "MySQL is not ready yet, waiting..."
    sleep 2
done

echo "MySQL is ready!"

# 使用 UTF-8 字符集执行初始化 SQL
echo "Executing seed data with UTF-8 charset..."
docker exec -i fl_dataset_mysql mysql -u root -prootpassword \
    --default-character-set=utf8mb4 \
    fl_dataset_db < ./database/init/02_seed_data.sql

echo ""
echo "========================================"
echo "Database initialized successfully!"
echo "========================================"

# 验证数据
echo ""
echo "Verifying data..."
docker exec fl_dataset_mysql mysql -u fl_user -pflpassword -e "
USE fl_dataset_db;
SELECT 'Partition Strategies' as table_name, COUNT(*) as count FROM partition_strategies
UNION ALL
SELECT 'Dataset Registrations', COUNT(*) FROM dataset_registrations;
" 2>/dev/null

echo ""
echo "Sample data (Chinese):"
docker exec fl_dataset_mysql mysql -u fl_user -pflpassword -e "
USE fl_dataset_db;
SELECT name, display_name FROM partition_strategies LIMIT 3;
" 2>/dev/null
