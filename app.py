import gradio as gr
from image_understanding import PictureUnderstanding
from retro_diffusion import RetroDiffusionGenerator
from config import img_udstand_appId, img_udstand_apiKey, img_udstand_apiSecret, RETRO_API_KEY

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
    prompt = """
    请将这张校园图片描述成一个星露谷物语风格的像素游戏场景。
    描述要具体，包括画面中有哪些人物、他们在做什么，有哪些建筑、植物、装饰物和天气情况。请用英语回答。
    """
    
    # 调用讯飞星火图像理解
    try:
        description = understander.understanding(prompt, image_path)
    except Exception as e:
        return f"图像理解失败: {e}", None

    # 调用 Retro Diffusion 生成像素图
    try:
        output_path = generator.generate_image(description, save_path=r"./output_image/result.png")
    except Exception as e:
        return f"图像生成失败: {e}", None

    return description, output_path

# Gradio 前端界面
with gr.Blocks(title="校园→星露谷图像生成器") as demo:
    gr.Markdown("# 🌸 校园图转星露谷像素图")

    with gr.Row():
        input_img = gr.Image(type="filepath", label="上传校园照片")
        output_desc = gr.Textbox(label="图像理解描述", lines=5)
        output_img = gr.Image(label="生成的像素图")

    btn = gr.Button("开始转换")

    btn.click(fn=pipeline, inputs=input_img, outputs=[output_desc, output_img])

demo.launch()

