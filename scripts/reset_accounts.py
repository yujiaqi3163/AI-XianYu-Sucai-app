# ============================================================
# reset_accounts.py
# 
# 账号重置与设备解绑脚本
# 功能说明：
# 1. 批量创建或重置 6 个标准测试账号
# 2. 强制重置密码为 yun123456.
# 3. 强制解绑所有设备信息（Bound Device ID & Session Token）
# 4. 独立运行，不依赖 init_database.py
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

def reset_standard_accounts():
    """重置标准账号并解绑设备"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('开始重置标准账号与解绑设备...')
        print('=' * 60)
        
        # 统一密码
        common_password = 'yun123456.'
        
        # 定义要操作的用户列表
        users_to_process = [
            # 超级管理员 (PC)
            {
                'username': 'pc_yujiaqi_super',
                'role_name': 'PC 超级管理员',
                'email': 'pc_yujiaqi_super@qq.com',
                'is_super_admin': True,
                'is_admin': True,
                'password': common_password
            },
            # 超级管理员 (PE)
            {
                'username': 'pe_yujiaqi_super',
                'role_name': 'PE 超级管理员',
                'email': 'pe_yujiaqi_super@qq.com',
                'is_super_admin': True,
                'is_admin': True,
                'password': common_password
            },
            # 管理员 (PC)
            {
                'username': 'pc_yujiaqi_admin',
                'role_name': 'PC 管理员',
                'email': 'pc_yujiaqi_admin@qq.com',
                'is_super_admin': False,
                'is_admin': True,
                'password': common_password
            },
            # 管理员 (PE)
            {
                'username': 'pe_yujiaqi_admin',
                'role_name': 'PE 管理员',
                'email': 'pe_yujiaqi_admin@qq.com',
                'is_super_admin': False,
                'is_admin': True,
                'password': common_password
            },
            # 普通用户 (PC)
            {
                'username': 'pc_yujiaqi_user',
                'role_name': 'PC 普通用户',
                'email': 'pc_yujiaqi_user@qq.com',
                'is_super_admin': False,
                'is_admin': False,
                'password': common_password
            },
            # 普通用户 (PE)
            {
                'username': 'pe_yujiaqi_user',
                'role_name': 'PE 普通用户',
                'email': 'pe_yujiaqi_user@qq.com',
                'is_super_admin': False,
                'is_admin': False,
                'password': common_password
            }
        ]
        
        created_count = 0
        reset_count = 0
        
        for user_info in users_to_process:
            user = User.query.filter_by(username=user_info['username']).first()
            
            if not user:
                # 检查邮箱占用
                if User.query.filter_by(email=user_info['email']).first():
                    print(f'  ⚠️ 邮箱 {user_info["email"]} 被占用，跳过创建 {user_info["username"]}')
                    continue
                
                # 创建新用户
                user = User(
                    username=user_info['username'],
                    email=user_info['email'],
                    is_admin=user_info['is_admin'],
                    is_super_admin=user_info['is_super_admin']
                )
                user.password = user_info['password']
                # 确保新创建的用户也是未绑定状态
                user.bound_device_id = None
                user.session_token = None
                
                db.session.add(user)
                print(f'  ✅ 创建账号: {user_info["username"]} ({user_info["role_name"]})')
                created_count += 1
            else:
                # 账号已存在，执行强制重置
                print(f'  🔄 重置账号: {user_info["username"]}')
                
                # 1. 重置密码
                user.password = user_info['password']
                
                # 2. 修正权限
                user.is_admin = user_info['is_admin']
                user.is_super_admin = user_info['is_super_admin']
                user.email = user_info['email']  # 确保邮箱正确
                
                # 3. 【核心】强制解绑设备和清空会话
                user.bound_device_id = None
                user.session_token = None
                user.device_unbind_status = 0
                user.device_unbind_requested_at = None
                
                reset_count += 1
        
        db.session.commit()
        
        print('\n' + '=' * 60)
        print(f'🎉 处理完成！新建: {created_count}, 重置: {reset_count}')
        print(f'🔑 统一密码: {common_password}')
        print('🛡️ 所有标准账号的设备绑定已强制解除')
        print('=' * 60)

if __name__ == '__main__':
    reset_standard_accounts()
