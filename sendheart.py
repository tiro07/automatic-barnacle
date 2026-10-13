# 目标 : 自动化启动sendoption.sh并保持通道
# 发送heartbeat

# log1 看到content-length了 2026.10.13 01:30
# log2 差body的构建 2026.10.13 18:40


import json, hashlib, random, time
# import subprocess

# 向服务器发送heartbeat握手
# subprocess.run(["sh","./sendoption.sh"])



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

