import logging

from http_utils import *
from utils import *


fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config_local.yaml')
cf = yaml.load(open(yamlPath, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)
startPortNo=cf['PortNo']['gouqi']
endPortNo=cf['PortNo']['nanpu']
sail_date="2024-05-04"
seats_need=3
seat_class_priority=["上舱","商务舱","中舱", "下舱", "三等舱", "普舱"]
depart_as_later_as_posible=False
need_order=False
logging.info(f"Starting shengsi qiangpiao script{startPortNo} 到 {endPortNo} on {sail_date} ...")

n=0


def pick_sail(sails):
    available_seat_info = ""
    if depart_as_later_as_posible:
        data = sorted(sails, key=lambda x: x['sailTime'], reverse=True)
    for sail in sails:
        seatClasses = sorted(sail['seatClasses'], key=lambda x: seat_class_priority.index(x['className']) if x['className'] in seat_class_priority else len(seat_class_priority))
        for seatClass in seatClasses:
            if seatClass['pubCurrentCount'] >= seats_need:
                available_seat_info += f"{seatClass['className']} 空余 {seatClass['pubCurrentCount']};"
                content = f"{sail['startPortName']} 到 {sail['endPortName']} {sail['sailDate']}  {sail['sailTime']} " + available_seat_info
                send_dingtalk(content)
                sail['seatClasses'][:] = []
                sail['seatClasses'].append(seatClass)
                return sail
    return None
while True:
    need_wait_time = get_next_check_time()
    if True or need_wait_time == 0:
        time.sleep(1)
        n+=1
        logging.info(f"Trying qiangpiao {n} times ...")
        token=get_token()
        res = query_enq(startPortNo,endPortNo, sail_date , token=token)
        response=json.loads(res.text)
        # failed fast
        if response['data'] is None:
            logging.info(f"Response data is None/Empty , {res.text}\n")
            continue
        # core logic
        sails=response['data']
        sail=pick_sail(sails)
        if need_order and sail is not None:
            order_id=save_seats(sail_date=sail_date, line_no=sail['lineNo'], token=token)
            if order_id is not None:
                send_dingtalk("抢票成功！！！请尽快前往支付")
                break
    else:
        # 不在放票时间内，等待到下一个放票时间
        logging.info(f"Not in ticket sale window. Next check at {datetime.datetime.now() + datetime.timedelta(seconds=need_wait_time)}")
        time.sleep(need_wait_time)



