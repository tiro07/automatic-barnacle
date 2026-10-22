import json, hashlib, random, time
import subprocess
import gzip
import json
import ssl
import urllib.error
import urllib.request
import zlib
from ipsearch import What_Is_IP



noncelist = []

def append_nonce (Min : int = 1000 , Max : int = 9999) -> int | None :
    """
    retuen a number between Min && Max which is not appear in the list 'noncelist'
    else retuen None
    """
    global noncelist

    a = random.randint(Min,Max)

    if a not in noncelist :
        noncelist.append(a)
        return a
    elif len(noncelist) < Max-Min+1 : # 防止调用过多
        return append_nonce(Min,Max)
    else :
        return None




# Auto-Signature 通过逆向77593.63c11554.chunk.js得出
# 算法：body + 四位随机数(用于去重) + 时间戳(检验新鲜度) + 公开盐(SALT)
# 进行md5

def make_auth_headers(data: dict , nonce : int) -> dict:
    """
    对Auto-Signature的破解

    Auto-Signature = MD5( body + nonce[1000~9999不重复] + timestamp + SALT(已知) )
    SALT = "fu2s2kxcswgn5hqanx7asmlogyr5wu29"
    """

    SALT = "fu2s2kxcswgn5hqanx7asmlogyr5wu29"

    body = json.dumps( data, separators=(",", ":"), ensure_ascii = False )
    nonce = noncelist # 其实我感觉没必要去重 但还是去了

    if nonce is None :
        raise Exception('a')

    timestamp = str(int(time.time() * 1000))

    raw = body + nonce + timestamp + SALT
    sig = hashlib.md5(raw.encode("utf-8")).hexdigest().upper()

    return {

        "Timestamp": timestamp,
        "Nonce": nonce,
        "Auth-Signature": sig

    }
# ---
