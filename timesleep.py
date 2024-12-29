from datetime import datetime, timedelta
import random

# with open('calendar2024.txt') as f:
#     hol = [el.replace('\n', '') for el in f.readlines()]

hol = []

def time_to_sleep_f(timeout = 180):
    beg_tm, end_time = 8, 23
    dt_tm = datetime.now()
    dt_tm_00 = dt_tm.replace(hour=0, minute=0, second=0, microsecond=0)
    if dt_tm.date().strftime("%Y.%m.%d") in hol:
        nexttime = dt_tm_00 + timedelta(days=1, hours=beg_tm, minutes=int(13 * (1 - random.uniform(0, 0.5))))
    elif dt_tm.time().hour < beg_tm:
        nexttime = dt_tm_00 + timedelta(hours=beg_tm, minutes=int(13 * (1 - random.uniform(0, 0.5))))
    elif dt_tm.time().hour >= end_time:
        nexttime = dt_tm_00 + timedelta(days=1, hours=beg_tm, minutes=int(13 * (1 - random.uniform(0, 0.5))))
    else:
        nexttime = dt_tm + timedelta(seconds=timeout * (1 - random.uniform(0, 0.5)))
    time_to_sleep = nexttime - dt_tm
    return nexttime, time_to_sleep, int(time_to_sleep.total_seconds())

        # nexttime, tmts_time, tmts_sec = time_to_sleep_f(timeout = 40*60)
        # logging.info(f'nexttime: {nexttime}, tmts_time: {tmts_time}, tmts_sec: {tmts_sec}')
        # time.sleep(tmts_sec)