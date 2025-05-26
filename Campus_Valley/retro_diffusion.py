#文生图，一个好用的像素图片生成模型

import requests
from PIL import Image
from io import BytesIO
import base64


class RetroDiffusionGenerator:
    def __init__(self, api_key: str, model: str = "RD_FLUX"):
        """
        初始化
        :param api_key: 从 RetroDiffusion 官网获取的 API key
        :param model: 使用的模型名称，默认 RD_FLUX
        """
        self.api_key = api_key
        self.model = model
        self.url = "https://api.retrodiffusion.ai/v1/inferences"

    def generate_image(self, prompt: str, save_path: str = "output.png", width: int = 512, height: int = 512) -> str:
        """
        调用 Retro Diffusion API,根据 prompt 生成图像
        :param prompt: 文本描述
        :param save_path: 图像保存路径
        :param width: 图像宽度
        :param height: 图像高度
        :return: 图像保存路径
        """
        headers = {
            "X-RD-Token": self.api_key
        }

        payload = {
            "model": self.model,
            "width": width,
            "height": height,
            "prompt": prompt,
            "num_images": 1
        }

        response = requests.post(self.url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"图像生成失败，状态码：{response.status_code}，响应内容：{response.text}")

        result = response.json()
        base64_image = result.get("base64_images", [None])[0]
        if not base64_image:
            raise Exception("未在响应中找到 base64 编码图像。")

        # 解码 base64 并保存为 PNG
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))
        image.save(save_path)

        return save_path

if __name__ == '__main__':
    from image_understanding import PictureUnderstanding
    from config import img_udstand_appId, img_udstand_apiKey, img_udstand_apiSecret, RETRO_API_KEY

    # 图片理解初始化
    understander = PictureUnderstanding(
        img_udstand_appId,
        img_udstand_apiKey,
        img_udstand_apiSecret    
    )

    # 指定图片路径
    image_path = './campus_image/img1.jpg'

    # 提示词：如何让图像理解生成更适合像素风图像生成
    prompt = """
    请将这张校园图片描述成一个星露谷物语风格的像素游戏场景。
    描述要具体，包括画面中有哪些人物、他们在做什么，有哪些建筑、植物、装饰物和天气情况。请用英语回答。
    """

    print("正在调用图片理解 API...")
    description = understander.understanding(prompt, image_path)
    print("图片理解结果：", description)

    print("正在调用 Retro Diffusion 文生图 API...")
    generator = RetroDiffusionGenerator(api_key=RETRO_API_KEY)
    output_path = generator.generate_image(description, save_path='./output_image/test_result.png')
    print(f"图像生成完成，已保存至：{output_path}")

