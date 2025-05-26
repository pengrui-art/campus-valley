import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse, urlencode
from wsgiref.handlers import format_date_time
import ssl
from time import mktime
import websocket  # 使用 websocket-client

# WebSocket返回内容
answer = ""
isFirstcontent = False

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    def create_url(self):
        now = datetime.datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = f"host: {self.host}\n" + f"date: {date}\n" + f"GET {self.path} HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        url = self.Spark_url + '?' + urlencode(v)
        return url


def on_error(ws, error):
    print("### error:", error)


def on_close(ws, *args):
    pass


def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, domain=ws.domain, question=ws.question))
    ws.send(data)


def on_message(ws, message):
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        text = choices['text'][0]
        global answer, isFirstcontent

        if 'reasoning_content' in text and text['reasoning_content']:
            isFirstcontent = True

        if 'content' in text and text['content']:
            content = text["content"]
            answer += content

        if status == 2:
            ws.close()


def gen_params(appid, domain, question):
    return {
        "header": {
            "app_id": appid,
            "uid": "1234",
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 1.2,
                "max_tokens": 32768
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }

# 对话上下文（这里初始化只使用一次）
text = []

def getText(role, content):
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text

def getlength(text):
    return sum(len(c["content"]) for c in text)

def checklen(text):
    while getlength(text) > 8000:
        del text[0]
    return text

def generate_stardew_quote(description):
    global answer, isFirstcontent
    answer = ""
    isFirstcontent = False

    appid = '874b2597'
    api_secret = 'YWFhOTVhMmUwM2EwNDBjNThmZTcyM2Fl'
    api_key = 'ec8c63f9521c4833d7cd26420a174be6'
    domain = "x1"
    Spark_url = "wss://spark-api.xf-yun.com/v1/x1"

    # 
    # 使用用户上传图片生成的图像描述作为提示
    prompt = """
    你是一个像素风格游戏《星露谷物语》的世界观设计师。
    请根据以下场景描述，创作一段幻想风格的游戏元素介绍，可以是某个植物、建筑、地点或角色。

    要求：
    1. 内容具有梦幻感、自然感，结合魔法、民间传说、情绪等要素；
    2. 使用游戏描述格式，如果是物品就生成例如“仙女玫瑰：传说它能吸引仙女。生命值+5,能量+10”;
    如果是场景就生成例如”清晨的阳光洒在潮湿的土地上，薄雾轻轻笼罩着田埂。远处的鸡舍传来咯咯的叫声，你推开小屋的门，一股泥土与青草的气息扑面而来。”
    3. 内容不要超过100字(使用中文)
    4. 可以加入道具效果、背景故事、用途或传说。
    5. 必须完全保留场景描述中的 **时间（如早晨、下午）、天气（阳光、阴天）、季节（如春季、秋季）等要素**，不要改变这些设定；
    6. 不要创造与输入场景相矛盾的时间、天气或季节细节。

    场景描述如下：
    {description}

    """ 

    question = checklen(getText("user", prompt))

    wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close,
                                 on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.domain = domain

    print("星火生成中：")
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return answer.strip()

# 测试语录生成
if __name__ == "__main__":
    while True:
        input("按回车生成一句星露谷语录：")
        quote = generate_stardew_quote()
        print("星露谷语录：", quote)


