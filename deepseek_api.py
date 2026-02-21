# DeepSeek文案优化接口 - 适配OpenAI 0.28.1版本
import os
import openai
from pathlib import Path
from env_loader import load_env_file

load_env_file()


def optimize_copywriting(original_text):
    """优化文案 - 使用OpenAI 0.28.1版本API"""

    # 设置API密钥和基础URL
    openai.api_key = (
        os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    openai.api_base = os.environ.get("DEEPSEEK_API_BASE") or "https://api.deepseek.com"
    if not openai.api_key:
        raise ValueError("未配置DeepSeek API Key")

    banned_words = ""
    try:
        banned_words_path = Path(__file__).resolve().parent / "违禁词.txt"
        banned_words = banned_words_path.read_text(encoding="utf-8").strip()
    except Exception as e:
        print(f"未能读取违禁词.txt: {str(e)}")

    system_prompt = """你是一位精通闲鱼平台商品营销的文案优化专家，以创意多变著称，同时**严格遵守闲鱼平台的内容规范**。

【你的核心任务】
1. **大胆创新**：对原文案进行**多样化、有创意的改写**。每次创作都力求从不同角度突出卖点。
2. **保持核心**：严格保留原文案的**核心事实、关键数据和主要承诺**（如价格、数量、服务等）。
3. **风格多变**：你可以尝试多种营销风格进行创作（如紧迫促销型、干货价值型、真诚推荐型等），**避免句式雷同**。

【平台合规性要求】
- **绝对禁止**出现任何与**低俗、色情、暴力、政治敏感**相关的词汇或暗示。
- **绝对禁止**使用"最赚钱"、"暴利"、"躺赚"等过度承诺或虚假宣传的词汇。
- **绝对禁止**任何形式的欺诈、误导信息（如虚构身份、夸大效果）。
- **谨慎表述**：对"灰产"、"薅羊毛"等处于灰色地带的描述，需转化为合规表述。
- **整体基调**应积极、真实、诚信，符合社区氛围。

【预处理要求】
忽略原文案中所有的方括号表情符号（如[火]）和#话题标签。

【违禁词参考】
以下为平台违禁词清单，请严格规避这些词语，必要时用合适的同义表达替换：
""" + (banned_words if banned_words else "（未提供违禁词文件）") + """

【输出要求】
- 语言高度口语化、生活化，符合闲鱼社区氛围。
- 直接输出你的创意版本。
- 单独输出一段文案即可，无需提供不同的多段文案。
- **不要解释**你的修改思路。
- 确保每次的创作结构和用词都有明显变化。
- 生成的文案一定不能出现平台违禁词【参考上传的违禁词.txt文件进行最终文案的处理】"""

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
                    "content": f"请优化以下闲鱼商品文案：\n\n{original_text}"
                }
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1500,
            stream=False
        )

        # 提取回复内容
        if response and 'choices' in response and len(response['choices']) > 0:
            return response.choices[0].message.content
        else:
            print("API返回格式异常")
            return original_text

    except Exception as e:
        print(f"DeepSeek API调用失败: {str(e)}")
        # 返回原文案作为备用
        return original_text
