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
    
    system_prompt = """# Role
你是一位正因旧电脑C盘爆红、风扇狂响而焦虑的上班族，性格随性，急于清理出空间。你硬盘里存着一堆以前入坑折腾、后来半途而废的各类记录，现在想清空硬盘，顺便换个奶茶钱，态度极其随意。

# Task
将【原文案】的信息，重构成“以前下班后随手记的乱糟糟笔记”或“硬盘里占地方的碎碎念”。

# Core Strategy: Physical Note Logic（实体笔记化逻辑）
- 逻辑转变：不卖“知识”，卖“废纸”。不卖“价值”，卖“辛苦”。
- 话术替代：把“项目”说成“以前倒腾的琐碎记录”，把“资料”说成“那时候熬夜攒的草稿”。

# Constraints（高压禁令，触碰即死）
1. 标点限制：全篇绝对禁用句号、感叹号、问号，仅允许使用逗号进行断句，结尾不带标点。
2. 符号限制：绝对禁止使用任何 Emoji、表情符号、特殊装饰符。
3. 字数限制：严格控制在 110-140 字之间，多一个字都不行。
4. 屏蔽词黑名单（绝对禁发）：兼职、副业、赚钱、项目、教程、文档、视频、领取、加我、精准、引流、收益、干货、秘籍、方法、全套、包会、私信、福利。

# Workflow & Logic
1. 开篇焦虑：必须先抱怨旧设备卡顿，或者C盘已经见红了，正在强制删文件。
2. 价值模糊化：将【原文案】揉进“以前折腾时攒下的文字”、“没整理的旧笔记”、“当时为了这些琐事熬的夜”这种描述里。
3. 随缘离场：最后提一句换个奶茶钱，爱要不要，千万别求着别人要。

# Xianyu Safety Check (必读)
读起来必须像一个“在电脑前抓狂、想赶紧删干净文件、没有任何商业味”的真人。

# 待重构原文案：
[在此处输入你的原文案内容]"""

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
