# ============================================================
# init_database.py
# 
# 数据库初始化脚本
# 功能说明：
# 1. 创建所有数据表
# 2. 初始化默认配置
# 3. 创建超级管理员（可选）
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化与迁移整合脚本
一键创建数据库并执行所有必要的迁移
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import (
    User, Config, MaterialType, Material, MaterialImage,
    RegisterSecret, TerminalSecret, UserMaterial, UserMaterialImage, Permission
)


def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('开始初始化数据库...')
        print('=' * 60)
        
        # 1. 创建所有表
        print('\n[步骤 1/8] 创建数据库表...')
        try:
            db.create_all()
            print('✅ 数据库表创建成功！')
        except Exception as e:
            print(f'❌ 创建表失败: {e}')
            return False
        
        # 2. 迁移用户表
        print('\n[步骤 2/8] 迁移用户表...')
        migrate_user_table()
        
        # 3. 迁移设备锁字段
        print('\n[步骤 3/8] 迁移设备锁字段...')
        migrate_device_lock()
        
        # 4. 迁移解绑申请字段
        print('\n[步骤 4/8] 迁移解绑申请字段...')
        migrate_unbind_request()
        
        # 5. 迁移卡密表
        print('\n[步骤 5/8] 迁移卡密表...')
        migrate_secrets_table()
        
        # 6. 迁移用户素材表
        print('\n[步骤 6/8] 迁移用户素材表...')
        migrate_user_material_tables()
        
        # 7. 初始化配置表
        print('\n[步骤 7/8] 初始化配置表...')
        init_config_table()
        
        # 8. 初始化权限表
        print('\n[步骤 8/8] 初始化权限表...')
        init_permissions_table()
        
        print('\n' + '=' * 60)
        print('🎉 数据库初始化完成！')
        print('=' * 60)
        
        return True


def migrate_user_table():
    """迁移用户表，添加avatar、bio、gender、birthday字段"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'avatar' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500)"))
                print('  ✅ 添加 avatar 列')
            
            if 'bio' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN bio VARCHAR(200)"))
                print('  ✅ 添加 bio 列')
            
            if 'gender' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
                print('  ✅ 添加 gender 列')
            
            if 'birthday' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN birthday DATE"))
                print('  ✅ 添加 birthday 列')
            
            conn.commit()
            print('  ✅ 用户表迁移完成')
    except Exception as e:
        print(f'  ℹ️ 用户表迁移跳过或已完成: {e}')


def migrate_device_lock():
    """迁移设备锁字段"""
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        with db.engine.connect() as conn:
            if 'bound_device_id' not in columns:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN bound_device_id VARCHAR(200)'))
                print('  ✅ 添加 bound_device_id 列')
            
            if 'session_token' not in columns:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN session_token VARCHAR(64)'))
                conn.execute(db.text('CREATE INDEX ix_users_session_token ON users (session_token)'))
                print('  ✅ 添加 session_token 列及索引')
                
            conn.commit()
            
        if 'bound_device_id' in columns and 'session_token' in columns:
            print('  ℹ️ 设备锁字段已存在')
    except Exception as e:
        print(f'  ℹ️ 设备锁迁移跳过: {e}')


def migrate_unbind_request():
    """迁移解绑申请字段"""
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        added = False
        
        if 'device_unbind_status' not in columns:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN device_unbind_status INTEGER DEFAULT 0'))
                conn.commit()
            print('  ✅ 添加 device_unbind_status 列')
            added = True
        
        if 'device_unbind_requested_at' not in columns:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN device_unbind_requested_at DATETIME'))
                conn.commit()
            print('  ✅ 添加 device_unbind_requested_at 列')
            added = True
        
        if not added:
            print('  ℹ️ 解绑申请字段已存在')
    except Exception as e:
        print(f'  ℹ️ 解绑申请迁移跳过: {e}')


def migrate_secrets_table():
    """迁移卡密表"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(register_secrets)"))
            columns = [row[1] for row in result]
            
            if 'duration_type' not in columns:
                conn.execute(db.text("ALTER TABLE register_secrets ADD COLUMN duration_type VARCHAR(20) DEFAULT 'permanent'"))
                print('  ✅ 添加 duration_type 列')
            
            if 'expires_at' not in columns:
                conn.execute(db.text("ALTER TABLE register_secrets ADD COLUMN expires_at DATETIME"))
                print('  ✅ 添加 expires_at 列')
            
            conn.execute(db.text("UPDATE register_secrets SET duration_type = 'permanent' WHERE duration_type IS NULL"))
            conn.commit()
            print('  ✅ 卡密表迁移完成')
    except Exception as e:
        print(f'  ℹ️ 卡密表迁移跳过: {e}')


def migrate_user_material_tables():
    """迁移用户素材表"""
    try:
        db.create_all()
        print('  ✅ 用户素材表已就绪')
    except Exception as e:
        print(f'  ℹ️ 用户素材表迁移跳过: {e}')


def init_config_table():
    """初始化配置表"""
    try:
        default_configs = [
            ('customer_service_wechat', 'your_kefu_wechat', '客服微信号')
        ]
        
        for key, value, description in default_configs:
            if not Config.query.filter_by(key=key).first():
                config = Config(key=key, value=value, description=description)
                db.session.add(config)
                print(f'  ✅ 添加默认配置: {key}')
        
        db.session.commit()
        print('  ✅ 配置表初始化完成')
    except Exception as e:
        print(f'  ℹ️ 配置表初始化跳过: {e}')


def init_permissions_table():
    """初始化权限表"""
    try:
        default_permissions = [
            ('material_manage', '素材管理', '管理素材库的素材'),
            ('secret_manage', '卡密管理', '管理注册卡密'),
            ('user_manage', '用户管理', '管理系统用户'),
            ('type_manage', '分类管理', '管理素材分类'),
            ('config_manage', '设置客服微信', '设置客服微信号')
        ]
        
        for code, name, description in default_permissions:
            if not Permission.query.filter_by(code=code).first():
                perm = Permission(code=code, name=name, description=description)
                db.session.add(perm)
                print(f'  ✅ 添加默认权限: {name}')
        
        db.session.commit()
        print('  ✅ 权限表初始化完成')
    except Exception as e:
        print(f'  ℹ️ 权限表初始化跳过: {e}')


def create_sample_data():
    """创建示例数据（可选）"""
    app = create_app()
    
    with app.app_context():
        print('\n' + '=' * 60)
        print('创建示例数据...')
        print('=' * 60)
        
        # 创建示例分类
        print('\n[1/4] 创建示例分类...')
        if not MaterialType.query.first():
            types = [
                MaterialType(name='副业', description='副业素材', sort_order=1)
            ]
            db.session.add_all(types)
            db.session.commit()
            print('  ✅ 示例分类创建成功')
        else:
            print('  ℹ️ 分类已存在，跳过')
        
        # 创建/初始化标准账号
        print('\n[2/4] 初始化 6 个标准账号...')
        
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
        reset_count = 0
        
        for user_info in users_to_create:
            user = User.query.filter_by(username=user_info['username']).first()
            if not user:
                # 检查邮箱是否已被使用
                if User.query.filter_by(email=user_info['email']).first():
                    print(f'  ⚠️ 邮箱 {user_info["email"]} 已被其他用户使用，跳过创建 {user_info["username"]}')
                    continue
                    
                user = User(
                    username=user_info['username'],
                    email=user_info['email'],
                    is_admin=user_info['is_admin'],
                    is_super_admin=user_info['is_super_admin']
                )
                user.password = user_info['password']
                db.session.add(user)
                print(f'  ✅ 创建 {user_info["role_name"]}: {user_info["username"]}')
                created_count += 1
            else:
                # 账号已存在，重置设备绑定和会话信息
                reset_needed = False
                if user.bound_device_id or user.session_token:
                    user.bound_device_id = None
                    user.session_token = None
                    user.device_unbind_status = 0
                    user.device_unbind_requested_at = None
                    reset_needed = True
                
                # 确保密码和权限正确（可选：强制重置密码和权限）
                # 这里只重置设备信息，保持密码不变以免影响用户修改后的密码
                
                if reset_needed:
                    print(f'  🔄 重置设备信息: {user_info["username"]}')
                    reset_count += 1
                else:
                    # print(f'  ℹ️ {user_info["role_name"]} 已存在且状态正常')
                    pass
        
        db.session.commit()
        
        if created_count > 0 or reset_count > 0:
            print(f'  ✅ 处理完成: 创建 {created_count} 个, 重置 {reset_count} 个')
        else:
            print('  ℹ️ 所有标准账号已存在且状态正常')
            
        print('\n  [账号清单]')
        print(f'  统一密码: {common_password}')
        print('  ----------------------------------------')
        print('  PE端:')
        print('    超级管理员: pe_yujiaqi_super')
        print('    管理员:     pe_yujiaqi_admin')
        print('    普通用户:   pe_yujiaqi_user')
        print('  ----------------------------------------')
        print('  PC端:')
        print('    超级管理员: pc_yujiaqi_super')
        print('    管理员:     pc_yujiaqi_admin')
        print('    普通用户:   pc_yujiaqi_user')
        
        # 创建测试卡密（空状态）
        print('\n[3/4] 保持卡密为空状态...')
        print('  ℹ️ 卡密表保持为空，需要手动添加')
        
        print('\n' + '=' * 60)
        print('🎉 示例数据创建完成！')
        print('=' * 60)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        success = init_database()
        if success:
            create_sample_data()
    elif len(sys.argv) > 1 and sys.argv[1] == '-y':
        init_database()
    else:
        print('使用方法:')
        print('  python scripts/init_database.py          # 仅初始化数据库')
        print('  python scripts/init_database.py --sample # 初始化数据库并创建示例数据\n')
        
        confirm = input('是否初始化数据库？(y/n): ')
        if confirm.lower() == 'y':
            init_database()
