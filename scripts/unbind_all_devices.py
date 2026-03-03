# ============================================================
# unbind_all_devices.py
# 
# 全局设备解绑脚本
# 功能说明：
# 1. 扫描数据库中所有用户账号
# 2. 强制清除所有用户的 bound_device_id (设备锁)
# 3. 强制清除所有用户的 session_token (强制下线)
# 4. 重置解绑申请状态
# 5. 不会修改密码、权限或其他任何信息
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

def unbind_all_users():
    """强制解绑所有用户的设备"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('🚨 正在执行全局设备解绑...')
        print('=' * 60)
        
        try:
            # 1. 查询所有已绑定设备或有活跃会话的用户
            # 条件：bound_device_id 不为空 或 session_token 不为空
            users = User.query.filter(
                (User.bound_device_id != None) | 
                (User.session_token != None)
            ).all()
            
            count = 0
            
            if not users:
                print('✅ 当前没有绑定设备或在线的用户，无需操作。')
                return

            print(f'🔍 发现 {len(users)} 个需要解绑的用户，开始处理...\n')

            for user in users:
                old_device = user.bound_device_id or '无'
                
                # 执行解绑与下线
                user.bound_device_id = None
                user.session_token = None
                
                # 重置申请状态
                user.device_unbind_status = 0
                user.device_unbind_requested_at = None
                
                print(f'  🔓 用户: {user.username:<20} | 原设备: {old_device[:20]}...')
                count += 1
            
            # 提交事务
            db.session.commit()
            
            print('\n' + '=' * 60)
            print(f'🎉 操作成功！已强制解绑 {count} 个账号')
            print('🛡️ 所有用户的设备锁和会话Token已清空，下次登录将自动绑定新设备')
            print('=' * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f'\n❌ 操作失败: {str(e)}')
            sys.exit(1)

if __name__ == '__main__':
    # 增加确认步骤，防止误操作
    if len(sys.argv) > 1 and sys.argv[1] == '-y':
        unbind_all_users()
    else:
        print('⚠️  警告: 此操作将强制解绑数据库中【所有用户】的设备！')
        confirm = input('确认继续吗？(输入 y 确认): ')
        if confirm.lower() == 'y':
            unbind_all_users()
        else:
            print('已取消操作')
