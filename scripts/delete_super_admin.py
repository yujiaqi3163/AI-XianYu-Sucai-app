# ============================================================
# delete_super_admin.py
# 
# 删除超级管理员账号脚本
# 功能说明：
# 1. 列出当前所有超级管理员
# 2. 交互式选择要删除的账号
# 3. 双重确认防止误删
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

def delete_super_admin():
    """删除超级管理员账号"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('删除超级管理员账号工具')
        print('=' * 60)
        print()
        
        # 查询所有超级管理员
        super_admins = User.query.filter_by(is_super_admin=True).all()
        
        if not super_admins:
            print('当前没有任何超级管理员账号。')
            return

        print(f'发现 {len(super_admins)} 个超级管理员账号:')
        print('-' * 60)
        print(f'{"ID":<5} | {"用户名":<20} | {"邮箱":<30}')
        print('-' * 60)
        
        for admin in super_admins:
            print(f'{admin.id:<5} | {admin.username:<20} | {admin.email:<30}')
        print('-' * 60)
        print()
        
        # 获取用户输入
        print('请输入要删除的【用户名】(输入 q 退出):')
        target_username = input('> ').strip()
        
        if target_username.lower() == 'q' or not target_username:
            print('已取消操作。')
            return
            
        # 查找要删除的用户
        target_user = User.query.filter_by(username=target_username, is_super_admin=True).first()
        
        if not target_user:
            print(f'❌ 错误: 未找到用户名为 "{target_username}" 的超级管理员。')
            return
            
        # 确认删除
        print()
        print('⚠️  警告: 即将删除以下账号:')
        print(f'  ID: {target_user.id}')
        print(f'  用户名: {target_user.username}')
        print(f'  邮箱: {target_user.email}')
        print()
        print('此操作不可恢复！请输入 "DELETE" 确认删除:')
        
        confirm = input('> ').strip()
        
        if confirm == 'DELETE':
            try:
                db.session.delete(target_user)
                db.session.commit()
                print()
                print(f'✅ 成功删除超级管理员: {target_username}')
            except Exception as e:
                db.session.rollback()
                print()
                print(f'❌ 删除失败: {str(e)}')
        else:
            print()
            print('❌ 确认码错误，已取消删除操作。')

if __name__ == '__main__':
    delete_super_admin()
