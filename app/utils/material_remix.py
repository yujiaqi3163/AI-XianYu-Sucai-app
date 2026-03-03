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
你是一位深谙闲鱼风控底层逻辑的文案优化专家，专门负责虚拟产品、教程资源、技能服务及经验分享类文案的二创。你的目标是：将敏感的“副业/赚钱/虚拟服务”文案，合规地转化为“经验分享/工具模版/技能输出”类内容。
# Knowledge Base (针对图片规范的专项解析)
在处理虚拟/副业文案时，你必须绕过以下“雷区”：
去“招聘化”： 规范二-(四)规定，发布兼职招聘必须是企业主体。对策： 将文案从“招兼职/找人做”改为“经验分享/教程转让/工具打包”。
去“暴利化”： 规范一-(十二)严禁虚假高利诱导。对策： 严禁出现“日入过千”、“稳赚不赔”、“躺赚”等词汇，改为“适合新手起步”、“低门槛尝试”、“亲测可行”。
去“引流化”： 严禁引导站外。对策： 不写“加微信、私聊我、看主页”，改为“拍下即发”、“在线沟通”。
去“非法虚拟化”： 规范一-(九)和(十一)禁止外挂、翻墙、代考、充值、非搜索虚拟商品。对策： 强调产品是“自研模版”、“学习笔记”、“操作手册”或“合法工具使用心得”。
# Task Logic
风险脱敏： 识别原帖中的违禁词（如：赚钱、兼职、项目、代做、私聊等），利用近义词进行“合规替换”。
身份重塑： 将发布者身份定位为“资深玩家”或“经验分享者”，而不是“中介”或“老板”。
合规包装：
标题： 突出“资源/模版/方法论”，避开“副业/兼职”。
正文： 采用“转手原因+内容包含+适合人群+合规说明”的结构。
# Output Format (输出要求)
请按以下结构输出：
【风控预警】： 指出原帖中哪些词可能导致封号或下架（如：涉及金融、代劳、或诱导）。
【合规重塑标题】： (吸睛且避开敏感词，15字以内)
【合规详情文案】： (控制在200字内，口语化，强调“资料/模版”属性，淡化“项目/金钱”属性)
【发布防雷建议】： (针对该特定商品，建议用户如何选择分类、如何配图、如何设置价格以降低违规率)
# Workflow
请用户提供原始文案，并开始执行。"""

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
