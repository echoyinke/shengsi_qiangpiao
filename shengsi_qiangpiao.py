from http_utils import *
import logging
logging.basicConfig(level=logging.INFO)

fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config_local.yaml')
cf = yaml.load(open(yamlPath, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)
startPortNo=cf['PortNo']['nanpu']
endPortNo=cf['PortNo']['gouqi']
sail_date="2024-04-25"

logging.info(f"Starting shengsi qiangpiao {startPortNo} 到 {endPortNo} on {sail_date} ...")

while True:
    token=get_token()
    res = query_enq(startPortNo,endPortNo, sail_date , token=token)
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
            order_id=save_seats(sail_date=sail_date, line_no=info['lineNo'], token=token)
            reserve_response=res_seats(order_id, token) # 貌似不必要
            if "成功" in reserve_response:
                send_dingtalk("抢票成功！！！请尽快前往支付")
                break