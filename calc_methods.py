from datetime import datetime
import time
import pandas as pd

start_time = time.time()


def div_calc(a, b):
    return float(a) / float(b)


def convert_time(time_str):
    a = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    b = a.strftime("%H:%M:%S.%f")
    return b


def strip_zeros(num):
    out = num.lstrip('0')
    out = float(out)
    return out


def cal_equ(total_vel, vel_vent_mg, vel_vent_tg, const):
    a = (const / vel_vent_tg / const) + (1 / vel_vent_mg)
    b = (total_vel - const / vel_vent_tg)
    return b / a


def remove_zero_from_list(lst):
    result = [x for x in lst if x != 0]
    return result


def w_query_time(q_time):
    TimeStamp = datetime.now()
    df = pd.DataFrame([TimeStamp, q_time[-1]])
    df = df.transpose()
    df.columns = ['TimeStamp', 'pi_query_pressure_time']
    df.to_csv('query_greater_30sec.csv', mode='a', index=False)


def convert_to_int(*kwargs):
    result = [(float(x)) for x in kwargs]
    return result


def check_if_empty(list_of_lists):
    return all([not elem for elem in list_of_lists])


def invalid_op(x):
    raise Exception("Invalid operation")


def make_eventID(pt1, pt2, pt3, pt4):
    if pt1:
        pt1 = ' '.join(pt1)
        return pt1[2:4] + pt1[5:7] + pt1[8:10]
    if pt2:
        p2 = ' '.join(pt2)
        return p2[2:4] + p2[5:7] + p2[8:10]


def clear_list(lst):
    lst.clear()