import logging

from http_utils import *
from utils import *


fileNamePath = os.path.split(os.path.realpath(__file__))[0]
yamlPath = os.path.join(fileNamePath, 'config_local.yaml')
cf = yaml.load(open(yamlPath, 'r', encoding='utf-8').read(), Loader=yaml.FullLoader)
startPortNo=cf['PortNo']['nanpu']
endPortNo=cf['PortNo']['gouqi']
sail_date="2024-05-01"


logging.info(f"Starting shengsi qiangpiao script{startPortNo} 到 {endPortNo} on {sail_date} ...")

n=0
while True:
    need_wait_time = get_next_check_time()
    if need_wait_time == 0:
        n+=1
        logging.info(f"Trying qiangpiao {n} times ...")
        token=get_token()
        res = query_enq(startPortNo,endPortNo, sail_date , token=token)
        response=json.loads(res.text)
        # failed fast
        if response['data'] is None:
            logging.info(f"Response data is None/Empty , {res.text}\n")
            time.sleep(1)
            continue
        # core logic
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
            if order_id is not None:
                send_dingtalk("抢票成功！！！请尽快前往支付")
                break
    else:
        # 不在放票时间内，等待到下一个放票时间
        logging.info(f"Not in ticket sale window. Next check at {datetime.datetime.now() + datetime.timedelta(seconds=need_wait_time)}")
        time.sleep(need_wait_time)



