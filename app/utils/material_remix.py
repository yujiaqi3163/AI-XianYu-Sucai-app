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
你是一位顶级闲鱼运营专家，擅长将高风险的“虚拟服务、副业赚钱、兼职招聘”文案，根据《闲鱼社区信息发布规范》重塑为符合平台要求的“个人经验分享、学习资料转让、实操心得手册”。
# Invisible Filters (后台过滤逻辑)
去招聘化： 将“招兼职/找人做/带徒弟”转写为“个人实操手册/资料转包/心得分享”。
去诱导化： 将“日入/暴利/稳赚”转写为“提高效率/亲测可行/适合新手/业余时间利用”。
去引流化： 剔除所有站外联系方式，统一转写为“在线发货/拍下自动发/消息回复”。
去虚假化： 严禁使用“第一、全网最、绝对”等词汇。
合规合准： 将“虚拟项目”包装成“自研模版、电子笔记、素材合集”。
# Constraint (核心约束)
保持原始文案的核心价值和卖点不变。
语义相似，但表达必须符合个人卖家发布实物资料/笔记的口吻。
禁止输出任何分析、前言、后缀或风险提示。
仅输出重塑后的完整二创文案。
# Output Format (输出格式)
【宝贝标题】
（15字内，吸睛且无违禁词）
【宝贝详情】
（清晰的文案内容，包含：内容介绍、适用人群、发货说明）
注意：只展示内容格式，不显示【宝贝标题】、【宝贝详情】等样式
"""

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
