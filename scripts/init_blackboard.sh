#!/bin/bash

# Blackboard 基础设施初始化脚本

set -e

echo "=== Blackboard Infrastructure Initialization ==="

# 等待 PostgreSQL 启动
echo "Waiting for PostgreSQL..."
until docker exec blackboard_postgres pg_isready -U postgres > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " PostgreSQL is ready!"

# 等待 Redis 启动
echo "Waiting for Redis..."
until docker exec blackboard_redis redis-cli ping > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " Redis is ready!"

# 等待 MinIO 启动
echo "Waiting for MinIO..."
until docker exec blackboard_minio curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo " MinIO is ready!"

# 执行数据库初始化（已通过 docker-entrypoint-initdb.d 自动执行）
echo "Database schema initialized via docker-entrypoint-initdb.d"

# 创建 MinIO bucket
echo "Creating MinIO bucket..."
docker exec blackboard_minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec blackboard_minio mc mb local/artifacts --ignore-existing
echo " MinIO bucket 'artifacts' created!"

# 测试连接
echo "Testing connections..."

# 测试 PostgreSQL
docker exec blackboard_postgres psql -U postgres -d blackboard -c "SELECT 'PostgreSQL connection OK' AS status;" || echo "PostgreSQL test failed"

# 测试 Redis
docker exec blackboard_redis redis-cli ping || echo "Redis test failed"

# 测试 MinIO
docker exec blackboard_minio mc ls local/artifacts || echo "MinIO test failed"

echo ""
echo "=== Initialization Complete! ==="
echo ""
echo "Services:"
echo "  PostgreSQL: localhost:5432 (user: postgres, password: password, db: blackboard)"
echo "  Redis:      localhost:6379"
echo "  MinIO:      localhost:9000 (console: localhost:9001)"
echo "              Access Key: minioadmin"
echo "              Secret Key: minioadmin"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo ""
