from http_utils import *

fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config_local.yaml')
cf = yaml.load(open(yamlPath, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)
startPortNo=cf['PortNo']['nanpu']
endPortNo=cf['PortNo']['gouqi']
start_date="2024-04-25"

token=get_token()

res = query_enq(startPortNo,endPortNo, start_date , token=token)
response=json.loads(res.text)
if len(response['data']) > 0:
    info=response['data'][0]
    available_seat_info=""
    seatClasses = info['seatClasses']
    for seatClass in seatClasses:
        if seatClass['pubCurrentCount'] > 0:
            available_seat_info += f"{seatClass['className']} 空余 {seatClass['pubCurrentCount']};"
    if available_seat_info !='':
        content = f"{info['startPortName']} 到 {info['endPortName']} {info['sailDate']}  {info['sailTime']} " + available_seat_info
        send_dingtalk(content)