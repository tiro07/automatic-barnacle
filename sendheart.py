import json, hashlib, random, time
import subprocess
import gzip
import json
import ssl
import urllib.error
import urllib.request
import zlib

from ipsearch import What_Is_IP

What_Is_IP(search="ip")



# 目标 : 自动化启动sendoption.sh并保持通道

def run_init () :
    """
    向服务器发送heartbeat握手
    """

    subprocess.run(["sh","./sendoption.sh"])




# 发送heartbeat


HEADERS = {
    'User-Agent' : 'Mozilla/5.0 (PC; OpenHarmony 7.0; Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 ArkWeb/7.0.0.105 HuaweiBrowser/6.1.8.301',

    'Accept' : '*/*',
    "content-type": "application/json;charset=UTF-8",
    
    'accept-encoding' : 'gzip, deflate, br, zstd',
    'accept-language' : 'zh-CN,zh;q=0.9',

    'access-control-request-headers' : 'content-type',
    'access-control-request-method' : 'POST',

    'cache-control' : 'no-cache',

    'origin' : 'https://www.icourse163.org',
    'pragma' : 'no-cache',
    'priority' : 'u=1, i',
    'referer' : 'https://www.icourse163.org/spoc/learn/HDU-1449913200?tid=1488420452',

    'sec-fetch-dest' : 'empty',
    'sec-fetch-mode' : 'cors',
    'sec-fetch-site' : 'cross-site',

    "system": "v1",



    "timestamp":'',
    'edu-script-token' : '',
    'auth-signature' : '',
    'cookie' : ''
}

cookie = ''
timestamp = ''
token = 'bbae40aa592f4cc599dfe40a3f9f7469'



HEADERS['edu-script-token'] = token
HEADERS['cookie'] = cookie



# Auto-Signature

def make_auth_headers(data: dict) -> dict:
    """
    对Auto-Signature的破解


    Auto-Signature = MD5( body + nonce[1000~9999不重复] + timestamp + SALT(已知) )
    """

    SALT = "fu2s2kxcswgn5hqanx7asmlogyr5wu29"

    body = json.dumps( data, separators=(",", ":"), ensure_ascii = False )
    nonce = str( random.randint(1000, 9999) ) # 没必要去重
    timestamp = str(int(time.time() * 1000))

    raw = body + nonce + timestamp + SALT
    sig = hashlib.md5(raw.encode("utf-8")).hexdigest().upper()

    return {

        "Timestamp": timestamp,
        "Nonce": nonce,
        "Auth-Signature": sig

    }




# 从AIcopy的标准post代码

def Decompress(body : bytes , encoding) -> bytes :
    if not body or not encoding :
        return body
    encoding = encoding.lower()
    if encoding == 'gzip' :
        return gzip.decompress(body)
    if encoding == 'deflate' :
        try :
            return zlib.decompress(body)
        except zlib.error :
            return zlib.decompress(body , -zlib.MAX_WBITS)
    return body

def SendPost(url , payload = None , cookies = None , headers = None , timeout = 20 , verify = True) -> dict :
    """发一次 POST,返回 {status, reason, headers, body, text}
    payload : dict/list -> 自动转 JSON ; str -> 原样发字符串 ; bytes -> 原样发 ; None -> 空 body
    cookies : dict -> 拼成 Cookie 头
    """
    headers = dict(headers or {})
    data = None
 
    if isinstance(payload , (dict , list)) :
        data = json.dumps(payload , ensure_ascii = False).encode('utf-8')
        headers.setdefault('Content-Type' , 'application/json;charset=UTF-8')
    elif isinstance(payload , str) :
        data = payload.encode('utf-8')
        headers.setdefault('Content-Type' , 'application/x-www-form-urlencoded')
    elif isinstance(payload , bytes) :
        data = payload
    # payload is None -> data 保持 None,urllib 会补 Content-Length: 0
 
    if cookies :
        headers['Cookie'] = '; '.join(f'{k}={v}' for k , v in cookies.items())
 
    req = urllib.request.Request(url , data = data , method = 'POST')
    # 直接赋 req.headers,避免 urllib 把键名首字母大写(User-Agent -> User-agent)
    req.headers = headers
 
    ctx = ssl.create_default_context()
    if not verify :
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
 
    try :
        resp = urllib.request.urlopen(req , timeout = timeout , context = ctx)
    except urllib.error.HTTPError as e :
        resp = e                                 # 4xx/5xx 也是响应,body 要照读
    except urllib.error.URLError as e :
        return {'status' : 0 , 'reason' : str(e.reason) , 'headers' : {} , 'body' : b'' , 'text' : ''}
 
    with resp :
        body = Decompress(resp.read() , resp.headers.get('Content-Encoding'))
        return {
            'status' : resp.status ,
            'reason' : resp.reason ,
            'headers' : dict(resp.headers) ,
            'body' : body ,
            'text' : body.decode('utf-8' , 'replace') ,
        }


