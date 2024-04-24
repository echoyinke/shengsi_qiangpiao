import argparse
import json
import os
import logging
import time

import requests
import yaml
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

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
    'Content-Type': 'application/json;charset=UTF-8',
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
        file.write(token)
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


def save_seats(sail_date,line_no, token):
    import requests
    url = "https://pc.ssky123.com/api/v2/holding/save"
    with open('./save_seats_payload_local.json', 'r', encoding='utf-8') as file:
        payload = json.load(file)
    payload['sailDate']=sail_date
    payload['lineNo']=line_no
    headers['token'] = token
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    try:
        order_id = json.loads(response.text)['data']["orderId"]
    except Exception as e:
        logging.info(f"Encounter ex:{e}, response text is: {response.text}")
        time.sleep(1)
        return None
    return order_id

def res_seats(order_id, token):
    url = "https://pc.ssky123.com/api/v2/query/holding/res"
    payload = {"orderId":order_id}
    headers['token'] = token
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response.text
