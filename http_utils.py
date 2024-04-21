import argparse
import json
import os

import requests
import yaml

fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config_local.yaml')
cf = yaml.load(open(yamlPath, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)

account = {
    'phoneNum': cf['User']['mobile'],
    'passwd': cf['User']['password'],
    'authentication': cf['User']['authentication'],
    'passengers': [],
    'seatNeed': 0,
}


def send_dingtalk(content):
    url = cf['dingtalk_url']
    content = cf['dingtalk_keyword'] + content
    payload = json.dumps({
        "msgtype": "text",
        "text": {
            "content": content
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }
    res = requests.request("POST", url, headers=headers, data=payload)
    print(res)


def read_token_cache():
    with open('./token_cache.txt', 'r') as file:
        content = file.read()  # 读取整个文件内容
    return content


def write_token_cache(token):
    with open('./token_cache.txt', 'w', encoding='UTF-8') as file:
        file.write()  # 读取整个文件内容


def token_check(token):
    url = "https://pc.ssky123.com/api/v2/user/tokenCheck"
    payload = {}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',

        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'authentication': '1713686372620595',
        'token': token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return "成功" in response.text


def get_token():
    token = read_token_cache()
    token_ok = token_check(token)
    if token_ok:
        return token
    url = 'https://pc.ssky123.com/api/v2/user/passLogin?phoneNum=' + account['phoneNum'] + '&passwd=' + account[
        'passwd'] + '&deviceType=3'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'authentication': '1713335172620595',
        'token': 'undefined'
    }
    response = requests.request("POST", url, headers=headers)
    token = json.loads(response.text)['data']["token"]
    write_token_cache(token)
    return token


def query_enq(startPortNo, endPortNo, start_date , authentication, token):
    payload = {
        "startPortNo": startPortNo,
        "endPortNo": endPortNo,
        "startDate": start_date,
        "accountTypeId": "0"}
    url = "https://pc.ssky123.com/api/v2/line/ship/enq"

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'authentication': authentication,
        'token': token
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    return response
