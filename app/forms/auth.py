# 导入 Flask-WTF 表单基类
from flask_wtf import FlaskForm
# 导入表单字段类型
from wtforms import StringField, PasswordField, BooleanField, SubmitField
# 导入表单验证器
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
# 导入数据模型
from app.models import User, RegisterSecret


# 登录表单类
class LoginForm(FlaskForm):
    # 用户名/邮箱字段：必填，最大120字符
    username_or_email = StringField('用户名/邮箱', validators=[DataRequired(), Length(max=120)])
    # 密码字段：必填
    password = PasswordField('密码', validators=[DataRequired()])
    # 记住我复选框
    remember = BooleanField('记住我')
    # 登录按钮
    submit = SubmitField('登录')


# 注册表单类
class RegisterForm(FlaskForm):
    # 用户名字段：必填，3-80字符
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=80)])
    # 邮箱字段：必填，邮箱格式验证，最大120字符
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    # 密码字段：必填，最小6字符
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    # 确认密码字段：必填，必须与密码一致
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message='两次密码输入不一致')])
    # 注册密钥字段：必填，最大100字符
    secret = StringField('注册密钥', validators=[DataRequired(), Length(max=100)])
    # 注册按钮
    submit = SubmitField('注册')

    # 自定义用户名验证：检查用户名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')

    # 自定义邮箱验证：检查邮箱是否已注册
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')

    # 自定义卡密验证：检查卡密是否有效且未使用
    def validate_secret(self, secret):
        register_secret = RegisterSecret.query.filter_by(secret=secret.data).first()
        if not register_secret:
            raise ValidationError('注册密钥无效，请检查后重试')
        if register_secret.is_used:
            raise ValidationError('该注册密钥已被使用')
