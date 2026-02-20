# 导入管理后台路由蓝图
from app.routes.admin.routes import bp as admin_bp

# 导出蓝图，方便其他模块使用
__all__ = ['admin_bp']
