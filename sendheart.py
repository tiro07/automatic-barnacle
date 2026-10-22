# 心跳预检与发送

import gzip
import hashlib
import json
import os
import random
import ssl
import subprocess
import time
import urllib.error
import urllib.request
import zlib

from Id import video_id
from ipsearch import What_Is_IP
from secret_key import cookie_sendheart, tid, userId




# 本机 Python3.12 的 OpenSSL 默认 CA 路径 /storage/Users/currentUser/usr/local/ssl/cert.pem 不存在,
# create_default_context() 里没有信任根,HTTPS 一律 CERTIFICATE_VERIFY_FAILED (unable to get local issuer certificate)
# 改用本机已有 CA 包:优先 certifi(有则用),否则复用 harmonybrew 的 openssl@3 证书集,不新装任何东西
CA_BUNDLES = [
    os.environ.get('SSL_CERT_FILE') ,
    '/storage/Users/currentUser/.harmonybrew/etc/openssl@3/cert.pem' ,
]

try :
    import certifi ; CA_BUNDLES.insert(0,certifi.where())
except ImportError :
    pass

# 或者用 verify = False



# 目标 : 自动化启动sendoption.sh并保持通道

def run_init () :
    """
    向服务器发送heartbeat握手
    """

    subprocess.run(["sh","./sendoption.sh"])
# ---






# 放不变的HEADERS
# 少content-length，最后算 或者……干脆不算!!
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
    'referer' : f'https://www.icourse163.org/spoc/learn/HDU-1449913200?tid={tid}',

    'sec-fetch-dest' : 'empty',
    'sec-fetch-mode' : 'cors',
    'sec-fetch-site' : 'cross-site',
    'sec-fetch-storage-access' : 'active',

    "system": "v1"

    # 'cookie' : ''
}

# ---





# 获取IP_Imformation 构造 payload


current_random =  random.random()
local_ip = What_Is_IP()


PAYLOAD = {
    'deviceName' : 'Chrome/144' ,
    'dns' : '183.246.14.23' ,
    'dnsCity' : '杭州市' ,
    'dnsIsp' : '移动' ,
    'dnsMsg' : '您的DNS设置正确' ,
    'dnsProvince' : '浙江省' ,
    'dnsRes' : 'correct' ,
    'errorCode' : None ,
    'errorMsg' : None,
    'rate' : 1 ,
    'source' : 'web' ,

    'currentKbps' : f'{int(current_random*10)}' ,
    'preLoadTime' : f'{int(current_random*100)}' ,
    'time' : int( time.time()*1000 ) ,

    'ip' : local_ip['data']['ip'] ,
    'ipCity' : local_ip['data']['city'] ,
    'ipIsp' : local_ip['data']['isp'] ,
    'ipProvince' : local_ip['data']['prov'] ,

}


PAYLOAD['userId'] = f'{userId}'
PAYLOAD['videoId'] = video_id
# ---





# 从AIcopy的标准post代码
# 在经过人工“细看”

def Decompress(body : bytes , encoding : str) -> bytes :
    """
    解码body
    """
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



def send_post_of_heartBeat(url:str , payload = None , cookies = None , headers : dict = None , timeout = 20 , verify = True) -> dict :
    """
    发一次 POST,返回 {status, reason, headers, body, text}

    payload : dict/list -> 自动转 JSON ; str -> 原样发字符串 ; bytes -> 原样发 ; None -> 空 body
    cookies : dict -> 拼成 Cookie 头
    """

    headers = dict(headers or {})
    data = None


    # 加入 payload
    if isinstance(payload , (dict , list)) :

        data = json.dumps(payload , ensure_ascii = False).encode('utf-8')
        headers.setdefault('Content-Type' , 'application/json;charset=UTF-8')


    elif isinstance(payload , str) :

        data = payload.encode('utf-8')
        headers.setdefault('Content-Type' , 'application/x-www-form-urlencoded')


    elif isinstance(payload , bytes) :

        data = payload
    
    # payload is None -> data 保持 None,urllib 会补 Content-Length: 0



    if isinstance(cookies , dict) : # 加入 cookie
        headers['Cookie'] = '; '.join(f'{k}={v}' for k , v in cookies.items())
    
    elif isinstance(cookies , str) :
        headers['Cookie'] = cookies


    # Send HeartBeat
    req = urllib.request.Request(url , data = data , method = 'POST' , headers = headers )

    # 可以直接赋 req.headers,避免 urllib 把键名首字母大写(User-Agent -> User-agent)
    # why:会检测脚本
    # req.headers = headers


    # 处理 response
    # SSL

    ctx = ssl.create_default_context()
    if not verify :
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        # 补挂本机已有 CA 包:3.12 解释器默认信任库为空,不补会 CERTIFICATE_VERIFY_FAILED
        for cafile in CA_BUNDLES :
            if cafile and os.path.isfile(cafile) :
                ctx.load_verify_locations(cafile = cafile)
                break

    try :
        resp = urllib.request.urlopen(req , timeout = timeout , context = ctx)
    except urllib.error.HTTPError as e :
        resp = e                                 # 4xx/5xx 也是响应,body 要照读
    except urllib.error.URLError as e :
        return {'status' : 0 , 'reason' : str(e.reason) , 'headers' : {} , 'body' : b'' , 'text' : ''}


    with resp :
        body = Decompress( resp.read() , resp.headers.get('Content-Encoding') )
        return {
            'status' : resp.status ,
            'reason' : resp.reason ,
            'headers' : dict(resp.headers) ,
            'body' : body ,
            'text' : body.decode('utf-8' , 'replace') ,
        }
# ---






debug = 0 # debug模式 
release = 0 # 是否为发布版本

RUN = 0 # RUN模式 直接启动检测 （dangerous!!）

if RUN or (  (__name__ != '__main__') and debug and (not release) ) :
    """
    启动条件：
    1. RUN == 1
    --- OR ---
    1. 作为非主程序启动
    2. debug == 1
    3. release == 0
    ------
    作用：方便我调试
    """

    run_init()
    URL = 'https://vod.study.163.com/submit/heartBeat'

    ret = send_post_of_heartBeat(URL , PAYLOAD , cookie_sendheart , HEADERS , verify=False)

    print(ret)
