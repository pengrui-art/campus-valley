#图像理解，用户输入图像，模型将理解图像里的内容并生成文本
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client

from dwspark.config import Config
from loguru import logger
from config import img_udstand_apiKey,img_udstand_apiSecret,img_udstand_appId


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        print(url)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


class PictureUnderstanding(object):

    def __init__(self, appid, apikey, apisecret, model_url:str = 'wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image'):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret
        self.model_url = model_url

    def understanding(self, question:str, picture_path:str) -> str:
        wsParam = Ws_Param(self.appid, self.apikey, self.apisecret, self.model_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=self.__on_message, on_error=self.__on_error, on_close=self.__on_close, on_open=self.__on_open)
        ws.question = question
        ws.messages = [{"role": "user", "content": str(base64.b64encode(open(picture_path,'rb').read()), 'utf-8'), "content_type":"image"}]
        ws.answer = ''
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return ws.answer


    # 收到websocket错误的处理
    def __on_error(self, ws, error):
        print("### error:", error)


    # 收到websocket关闭的处理
    def __on_close(self, ws,one,two):
        print(" ")


    # 收到websocket连接建立的处理
    def __on_open(self, ws):
        thread.start_new_thread(self.__run, (ws,))


    def __run(self, ws, *args):
        messages = self.__getText('user', ws.question, ws.messages)
        data = json.dumps(self.__gen_params(question = messages))
        ws.send(data)


    # 收到websocket消息的处理
    def __on_message(self, ws, message):
        #print(message)
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            ws.answer += content
            # print(1)
            if status == 2:
                ws.close()

    def __gen_params(self, question):
        """
        通过appid和用户的提问来生成请参数
        """

        data = {
            "header": {
                "app_id": self.appid
            },
            "parameter": {
                "chat": {
                    "domain": "imagev3",
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2028,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }

        return data

    def __getText(self, role, content, messages):
        messages.append({'role': role, 'content': content})
        return messages

if __name__ == '__main__':
    model = PictureUnderstanding(img_udstand_appId, img_udstand_apiKey, img_udstand_apiSecret)
    prompt = """
    请将这张校园图片描述成一个星露谷物语风格的像素游戏场景。
    详细说明画面中有哪些人物、他们在做什么，有哪些建筑、花草树木、装饰物、天气情况等内容。
    使用富有画面感和幻想风格的描述方式，为后续图像生成模型提供参考。
    """
    answer  = model.understanding(prompt, '.\campus_image\img1.jpg')
    logger.info(answer)