from app.routes.main import main_bp  # 导入主路由蓝图
from app.routes.admin import admin_bp  # 导入管理后台路由蓝图

__all__ = ['main_bp', 'admin_bp']  # 定义模块导出内容
