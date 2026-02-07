#!/bin/bash
# RequirementParser Agent 部署脚本
# Requirements: 7.1, 7.2, 7.3

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必需的工具
check_requirements() {
    log_info "检查部署环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_info "环境检查通过"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f ".env" ]; then
        log_error ".env 文件不存在"
        log_info "请复制 .env.template 为 .env 并填写配置"
        log_info "命令: cp .env.template .env"
        exit 1
    fi
    
    # 检查必需的环境变量
    source .env
    
    if [ -z "$REQ_PARSER_DEEPSEEK_API_KEY" ] || [ "$REQ_PARSER_DEEPSEEK_API_KEY" = "your_deepseek_api_key_here" ]; then
        log_error "DeepSeek API Key 未配置"
        log_info "请在 .env 文件中设置 REQ_PARSER_DEEPSEEK_API_KEY"
        exit 1
    fi
    
    log_info "配置文件检查通过"
}

# 构建 Docker 镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    docker-compose build --no-cache
    
    if [ $? -eq 0 ]; then
        log_info "镜像构建成功"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_info "服务启动成功"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 检查服务健康状态
check_health() {
    log_info "检查服务健康状态..."
    
    # 等待服务启动
    sleep 5
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_info "服务运行正常"
    else
        log_error "服务未正常运行"
        log_info "查看日志: docker-compose logs"
        exit 1
    fi
}

# 显示服务信息
show_info() {
    log_info "部署完成！"
    echo ""
    echo "服务信息:"
    echo "  - RequirementParser Agent: 运行中"
    echo "  - Redis (Event Bus): localhost:6379"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止服务: docker-compose down"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 查看状态: docker-compose ps"
    echo ""
}

# 主函数
main() {
    log_info "开始部署 RequirementParser Agent..."
    
    check_requirements
    check_config
    build_image
    start_services
    check_health
    show_info
    
    log_info "部署成功完成！"
}

# 执行主函数
main
