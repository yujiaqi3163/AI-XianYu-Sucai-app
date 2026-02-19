from flask import Blueprint, render_template  # 导入Flask相关模块
from app.models import User, RegisterSecret  # 导入数据模型

bp = Blueprint('main', __name__)  # 创建主路由蓝图


@bp.route('/')
def index():
    users = User.query.all()  # 查询所有用户
    register_secrets = RegisterSecret.query.all()  # 查询所有注册卡密
    return render_template('index.html', users=users, register_secrets=register_secrets)  # 渲染首页模板
