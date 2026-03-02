# ============================================================
# run.py
# 
# Flask 应用启动入口
# 功能说明：
# 1. 创建 Flask 应用实例
# 2. 启动开发服务器
# ============================================================

# 导入创建应用的函数
from app import create_app
import socket

# 创建 Flask 应用实例
app = create_app()

def get_local_ip():
    try:
        # 创建一个UDP socket连接到外部地址（不会真的发送数据）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 如果直接运行此文件
if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    
    print('=' * 60)
    print(f'  应用正在启动...')
    print(f'  本地访问: http://127.0.0.1:{port}')
    print(f'  局域网访问 (手机/其他设备): http://{local_ip}:{port}')
    print('=' * 60)
    
    # 启动服务器：监听所有IP、端口5000、开启调试模式
    app.run(host='0.0.0.0', port=port, debug=True)
