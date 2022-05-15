import re
import requests
import json
requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1)"
def htmlspecialchars(content):
    return content.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&#039;").replace("<", "&lt;").replace(">", "&gt;")
def format(url):
    return url.replace("/playwm/", "/play/")
def get_link(url):
    id=parse_id(url)
    key=""#self::get_key($id);
    api = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids="+id+"&dytk="+key
    res=get(api)
    try:
        data=json.loads(res)
        return format(data['item_list'][0]['video']['play_addr']['url_list'][0])
    except:
       raise Exception("Douyin: Get Link Failed")
def get_key(url):
    res=get(url, timeout=30)
    res=htmlspecialchars(res)
    find=re.findall('(?<=dytk: ")[^"]+')
    if len(find)>0:
        return find[0][0]
    return None

def get_video(id, simple=False):
    id=parse_id(id)
    if not id: raise Exception("No Video ID")
    url='https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='+id
    res=get(url)
    try:
        data=json.loads(res)
        if not data or data['status_code']!=0: raise Exception("Douyin: No Video Data")
        data=data['item_list'][0]
        if not simple: 
            arr = data
        else:
            arr={}
        arr['url'] =format(data['video']['play_addr']['url_list'][0])
        arr['title']=data['desc']
        return arr
    except Exception as e:
        raise Exception("Douyin: Parse URL Failed")

def parse_id(url):
    if (re.search("^\d+$", url)):
        return url
    match = re.search("(\/share)?\/video\/([^\/\?]+)", url)
    if match:
        return match.group(2)
    last=requests.Request("GET", url).url
    match = re.search("(\/share)?\/video\/([^\/\?]+)", last)
    if match:
        return match.group(2)
    return None
def get_data(url, limit=10):
    if not (limit>=0): limit=10
    res=get(url)
    data=json.loads(res)
    if not data or "billboard_data" not in data: raise Exception("No Tiktok Data")
    list=[]
    cnt=0
    for extra in data['billboard_data']:
        if "extra_list" in extra:
            for item in extra['extra_list']:
                i={
                    'title':item['title'],
                    'url':item['link'],
                    'thumbnail':item['img_url'],
                }
                list.append(i)
                cnt+=1
                if limit>0 and cnt>=limit: 
                    return list
        else:
            i={
                'title':extra['title'],
                'url':extra['link'],
                'thumbnail':extra['img_url'],
            }
            list.append(i)
            cnt+=1
            if limit>0 and cnt>=limit: 
                return list
    return list
def get(url, data="", timeout=30):
    with requests.request("GET", url, timeout=timeout, 
    headers={
        "referer": "https://creator.douyin.com/billboard/hot_aweme",
        "User-Agent": user_agent
    }, verify=False) as con:
        res=con.text
        return res
