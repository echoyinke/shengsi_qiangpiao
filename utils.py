import time
import datetime
import logging
logging.basicConfig(level=logging.INFO)
def time_ahead_sale(sail_date):
    """计算当前时间到目标日期6点半的秒数，以便休眠到该时间点"""
    now = datetime.datetime.now()
    sail_date=datetime.datetime.strptime(sail_date, '%Y-%m-%d').date()
    # 提前5天放票（也有时候7天放票不确定，deprecated）
    start_qiangpiao_date=sail_date - datetime.timedelta(days=4)
    start_datetime = datetime.datetime.combine(start_qiangpiao_date, datetime.time(6, 50))
    return (start_datetime - now).total_seconds()


def get_next_check_time():
    """计算下一次检查时间的间隔（秒）"""
    now = datetime.datetime.now()
    start_time = now.replace(hour=6, minute=50, second=0, microsecond=0)
    end_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

    # 如果当前时间早于今天的放票开始时间
    if now < start_time:
        return (start_time - now).total_seconds()
    # 如果当前时间晚于今天的放票结束时间，则等待到明天的放票开始时间
    elif now > end_time:
        tomorrow_start_time = start_time + datetime.timedelta(days=1)
        return (tomorrow_start_time - now).total_seconds()
    # 如果当前时间在放票时间范围内
    else:
        return 0
