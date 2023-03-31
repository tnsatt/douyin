import json
import os
import re
import sys
from urllib.parse import urlparse

import requests
from py_mini_racer import MiniRacer

requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

cookie = None
# cookie = "s_v_web_id=verify_legxn6eq_fBNVLyxg_Hrat_4Ld8_8baF_NeB9RM5LcqHg"
user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1)"


def genxbogus(query, ua):
    ctx = MiniRacer()
    file = os.path.dirname(__file__) + "/res/X-Bogus.js"
    with open(file, "r") as fp:
        code = fp.read()
        # execjs.compile(code).call('sign', query, ua)
        # js2py.eval_js6(code)
        js = "\nsign('{}', '{}')".format(query, ua)
        res = ctx.eval(code + js)
        return res


def get_data(url):
    id = parse_id(url)
    if not id:
        raise Exception("No Douyin ID")
    # api = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + id
    api = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={id}&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1344&screen_height=756&browser_language=zh-CN&browser_platform=Win32&browser_name=Firefox&browser_version=110.0&browser_online=true&engine_name=Gecko&engine_version=109.0&os_name=Windows&os_version=10&cpu_core_num=16&device_memory=&platform=PC&webid=7158288523463362079&msToken=abL8SeUTPa9-EToD8qfC7toScSADxpg6yLh2dbNcpWHzE0bT04txM_4UwquIcRvkRb9IU8sifwgM1Kwf1Lsld81o9Irt2_yNyUbbQPSUO8EfVlZJ_78FckDFnwVBVUVK"
    p = urlparse(api)
    q = genxbogus(p.query, user_agent)
    api = api + "&X-Bogus=" + q
    headers = {
        "Referer": "https://www.douyin.com/",
        "User-Agent": user_agent,
    }
    if cookie:
        headers["Cookie"] = cookie
    with requests.get(api, headers=headers, verify=False) as req:
        res = req.text
        data = json.loads(res)
        if not data:
            raise Exception("Douyin: No Data")
        data["url"] = find_url(data["aweme_detail"])
        data["title"] = data["aweme_detail"]["desc"]
        return data


def parse_id(url):
    if re.search("^\d+$", url):
        return url
    pattern = "((\/share)?\/video|\/note)\/([^\/\?]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(3)
    with requests.get(url, verify=False) as req:
        last = req.url
        match = re.search(pattern, last)
        if match:
            return match.group(3)
        return None


def find_url(data):
    if "images" in data and data["images"]:
        arr = []
        for i in data["images"]:
            ok = False
            for u in i["url_list"]:
                if ".webp" in u:
                    continue
                arr.append(u)
                ok = True
                break
            if not ok:
                arr.append(i["url_list"][0])
        return arr
    # try:
    #     uri = data['video']['play_addr']['uri']
    #     return f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"
    # except:
    #     pass
    return format(data["video"]["play_addr"]["url_list"][0])


def get_link(url):
    data = get_data(url)
    return data["url"]


def get(url, data="", timeout=30):
    with requests.request(
        "GET",
        url,
        timeout=timeout,
        headers={
            "referer": "https://creator.douyin.com/billboard/hot_aweme",
            "User-Agent": user_agent,
        },
        verify=False,
    ) as con:
        res = con.text
        return res


def htmlspecialchars(content):
    return (
        content.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format(url):
    return url.replace("/playwm/", "/play/")


def get_key(url):
    res = get(url, timeout=30)
    res = htmlspecialchars(res)
    find = re.findall('(?<=dytk: ")[^"]+')
    if len(find) > 0:
        return find[0][0]
    return None


def err(e):
    print(e, file=sys.stderr)
