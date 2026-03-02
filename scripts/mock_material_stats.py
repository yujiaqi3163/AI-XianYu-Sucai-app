# ============================================================
# mock_material_stats.py
# 
# 模拟素材统计数据脚本
# 功能说明：
# 1. 随机生成所有素材的统计数据
# 2. 浏览量：0 - 10000 随机
# 3. 下载量：浏览量的 0% - 30% 随机
# 4. 收藏量：浏览量的 0% - 30% 随机
# ============================================================

import sys
import os
import random
from tqdm import tqdm  # 导入进度条库

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Material

def mock_stats():
    """模拟生成素材统计数据"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('开始生成模拟统计数据...')
        print('=' * 60)
        print()
        
        # 获取所有素材
        materials = Material.query.all()
        total_materials = len(materials)
        
        if total_materials == 0:
            print('❌ 数据库中没有素材，无需处理。')
            return

        print(f'共发现 {total_materials} 个素材，正在处理...')
        print('-' * 60)
        
        updated_count = 0
        
        # 使用 tqdm 显示进度条
        for material in tqdm(materials, desc="处理进度", unit="个"):
            # 1. 生成浏览量 (0 - 10000)
            view_count = random.randint(0, 10000)
            
            # 2. 生成下载量 (浏览量的 0% - 30%)
            # 确保下载量不超过浏览量
            download_ratio = random.uniform(0, 0.3)
            download_count = int(view_count * download_ratio)
            
            # 3. 生成收藏量 (浏览量的 0% - 30%)
            # 确保收藏量不超过浏览量
            favorite_ratio = random.uniform(0, 0.3)
            favorite_count = int(view_count * favorite_ratio)
            
            # 更新数据
            material.view_count = view_count
            material.download_count = download_count
            material.favorite_count = favorite_count
            
            updated_count += 1
            
            # 每处理 100 个提交一次，避免事务过大
            if updated_count % 100 == 0:
                db.session.commit()
        
        # 提交剩余的数据
        db.session.commit()
        
        print()
        print('=' * 60)
        print(f'🎉 处理完成！共更新 {updated_count} 个素材的数据。')
        print('=' * 60)
        print('数据生成规则:')
        print('  - 浏览量: 0 - 10000 随机')
        print('  - 下载量: 浏览量的 0% - 30%')
        print('  - 收藏量: 浏览量的 0% - 30%')
        print('=' * 60)

if __name__ == '__main__':
    # 检查是否安装了 tqdm，如果没有则简单提示
    try:
        import tqdm
    except ImportError:
        print('提示: 安装 tqdm 库可以看到进度条 (pip install tqdm)')
        # 定义一个简单的替代类，使得代码在没有 tqdm 时也能运行
        class tqdm:
            def __init__(self, iterable, **kwargs):
                self.iterable = iterable
            def __iter__(self):
                return iter(self.iterable)
    
    mock_stats()
