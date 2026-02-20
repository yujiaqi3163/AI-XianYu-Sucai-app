# 导入Flask相关模块
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, jsonify
# 导入登录相关模块
from flask_login import login_required, current_user
# 导入数据库模块
from app import db
# 导入表单
from app.forms import MaterialForm
from app.forms.material_type import MaterialTypeForm
# 导入模型
from app.models import Material, MaterialType, MaterialImage
# 导入文件处理模块
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# 创建管理后台路由蓝图
bp = Blueprint('admin', __name__, url_prefix='/admin')


def save_image(file):
    """保存图片到本地并返回相对路径"""
    if not file:
        return None
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    # 添加时间戳避免重名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    # 构建保存路径
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # 保存文件
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # 返回相对路径（用于数据库存储）
    return f'/static/uploads/{filename}'


@bp.route('/')
@login_required
def index():
    material_types = MaterialType.query.order_by(MaterialType.created_at.desc()).all()
    return render_template('admin/admin_index.html', material_types=material_types)


@bp.route('/materials')
@login_required
def materials():
    material_types = MaterialType.query.order_by(MaterialType.created_at.desc()).all()
    return render_template('admin/admin_materials.html', material_types=material_types)


@bp.route('/materials/add', methods=['GET', 'POST'])
@login_required
def material_add():
    # 创建表单实例
    form = MaterialForm()
    
    # 填充素材类型选择框
    material_types = MaterialType.query.all()
    form.material_type_id.choices = [(t.id, t.name) for t in material_types]
    
    # 如果是POST请求
    if form.validate_on_submit():
        # 获取封面图
        cover_image = None
        if 'cover_image' in request.files:
            cover_file = request.files['cover_image']
            if cover_file and cover_file.filename:
                cover_image = save_image(cover_file)
        
        # 获取其他图片
        other_images = []
        if 'other_images' in request.files:
            other_files = request.files.getlist('other_images')
            for file in other_files:
                if file and file.filename:
                    saved_path = save_image(file)
                    if saved_path:
                        other_images.append(saved_path)
        
        # 检查封面图是否上传（必填）
        if not cover_image:
            flash('请上传封面图！', 'error')
            return render_template('admin/admin_material_add.html', form=form)
        
        # 创建新素材
        material = Material(
            title=form.title.data,
            description=form.description.data,
            material_type_id=form.material_type_id.data,
            is_published=form.is_published.data
        )
        
        # 保存素材到数据库
        db.session.add(material)
        db.session.flush()  # 获取素材ID
        
        # 保存封面图
        if cover_image:
            cover_img = MaterialImage(
                material_id=material.id,
                image_url=cover_image,
                is_cover=True,
                sort_order=0
            )
            db.session.add(cover_img)
        
        # 保存其他图片
        for idx, img_url in enumerate(other_images):
            other_img = MaterialImage(
                material_id=material.id,
                image_url=img_url,
                is_cover=False,
                sort_order=idx + 1
            )
            db.session.add(other_img)
        
        # 提交到数据库
        db.session.commit()
        
        # 提示成功
        flash('素材添加成功！', 'success')
        
        # 跳转到素材列表
        return redirect(url_for('admin.materials'))
    
    # GET请求或验证失败，渲染表单
    return render_template('admin/admin_material_add.html', form=form)


@bp.route('/secrets')
@login_required
def secrets():
    return render_template('admin/admin_secrets.html')


@bp.route('/users')
@login_required
def users():
    return render_template('admin/admin_users.html')


@bp.route('/material-types')
@login_required
def material_types():
    """分类管理页面"""
    material_types = MaterialType.query.order_by(MaterialType.created_at.desc()).all()
    return render_template('admin/admin_material_types.html', material_types=material_types)


@bp.route('/api/material-types', methods=['POST'])
@login_required
def api_add_material_type():
    """添加分类API"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    # 检查分类名称是否已存在
    existing = MaterialType.query.filter_by(name=name).first()
    if existing:
        return jsonify({'success': False, 'message': '分类名称已存在'}), 400
    
    material_type = MaterialType(
        name=name,
        description=data.get('description', '').strip()
    )
    db.session.add(material_type)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '分类添加成功',
        'data': {
            'id': material_type.id,
            'name': material_type.name,
            'description': material_type.description
        }
    })


@bp.route('/api/material-types/<int:type_id>', methods=['GET'])
@login_required
def api_get_material_type(type_id):
    """获取单个分类API"""
    material_type = MaterialType.query.get_or_404(type_id)
    return jsonify({
        'success': True,
        'data': {
            'id': material_type.id,
            'name': material_type.name,
            'description': material_type.description
        }
    })


@bp.route('/api/material-types/<int:type_id>', methods=['PUT'])
@login_required
def api_update_material_type(type_id):
    """更新分类API"""
    material_type = MaterialType.query.get_or_404(type_id)
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    # 检查分类名称是否已存在（排除当前分类）
    existing = MaterialType.query.filter(MaterialType.name == name, MaterialType.id != type_id).first()
    if existing:
        return jsonify({'success': False, 'message': '分类名称已存在'}), 400
    
    material_type.name = name
    material_type.description = data.get('description', '').strip()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '分类更新成功',
        'data': {
            'id': material_type.id,
            'name': material_type.name,
            'description': material_type.description
        }
    })


@bp.route('/api/material-types/<int:type_id>', methods=['DELETE'])
@login_required
def api_delete_material_type(type_id):
    """删除分类API"""
    material_type = MaterialType.query.get_or_404(type_id)
    
    # 将关联素材的分类ID设为NULL
    for material in material_type.materials:
        material.material_type_id = None
    
    db.session.delete(material_type)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '分类删除成功'
    })
