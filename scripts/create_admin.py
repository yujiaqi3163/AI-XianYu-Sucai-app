# ============================================================
# create_admin.py
# 
# 批量创建/更新账号脚本
# 功能说明：
# 1. 创建 PE/PC 端各3个账号（超级管理员、管理员、普通用户）
# 2. 不会影响或清除现有数据库数据
# 3. 检查账号是否已存在，避免重复创建
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量创建账号脚本
包含 PC/PE 端的 Super/Admin/User 角色
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

def create_users():
    """创建指定账号（不清除任何数据）"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('开始初始化 6 个标准账号')
        print('=' * 60)
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
                
        print()
        print('=' * 60)
        print(f'完成！新建: {created_count}, 更新: {updated_count}, 跳过: {skipped_count}')
        print('=' * 60)

if __name__ == '__main__':
    create_users()
