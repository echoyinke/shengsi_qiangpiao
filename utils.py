import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)
def time_ahead_sale(target_date):
    """计算当前时间到目标日期6点半的秒数，以便休眠到该时间点"""
    now = datetime.datetime.now()
    start_datetime = datetime.datetime.combine(target_date, datetime.time(6, 50))
    return (start_datetime - now).total_seconds()
