import secrets
import string
from datetime import datetime
from app import create_app, db
from app.models import RegisterSecret

def generate_random_secret(prefix="2026", category="USER"):
    """
    生成格式化的卡密：YEAR-CATEGORY-RANDOM_HEX
    例如: 2026-USER-7F2A3B
    """
    # 生成6位随机的十六进制字符串
    random_part = secrets.token_hex(3).upper()
    return f"{prefix}-{category}-{random_part}"

def add_bulk_secrets(count=5):
    app = create_app()
    
    with app.app_context():
        print(f"正在准备生成 {count} 条随机卡密...")
        
        new_secrets = []
        for _ in range(count):
            secret_code = generate_random_secret()
            
            # 简单查重：确保生成的卡密在数据库中不存在
            if not RegisterSecret.query.filter_by(secret=secret_code).first():
                new_secret_obj = RegisterSecret(
                    secret=secret_code,
                    is_used=False  # 默认为未使用
                )
                db.session.add(new_secret_obj)
                new_secrets.append(secret_code)
        
        try:
            db.session.commit()
            print("--- 写入成功 ---")
            for s in new_secrets:
                print(f"成功添加卡密: {s}")
        except Exception as e:
            db.session.rollback()
            print(f"发生错误，已回滚: {e}")

if __name__ == '__main__':
    add_bulk_secrets(5)