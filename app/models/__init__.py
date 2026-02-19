# 导入用户模型
from app.models.user import User
# 导入注册卡密模型
from app.models.register_secret import RegisterSecret

# 导出模型，方便其他模块使用
__all__ = ['User', 'RegisterSecret']
