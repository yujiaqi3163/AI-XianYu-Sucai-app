# ============================================================
# create_admin_bt.py
# 
# 宝塔服务器专用 - 批量创建/更新账号脚本
# 功能说明：
# 1. 自动检测项目路径
# 2. 更好的错误处理
# 3. 详细的日志输出
# 4. 创建 PE/PC 端各3个账号（超级管理员、管理员、普通用户）
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宝塔服务器专用 - 批量创建账号脚本
包含 PC/PE 端的 Super/Admin/User 角色
"""

import sys
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（脚本所在目录的上一级）
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

print('=' * 80)
print('宝塔服务器 - 批量创建账号')
print('=' * 80)
print()
print(f'脚本目录: {SCRIPT_DIR}')
print(f'项目根目录: {PROJECT_ROOT}')
print()

# 添加项目根目录到Python路径
sys.path.insert(0, PROJECT_ROOT)

# 检查是否存在 .env 文件
env_path = os.path.join(PROJECT_ROOT, '.env')
if not os.path.exists(env_path):
    print('⚠️  警告: .env 文件不存在，请检查！')
    print(f'期望路径: {env_path}')
    print()

# 检查是否存在 app 目录
app_path = os.path.join(PROJECT_ROOT, 'app')
if not os.path.exists(app_path):
    print('❌ 错误: app 目录不存在！')
    print(f'期望路径: {app_path}')
    print()
    print('请确保在正确的项目目录下运行此脚本！')
    sys.exit(1)

try:
    from app import create_app, db
    from app.models import User
except ImportError as e:
    print(f'❌ 导入模块失败: {e}')
    print()
    print('请确保：')
    print('1. 已激活虚拟环境')
    print('2. 已安装所有依赖 (pip install -r requirements.txt)')
    print('3. 在正确的项目目录下运行')
    sys.exit(1)


def create_users():
    """创建指定账号"""
    print('正在初始化应用...')
    
    try:
        app = create_app()
    except Exception as e:
        print(f'❌ 创建应用失败: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    with app.app_context():
        print('应用初始化成功！')
        print()
        print('=' * 80)
        print('开始初始化 6 个标准账号')
        print('=' * 80)
        print()
        
        # 统一密码
        common_password = 'yun123456.'
        
        # 定义要创建的用户列表
        # 格式: (username, email, is_super_admin, is_admin)
        users_to_create = [
            # PE 端账号
            {
                'username': 'pe_yujiaqi_super',
                'email': 'pe_super@example.com',
                'password': common_password,
                'is_super_admin': True,
                'is_admin': True,
                'role_name': 'PE 超级管理员'
            },
            {
                'username': 'pe_yujiaqi_admin',
                'email': 'pe_admin@example.com',
                'password': common_password,
                'is_super_admin': False,
                'is_admin': True,
                'role_name': 'PE 管理员'
            },
            {
                'username': 'pe_yujiaqi_user',
                'email': 'pe_user@example.com',
                'password': common_password,
                'is_super_admin': False,
                'is_admin': False,
                'role_name': 'PE 普通用户'
            },
            
            # PC 端账号
            {
                'username': 'pc_yujiaqi_super',
                'email': 'pc_super@example.com',
                'password': common_password,
                'is_super_admin': True,
                'is_admin': True,
                'role_name': 'PC 超级管理员'
            },
            {
                'username': 'pc_yujiaqi_admin',
                'email': 'pc_admin@example.com',
                'password': common_password,
                'is_super_admin': False,
                'is_admin': True,
                'role_name': 'PC 管理员'
            },
            {
                'username': 'pc_yujiaqi_user',
                'email': 'pc_user@example.com',
                'password': common_password,
                'is_super_admin': False,
                'is_admin': False,
                'role_name': 'PC 普通用户'
            }
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for user_info in users_to_create:
            username = user_info['username']
            email = user_info['email']
            password = user_info['password']
            is_super = user_info['is_super_admin']
            is_admin = user_info['is_admin']
            role_name = user_info['role_name']
            
            print(f'正在处理: {role_name} ({username}) ...')
            
            # 检查用户名是否已存在
            try:
                user = User.query.filter_by(username=username).first()
                
                if user:
                    print(f'  ℹ️ 账号 "{username}" 已存在，正在更新权限和密码...')
                    
                    # 更新用户信息
                    user.is_super_admin = is_super
                    user.is_admin = is_admin
                    user.password = password
                    
                    # 如果邮箱不同，尝试更新邮箱
                    if user.email != email:
                        # 检查新邮箱是否被其他用户占用
                        existing_by_email = User.query.filter_by(email=email).first()
                        if existing_by_email and existing_by_email.id != user.id:
                            print(f'  ⚠️  邮箱 "{email}" 已被用户 "{existing_by_email.username}" 占用，跳过更新邮箱')
                        else:
                            old_email = user.email
                            user.email = email
                            print(f'  ✅ 更新邮箱: {old_email} → {email}')
                    
                    db.session.commit()
                    print(f'  ✅ 更新成功')
                    updated_count += 1
                else:
                    # 用户名不存在，检查邮箱是否已被占用
                    existing_by_email = User.query.filter_by(email=email).first()
                    
                    if existing_by_email:
                        print(f'  ⚠️  邮箱 "{email}" 已被用户 "{existing_by_email.username}" 占用，跳过创建账号 "{username}"')
                        skipped_count += 1
                        continue
                    
                    # 创建新账号
                    new_user = User(
                        username=username,
                        email=email,
                        is_admin=is_admin,
                        is_super_admin=is_super
                    )
                    new_user.password = password
                    
                    db.session.add(new_user)
                    db.session.commit()
                    print(f'  ✅ 创建成功')
                    created_count += 1
                    
            except Exception as e:
                print(f'  ❌ 处理账号 "{username}" 时出错: {e}')
                db.session.rollback()
                continue
                
        print()
        print('=' * 80)
        print(f'完成！新建: {created_count}, 更新: {updated_count}, 跳过: {skipped_count}')
        print('=' * 80)
        
if __name__ == '__main__':
    create_users()
