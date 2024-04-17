import argparse
import json
import os

import requests
import yaml

fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config_local.yaml')
cf = yaml.load(open(yamlPath, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)

# flagOptions > yaml
parser = argparse.ArgumentParser(usage=" option can coverage .yaml ", description="")
parser.add_argument("-f", "--from", default=cf['From'], help="出发站", dest="sfrom")
parser.add_argument("-t", "--to", default=cf['To'], help="到达站", dest="to")
parser.add_argument("-d", "--date", default=cf['Date'], help="订票日期", dest="date")
parser.add_argument("-lbt", "--lbt", default=cf['Customization']['LatestBusTime'], help="最晚开车时间", dest="lbt")
parser.add_argument("-lst", "--lst", default=cf['Customization']['LatestShipTime'], help="最晚开船时间", dest="lst")
parser.add_argument("-mst", "--mst", default=cf['Customization']['MinShipTime'], help="最早开船时间", dest="mst")
parser.add_argument("-line", "--line", default=cf['Customization']['LineNum'], help="指定航班", dest="line")
parser.add_argument("-class", "--class", default=cf['Customization']['Class'], help="指定舱位", dest="className")
args = parser.parse_args()

account = {
    'phoneNum': cf['User']['mobile'],
    'passwd': cf['User']['password'],
    'authentication': cf['User']['authentication'],
    'passengers': [],
    'seatNeed': 0,
}


def login4token():
    url = 'https://pc.ssky123.com/api/v2/user/passLogin?phoneNum=' + account['phoneNum'] + '&passwd=' + account[
        'passwd'] + '&deviceType=3'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'authentication': '1713335172620595',
        'token': 'undefined'
    }
    response = requests.request("POST", url, headers=headers)
    return json.loads(response.text)['data']["token"]


def query_enq(payload, authentication, token):
    url = "https://pc.ssky123.com/api/v2/line/ship/enq"

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'authentication': authentication,
        'token': token
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    return response
