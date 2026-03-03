#!/bin/bash

# ============================================================
# 自动化部署脚本 - HuanHe-Base 终极优化版
# 功能：
# 1. 强制同步 Git 代码
# 2. 更新 Python 依赖
# 3. 初始化数据库 & 重置标准账号 (替代旧版 create_admin)
# 4. 修复权限与目录
# 5. 重启服务 (Supervisor)
# ============================================================

# 1. 定义项目核心路径
PROJECT_DIR="/www/wwwroot/HuanHe-Base"
VENV_PATH="$PROJECT_DIR/venv"
PYTHON_BIN="$VENV_PATH/bin/python3"
PIP_BIN="$VENV_PATH/bin/pip3"

# 确保进入正确目录
cd $PROJECT_DIR || { echo "❌ 找不到项目目录: $PROJECT_DIR"; exit 1; }

echo "========== 1. 强制同步代码 (解决卡顿与权限) =========="

# 【修复】自动解除 Git 安全目录限制
git config --global --add safe.directory $PROJECT_DIR

# 清除旧的编译缓存
find . -name "*.pyc" -delete

# 【优化】增加超时限制，防止 Git 卡死
echo "正在从 GitHub 获取更新 (限时 60s)..."
timeout 60s git fetch --all

if [ $? -eq 124 ]; then
    echo "❌ Git 同步超时！请检查服务器网络连接。"
    exit 1
fi

# 【优化】自动识别当前分支并强制重置
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "当前分支: $CURRENT_BRANCH，正在执行强制重置..."
git reset --hard origin/$CURRENT_BRANCH

# 打印最新提交信息
echo "最新提交信息: $(git log -1 --pretty=format:'%h - %s (%cr)')"

echo "========== 2. 更新虚拟环境依赖 (pip) =========="
if [ -f "requirements.txt" ]; then
    # 使用清华源加速
    $PIP_BIN install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
else
    echo "⚠️ 跳过：未找到 requirements.txt"
fi

echo "========== 3. 执行数据库初始化与账号重置 =========="
# 【核心修改】使用新的 init_database.py -y 替代旧的 create_admin.py
# 这将自动完成：
# 1. 数据库迁移（添加字段）
# 2. 创建/重置 6 个标准账号
# 3. 强制解绑设备和清空 Session
if [ -f "scripts/init_database.py" ]; then
    echo "正在执行数据库初始化与账号重置..."
    $PYTHON_BIN scripts/init_database.py -y
else
    echo "❌ 错误：未找到 scripts/init_database.py"
    exit 1
fi

echo "========== 4. 修复目录权限 (www用户) =========="
# 确保所有文件属于 www 用户
chown -R www:www $PROJECT_DIR
# 设置目录权限
find $PROJECT_DIR -type d -exec chmod 755 {} \;
# 设置文件权限
find $PROJECT_DIR -type f -exec chmod 644 {} \;
# 脚本文件赋予执行权限
chmod +x deploy.sh

# 【关键】确保数据库文件对 www 具有读写权
if [ -f "app.db" ]; then
    chmod 664 app.db
    chown www:www app.db
fi

# 【关键】确保日志和上传目录存在且可写
mkdir -p logs static/uploads
chown -R www:www logs static/uploads
chmod -R 777 logs static/uploads

echo "========== 5. 自动重启所有服务 (对接守护进程) =========="

# 重启 Celery Worker
echo "正在重启 Celery Worker..."
/usr/bin/supervisorctl restart HuanHe_Base_Worker

# 重启 Flask 主程序
echo "正在重启 Flask 主程序 (Gunicorn)..."
# 强行释放 5000 端口（防止残留进程）
fuser -k 5000/tcp > /dev/null 2>&1
/usr/bin/supervisorctl restart HuanHe_Base_Main

echo "================================================"
echo "✅ Base 版部署完成！"
echo "💡 提示：所有标准账号已重置密码 (yun123456.) 并强制解绑设备。"
echo "================================================"
