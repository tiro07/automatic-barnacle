# ip的查找

import time
from dataclasses import dataclass
from typing import Any, Type, TypeVar, cast

import requests
from cachetools.func import ttl_cache

# 复制网站上的“生成模型代码”
# 增加 查询的IP地址 字段的引用

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()



@dataclass
class Data:
    """数据体"""
    """区县"""
    area: str
    """电话编号"""
    area_code: str
    """国内大区划分"""
    big_area: str
    """城市"""
    city: str
    """城市简码"""
    city_code: str
    """城市简码"""
    city_short_code: str
    """国家/地区"""
    country: str
    """国家/地区简码"""
    country_code: str
    """查询的ip地址"""
    ip: str
    """运营商"""
    isp: str
    """城市中心-纬度"""
    lat: str
    """城市中心-经度"""
    lng: str
    """longip"""
    long_ip: float
    """邮政编码"""
    post_code: str
    """省份"""
    prov: str

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        assert isinstance(obj, dict)
        area = from_str(obj.get("area"))
        area_code = from_str(obj.get("area_code"))
        big_area = from_str(obj.get("big_area"))
        city = from_str(obj.get("city"))
        city_code = from_str(obj.get("city_code"))
        city_short_code = from_str(obj.get("city_short_code"))
        country = from_str(obj.get("country"))
        country_code = from_str(obj.get("country_code"))
        ip = from_str(obj.get("ip"))
        isp = from_str(obj.get("isp"))
        lat = from_str(obj.get("lat"))
        lng = from_str(obj.get("lng"))
        long_ip = from_float(obj.get("long_ip"))
        post_code = from_str(obj.get("post_code"))
        prov = from_str(obj.get("prov"))
        return Data(area, area_code, big_area, city, city_code, city_short_code, country, country_code, ip, isp, lat, lng, long_ip, post_code, prov)

    def to_dict(self) -> dict:
        result: dict = {}
        result["area"] = from_str(self.area)
        result["area_code"] = from_str(self.area_code)
        result["big_area"] = from_str(self.big_area)
        result["city"] = from_str(self.city)
        result["city_code"] = from_str(self.city_code)
        result["city_short_code"] = from_str(self.city_short_code)
        result["country"] = from_str(self.country)
        result["country_code"] = from_str(self.country_code)
        result["ip"] = from_str(self.ip)
        result["isp"] = from_str(self.isp)
        result["lat"] = from_str(self.lat)
        result["lng"] = from_str(self.lng)
        result["long_ip"] = to_float(self.long_ip)
        result["post_code"] = from_str(self.post_code)
        result["prov"] = from_str(self.prov)
        return result



@dataclass
class ApifoxModel:
    """数据体"""
    data: Data
    """查询时间-秒"""
    qt: float
    """状态码"""
    ret: int

    @staticmethod
    def from_dict(obj: Any) -> 'ApifoxModel':
        assert isinstance(obj, dict)
        data = Data.from_dict(obj.get("data"))
        qt = from_float(obj.get("qt"))
        ret = from_int(obj.get("ret"))
        return ApifoxModel(data, qt, ret)

    def to_dict(self) -> dict:
        result: dict = {}
        result["data"] = to_class(Data, self.data)
        result["qt"] = to_float(self.qt)
        result["ret"] = from_int(self.ret)
        return result



def apifox_model_from_dict(s: Any) -> ApifoxModel:
    return ApifoxModel.from_dict(s)



def apifox_model_to_dict(x: ApifoxModel) -> Any:
    return to_class(ApifoxModel, x)
# ---





# 手写的API查询请求,包含报错

def get_ip_information(ip: str | None = None, AutoPolling: bool = True ,max_req_num : int = 5) -> dict :
    """
    ip : str (ipv4 或 ipv6) (可选 IP == None 则查询本地IP)
    AutoPolling : True 否则出错后退出
    max_req_num : 轮询次数 = 5
    



    不想做IDE调用提示优化,你自己看着办呗 ><

    search URL = https://ip9.com.cn


    返回json

    举例:

    {

        "ret": 200,                  // 200为正常

        "data": 
        {
            "ip": "58.30.0.0",         // 查询的IP地址
            "country": "中国",          // 国家/地区
            "country_code": "cn",      // 国家/地区简码
            "prov": "北京",             // 省份
            "city": "北京",             // 城市
            "city_code": "beijing",    // 城市拼音
            "city_short_code": "bj",   // 城市简码
            "post_code": "100000",     // 邮政编码
            "area_code": "010",        // 电话区号
            "isp": "中国移动",          // 运营商
            "lng": "116.41",           // 城市中心-经度
            "lat": "39.93",            // 城市中心-纬度
            "long_ip": 975044608,      // longip
            "big_area": "华北",         // 国内大区划分

            // VIP 字段
            "area": "东城",             // 区县
            "ip_type": "ISP",          // IP类型 [ISP:家庭用户] [BUS:企业专线] [IDC:机房/数据中心]
            "ip_asn": "AS17429"        // AS号
        },
        
        "qt": 0.001                  // 查询时间-秒
    }
    """


    org_url = "https://ip9.com.cn/get"

    url = org_url # 可以查询自己的IP

    if ip is not None :
        url += "?" + f"ip={ip}"

    payload = {} ; headers = {}



    # max_req_num = 5
    wait_time = 2
    time_out = 5



    while max_req_num > 0 :

        status = None #先给status赋初值

        try :

            max_req_num -= 1
            response = requests.request("GET", url, headers=headers, data=payload, timeout=(time_out,time_out+2))

            status = response.status_code
            response.raise_for_status()
            data : dict = response.json()



            if 200 <= status < 300 :
                return data


        except requests.exceptions.ConnectTimeout as connect_error :

            if max_req_num != 0 and AutoPolling :
                time.sleep(wait_time)
                wait_time *= 2

                continue
            else :

                raise requests.exceptions.ConnectTimeout("连接超时,请检查网络") from connect_error

        except requests.exceptions.ReadTimeout as read_time_out_error :

            if max_req_num != 0 and AutoPolling :

                time.sleep(wait_time)
                wait_time *= 2

                continue
            else :

                raise requests.exceptions.ReadTimeout("读取超时,请检查网络") from read_time_out_error
        
        except requests.exceptions.HTTPError as http_error :

            if status == 400 or (status is None):

                raise ValueError("IP格式错误")

            if max_req_num != 0 and AutoPolling :

                time.sleep(wait_time)
                wait_time *= 2

                continue
            
            else :

                raise requests.exceptions.HTTPError("HTTP错误,请检查网络") from http_error

        except requests.exceptions.JSONDecodeError as json_decode_error :

            if max_req_num != 0 and AutoPolling :

                time.sleep(wait_time)
                wait_time *= 2

                continue
            else :

                raise requests.exceptions.JSONDecodeError("JSON解析错误,请检查网络") from json_decode_error


    if max_req_num == 0 :
        raise requests.exceptions.RequestException("请求次数过多,请稍后再试")
# ---





# 手写惰性类求值
# 手搓到一半发现原来Python3.12.8有内建的修饰器 >< 啊啊啊 现在是2026.10.14 5:49:42
# 不行了，熬穿了 ><
# 然后发现没什么用，就删了
# LazyData   R.I.P.




# 手写的查询自己的API
# 搞成调用接口叭

@ttl_cache()
def What_Is_IP (search: str | list | None = None) -> dict :
    """
    (除特殊标注,默认为 str ) // important

    search[ str | str : ip, bool : IsAutoPolling = True, int : SearchMaxTimes = 5 ]
    if search == None , 则查询本地IP

    Args:

    {
        ret // 200为正常    :    int

        data : 
        {

            ip // 查询的IP地址
            country // 国家/地区
            country_code // 国家/地区简码
            prov // 省份
            city // 城市
            city_code // 城市拼音
            city_short_code // 城市简码
            post_code // 邮政编码
            area_code // 电话区号
            isp // 运营商
            lng // 城市中心-经度
            lat // 城市中心-纬度
            long_ip // longip    :    int
            big_area // 国内大区划分

            // VIP 字段
            area // 区县
            ip_type // IP类型 [ISP:家庭用户] [BUS:企业专线] [IDC:机房/数据中心]
            ip_asn // AS号

        },
    
        qt // 查询时间-秒    :    int
    }
    """

    if search is None :
        data = get_ip_information()

    elif len(search) == 1 or type(search) == 'str':
        data = get_ip_information(search[0])

    elif len(search) == 3 and type(search) == 'list':
        data = get_ip_information(search[0], bool(search[1]), int(search[2]))

    else:
        raise TypeError(f'your {search} is must the formate of {What_Is_IP.__doc__}')

    return data
# ---



if __name__ == '__main__' :


    # print(What_Is_IP()['data'])
    # print(What_Is_IP()['data']['ip'])
    # print(What_Is_IP()['data']['city'])
    # print(What_Is_IP()['data']['long_ip'])
    # 成功,就不测试缓存了 !! ><

    pass
