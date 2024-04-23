import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)
def time_ahead_sale(sail_date):
    """计算当前时间到目标日期6点半的秒数，以便休眠到该时间点"""
    now = datetime.datetime.now()
    sail_date=datetime.datetime.strptime(sail_date, '%Y-%m-%d').date()
    # 提前5天放票
    start_qiangpiao_date=sail_date - datetime.timedelta(days=4)
    start_datetime = datetime.datetime.combine(start_qiangpiao_date, datetime.time(6, 50))
    return (start_datetime - now).total_seconds()
