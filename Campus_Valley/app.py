import gradio as gr
from image_understanding import PictureUnderstanding
from retro_diffusion import RetroDiffusionGenerator
from config import img_udstand_appId, img_udstand_apiKey, img_udstand_apiSecret, RETRO_API_KEY
from story_generator import generate_stardew_quote

custom_css = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                 Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background-color: #f5f7fa;
    color: #333;
    margin: 0;
    padding: 0;
}
.gradio-container {
    background: white;
    max-width: 900px;
    margin: 40px auto;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    padding: 30px 40px;
}
h1 {
    font-weight: 700;
    font-size: 28px;
    color: #4a90e2;
    text-align: center;
    margin-bottom: 30px;
}
.gr-button {
    background-color: #4a90e2;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 12px 30px;
    border: none;
    box-shadow: 0 4px 12px rgba(74,144,226,0.4);
    transition: background-color 0.3s ease;
    cursor: pointer;
}
.gr-button:hover {
    background-color: #357ABD;
}
.gr-row {
    gap: 30px;
}
.gr-column {
    display: flex;
    flex-direction: column;
    gap: 20px;
}
.gr-textbox textarea {
    font-size: 16px;
    line-height: 1.5;
    resize: vertical;
}
.gr-image {
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
"""

def dummy_fn(img):
    return "这里显示星露谷风格描述。", img

# 初始化图片理解器
understander = PictureUnderstanding(
    img_udstand_appId,
    img_udstand_apiKey,
    img_udstand_apiSecret    
)

# 初始化像素图生成器
generator = RetroDiffusionGenerator(api_key=RETRO_API_KEY)

# Gradio 处理函数
def pipeline(image_path):
    prompt_image = """
    请将这张校园照片描述为像素风电子游戏（例如《星露谷物语》）中一个细致的互动场景。
    请非常具体地描述，并包含以下内容：

    1. **场景布局和物体位置**：前景、中景和背景中分别有哪些物体或人物？建筑物、树木、人物、长椅等的位置（例如，“左侧”、“中间”、“右上角”）？

    2. **建筑物**：颜色、材质、屋顶类型、楼层数、阳台细节、窗户形状及其在场景中的相对位置。

    3. **自然元素**：树木、花卉、草地、落叶的类型和位置，以及天气效果（例如阴影、阳光过滤）。

    4. **人物**：有多少人？他们在哪里？他们在做什么、穿什么、拿什么或说什么？

    5. **物品和装饰**：自动售货机、长椅、自行车、路标、路灯、栅栏、宠物或鸟类——以及它们的具体位置。

    6. **时间和氛围**：是早上、下午还是晚上？现在是什么季节？光线和天空是什么样子的？

    描述一下这个场景，就像你在帮助游戏美术师**以像素风格绘制这个布局**一样。包括清晰的左右中心方向、物体的分层（前后），并使其舒适有趣。
    用英语书写。
    """
    
    # 调用讯飞星火图像理解
    try:
        description = understander.understanding(prompt_image, image_path)
    except Exception as e:
        return f"图像理解失败: {e}",None
    
    try:
        story = generate_stardew_quote(description)
    except Exception as e:
        return f"故事生成失败: {e}",None

    # 调用 Retro Diffusion 生成像素图
    try:
        output_path = generator.generate_image(description, save_path='./output_image/result.png')
    except Exception as e:
        return f"图像生成失败: {e}", None

    return story,output_path

with gr.Blocks(css=custom_css, title="PixSchool") as demo:
    gr.HTML("<h1>🌸 PixSchool: 像素校园生成器</h1>")
    with gr.Row():
        with gr.Column(scale=1):
            input_img = gr.Image(type="filepath", label="🎒 上传你的校园照片", interactive=True)
            btn = gr.Button("✨ 开始转换")
        with gr.Column(scale=1):
            output_text = gr.Textbox(label="📜 星露谷风格描述", lines=8, interactive=False)
            output_img = gr.Image(label="🖼️ 像素风生成图")

    btn.click(pipeline, inputs=input_img, outputs=[output_text, output_img])

demo.launch()



