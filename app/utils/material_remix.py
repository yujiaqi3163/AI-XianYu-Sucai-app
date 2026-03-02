# ============================================================
# material_remix.py
# 
# 素材二创工具模块
# 功能说明：
# 1. optimize_copywriting: 调用DeepSeek API优化文案
# 2. get_unique_css_recipes: 获取不重复的CSS样式配方
# ============================================================

# DeepSeek文案优化接口
import os
import openai
import random
import string
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def sanitize_copy(text):
    """清洗文案中的代码式表情等噪声"""
    if not text:
        return text
    
    # 移除形如 [哈哈] / [火] / [doge] / [OK] 等“代码式表情包”
    text = re.sub(r'\[(?:[A-Za-z0-9_\u4e00-\u9fff]{1,8})\]', '', text)
    
    # 移除形如 :smile: :ok_hand: 等冒号包裹的表情关键词
    text = re.sub(r':[A-Za-z0-9_+\-]{1,30}:', '', text, flags=re.IGNORECASE)
    
    # 规范多余空白与标点前空格
    text = re.sub(r'\s+([，。；；、,.!！?？])', r'\1', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    
    return text.strip()


def optimize_copywriting(original_text):
    """优化文案 - 使用DeepSeek API"""
    
    if not original_text or not original_text.strip():
        return original_text
    
    # 获取API密钥和基础URL
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    api_base = os.environ.get("DEEPSEEK_API_BASE") or "https://api.deepseek.com"
    
    if not api_key:
        logger.warning("未配置DeepSeek API Key，返回原文案")
        return original_text
    
    # 设置API
    openai.api_key = api_key
    openai.api_base = api_base
    
    system_prompt = """Role
你是一位因为工作变动或电脑内存不足，正忙着清理“陈年旧物”的普通用户。你曾深度参与过互联网各种小活计，现在手里攒了一堆当时记录的“经验碎纸片”，你觉得丢了可惜，想随便换个奶茶钱。
Task
将【原文案】中关于“兼职、赚钱项目、电子教程”的核心信息，包装成“以前折腾过的旧笔记”或“舍不得删的压箱底存货”。
Strategy: The Invisible Digital Trade (隐形交易策略)
业务降维（Crucial）：
将“兼职/副业”重构为：“以前下班后捣鼓的小摊子”、“以前整点碎银子的路子”、“那点换馒头钱的活儿”。
将“教程/资料/信息”重构为：“当时记的一坨乱七八糟的记录”、“硬盘里舍不得删的存货”、“以前整理的随笔”、“那堆压箱底的玩意儿”。
情绪植入：开头必须体现一种“清理的烦躁”。如：电脑卡爆了、换了新电脑不想倒腾数据了、被这些旧文件夹整崩溃了。
价值模糊化：不要列大纲。要说“当时为了这些整宿不睡”、“走过不少弯路才总结出来的”、“其实挺亲切的，就是现在没精力弄了”。
去商业化语式：禁止使用“原价/现价/福利/包教包会”。改为“随便拿走吧”、“换个奶茶钱”、“随缘出”。
Constraints
纯净文本：绝对禁止 Emoji。仅使用逗号，禁止句号及其他符号。
禁语库（死命令）：严禁出现：兼职、副业、赚钱、项目、教程、文档、视频、领取、加我、赚钱、精准、引流。
字数控制：130-160 字。
Workflow
背景设定：电脑清理或断舍离。
内容封装：将你的兼职/资料信息塞进“旧笔记”的描述中。
成品自检：读起来必须像是一个“在发牢骚、想清理硬盘空间”的普通人。"""

    try:
        # 使用旧版API调用方式
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"请对这段文案进行二创，确保合规且吸引人：\n\n{original_text}"
                }
            ],
            temperature=0.8,  # 略微提高温度，增加二创的随机性和原创度
            top_p=0.9,
            max_tokens=1000,
            stream=False,
            timeout=30  # 添加30秒超时，防止API响应慢导致请求堆积
        )

        # 提取回复内容
        if response and 'choices' in response and len(response['choices']) > 0:
            generated = response.choices[0].message.content.strip()
            return sanitize_copy(generated)
        else:
            logger.warning("API返回格式异常，返回原文案")
            return sanitize_copy(original_text)

    except Exception as e:
        logger.error(f"DeepSeek API调用失败: {str(e)}", exc_info=True)
        # 返回原文案作为备用
        return sanitize_copy(original_text)


# CSS混合配方库
CSS_RECIPES = [
    {
        "gradient": "linear-gradient(45deg, #ff9a9e, #fad0c4)",
        "blend_mode": "multiply",
        "contrast": 1.15,
        "brightness": 1.0,
        "saturation": 1.2,
        "opacity": 0.25
    },
    {
        "gradient": "linear-gradient(120deg, #a1c4fd, #c2e9fb)",
        "blend_mode": "overlay",
        "contrast": 1.1,
        "brightness": 1.05,
        "saturation": 1.15,
        "opacity": 0.3
    },
    {
        "gradient": "linear-gradient(to right, #43e97b, #38f9d7)",
        "blend_mode": "soft-light",
        "contrast": 1.2,
        "brightness": 0.95,
        "saturation": 1.3,
        "opacity": 0.2
    },
    {
        "gradient": "linear-gradient(135deg, #667eea, #764ba2)",
        "blend_mode": "screen",
        "contrast": 1.12,
        "brightness": 1.02,
        "saturation": 1.25,
        "opacity": 0.28
    },
    {
        "gradient": "linear-gradient(45deg, #fa709a, #fee140)",
        "blend_mode": "color-dodge",
        "contrast": 1.08,
        "brightness": 1.1,
        "saturation": 1.2,
        "opacity": 0.22
    }
]


def get_random_css_recipe(exclude_recipes=None):
    """获取随机CSS混合配方，可排除已使用的配方"""
    if exclude_recipes is None:
        exclude_recipes = []
    
    available_recipes = [r for r in CSS_RECIPES if r not in exclude_recipes]
    
    if not available_recipes:
        available_recipes = CSS_RECIPES
    
    return random.choice(available_recipes)


def get_unique_css_recipes(count):
    """获取指定数量的不重复CSS配方"""
    selected_recipes = []
    
    for i in range(count):
        recipe = get_random_css_recipe(selected_recipes)
        selected_recipes.append(recipe)
    
    return selected_recipes


def generate_remix_html(image_url, recipe):
    """生成图片二创的HTML（用于前端渲染）"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: transparent;
        }}
        .container {{
            position: relative;
            width: 100%;
            max-width: 1024px;
            line-height: 0;
        }}
        img {{
            width: 100%;
            height: auto;
            filter: contrast({recipe['contrast']}) brightness({recipe['brightness']}) saturate({recipe['saturation']});
        }}
        .overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            mix-blend-mode: {recipe['blend_mode']};
            background: {recipe['gradient']};
            opacity: {recipe['opacity']};
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{image_url}" crossorigin="anonymous">
        <div class="overlay"></div>
    </div>
</body>
</html>
"""
    return html
