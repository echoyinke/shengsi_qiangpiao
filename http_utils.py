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
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'authentication': account['authentication'],
    'token': 'undefined'
}


def send_dingtalk(content):
    url = cf['dingtalk_url']
    content = cf['dingtalk_keyword'] + content
    payload = json.dumps({"msgtype": "text","text": {"content": content}})
    headers = {
        'Content-Type': 'application/json'
    }
    res = requests.request("POST", url, headers=headers, data=payload)
    print(res)

def token_check(token):
    url = "https://pc.ssky123.com/api/v2/user/tokenCheck"
    payload = {}
    headers['token'] = token
    response = requests.request("GET", url, headers=headers, data=payload)
    return "成功" in response.text


def get_token():
    with open('./token_cache.txt', 'r') as file:
        token = file.read()
    token_ok = token_check(token)
    if token_ok:
        return token
    url = 'https://pc.ssky123.com/api/v2/user/passLogin?phoneNum=' + account['phoneNum'] + '&passwd=' + account[
        'passwd'] + '&deviceType=3'
    response = requests.request("POST", url, headers=headers)
    token = json.loads(response.text)['data']["token"]
    with open('./token_cache.txt', 'w', encoding='UTF-8') as file:
        file.write()
    return token


def query_enq(startPortNo, endPortNo, start_date, token):
    payload = {
        "startPortNo": startPortNo,
        "endPortNo": endPortNo,
        "startDate": start_date,
        "accountTypeId": "0"}
    url = "https://pc.ssky123.com/api/v2/line/ship/enq"
    headers['token'] = token
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response


def save_seats(sailDate, token):
    import requests
    url = "https://pc.ssky123.com/api/v2/holding/save"
    payload = {"accountTypeId": "0", "userId": "620595", "buyTicketType": 1, "contactNum": "17521080261",
               "lineNum": 1775, "lineName": "南浦至嵊泗", "lineNo": 24031, "shipName": "舟桥6轮", "startPortNo": 46,
               "startPortName": "上海(南浦)", "endPortNo": 17, "endPortName": "嵊泗(枸杞)", "sailDate": sailDate,
               "sailTime": "09:40", "lineDirect": 1, "totalFee": 342, "totalPayFee": 342, "sx": 0,
               "orderItemRequests": [
                   {"passName": "孙桂芝", "credentialType": 1, "passId": 5077047, "seatClassName": "上舱",
                    "seatClass": 31, "ticketFee": 114, "realFee": 114, "freeChildCount": 0, "passType": 1},
                   {"passName": "尹珂", "credentialType": 1, "passId": 3593485, "seatClassName": "上舱",
                    "seatClass": 31, "ticketFee": 114, "realFee": 114, "freeChildCount": 0, "passType": 1},
                   {"passName": "刘妍", "credentialType": 1, "passId": 3593483, "seatClassName": "上舱",
                    "seatClass": 31, "ticketFee": 114, "realFee": 114, "freeChildCount": 0, "passType": 1}],
               "busStartTime": "07:30", "clxm": "客滚船", "clxh": 5, "hxlxh": 0, "hxlxm": "正常航班", "bus": 92,
               "bus2": 0, "dwh": 23}

    headers['token'] = token
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    print(response.text)


def res_seats(token):
    url = "https://pc.ssky123.com/api/v2/query/holding/res"
    payload ={}
    headers['token'] = token
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
