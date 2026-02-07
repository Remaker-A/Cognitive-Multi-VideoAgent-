@echo off
REM RequirementParser Agent 部署脚本 (Windows)
REM Requirements: 7.1, 7.2, 7.3

setlocal enabledelayedexpansion

echo ========================================
echo RequirementParser Agent 部署脚本
echo ========================================
echo.

REM 检查 Docker
echo [INFO] 检查 Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未安装，请先安装 Docker Desktop
    exit /b 1
)

REM 检查 Docker Compose
echo [INFO] 检查 Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose 未安装
    exit /b 1
)

echo [INFO] 环境检查通过
echo.

REM 检查配置文件
echo [INFO] 检查配置文件...
if not exist ".env" (
    echo [ERROR] .env 文件不存在
    echo [INFO] 请复制 .env.template 为 .env 并填写配置
    echo [INFO] 命令: copy .env.template .env
    exit /b 1
)

echo [INFO] 配置文件检查通过
echo.

REM 构建镜像
echo [INFO] 构建 Docker 镜像...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] 镜像构建失败
    exit /b 1
)

echo [INFO] 镜像构建成功
echo.

REM 启动服务
echo [INFO] 启动服务...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 服务启动失败
    exit /b 1
)

echo [INFO] 服务启动成功
echo.

REM 等待服务启动
echo [INFO] 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
echo [INFO] 检查服务状态...
docker-compose ps

echo.
echo ========================================
echo 部署完成！
echo ========================================
echo.
echo 服务信息:
echo   - RequirementParser Agent: 运行中
echo   - Redis (Event Bus): localhost:6379
echo.
echo 常用命令:
echo   - 查看日志: docker-compose logs -f
echo   - 停止服务: docker-compose down
echo   - 重启服务: docker-compose restart
echo   - 查看状态: docker-compose ps
echo.

endlocal
