import json, hashlib, random, time
import subprocess
import gzip
import json
import ssl
import urllib.error
import urllib.request
import zlib
from ipsearch import What_Is_IP



timestamp = str( int( time.time()*1000 ) )

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
# ---


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
# ---