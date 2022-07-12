from datetime import datetime


def diff_calc(a, b):
    return float(a) - float(b)


def div_calc(a, b):
    return float(a) / float(b)


def sum_calc(a, b):
    return float(a) + float(b)


def mult_calc(a, b):
    return float(a) * float(b)


def convert_time(time_str):
    a = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S.%f")
    b = a.strftime("%H:%M:%S.%f")
    return b[6:]


def get_minimum(*kwargs):
    return min(kwargs)


def cal_equ(total_vel, vel_vent_mg, vel_vent_tg, const):
    a = (const / vel_vent_tg / const) + (1 / vel_vent_mg)
    b = (total_vel - const / vel_vent_tg)
    return b / a


def make_eventID(fst_pulse):
    return fst_pulse[2:4] + fst_pulse[5:7] + fst_pulse[5:7]


def invalid_op(x):
    raise Exception("Invalid operation")
