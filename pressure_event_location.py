import db_manager
import global_conf_variables
from calc_methods import sum_calc, diff_calc, div_calc, mult_calc, get_minimum, cal_equ, convert_time, check_if_empty
import warnings

warnings.filterwarnings("ignore")

values = global_conf_variables.get_values()

# Constants
dist_pt1_to_pt2 = values[0]
dist_pt2_to_pt3 = values[1]
dist_pt3_to_pt4 = values[2]
LW_face_area = values[3]
shield_width = values[4]

vent_velocity = db_manager.pi_query_vent()

sensor_loc_1 = values[10]
sensor_loc_2 = values[11]
sensor_loc_3 = values[12]
sensor_loc_4 = values[13]

LW_face_area = LW_face_area  # m^2
shield_width = shield_width  # meters

# ventilation velocity from PI data, assumed same both directions
PW_to_TG = vent_velocity
PW_to_MG = vent_velocity

shield_no_pulse = []


def get_shield_no(pt1, pt2, pt3, pt4, pulse):
    if pulse == pt1:
        shield_no_pulse.append(sensor_loc_1)
    elif pulse == pt2:
        shield_no_pulse.append(sensor_loc_2)
    elif pulse == pt3:
        shield_no_pulse.append(sensor_loc_3)
    elif pulse == pt4:
        shield_no_pulse.append(sensor_loc_4)
    return shield_no_pulse


def fist_pulse(pt1, pt2, pt3, pt4):

    if pt1:
        pt_1 = convert_time(pt1[0])
        pt_2 = convert_time(pt2[0])
        pt_3 = convert_time(pt3[0])
        pt_4 = convert_time(pt4[0])
        fst_pulse = get_minimum(pt_1, pt_2, pt_3, pt_4)
        return fst_pulse, pt_1, pt_2, pt_3, pt_4
    else:
        pass


def second_pulse(fst_pulse, pt_1, pt_2, pt_3, pt_4):
    sec_pulse = []
    ops = {
        'second_pulse1': get_minimum(pt_2, pt_3, pt_4),
        'second_pulse2': get_minimum(pt_1, pt_3, pt_4),
        'second_pulse3': get_minimum(pt_2, pt_1, pt_4),
        'second_pulse4': get_minimum(pt_2, pt_3, pt_1)
    }

    if pt_1 == fst_pulse:
        sec_pulse.append(ops.get('second_pulse1'))
    elif pt_2 == fst_pulse:
        sec_pulse.append(ops.get('second_pulse2'))
    elif pt_3 == fst_pulse:
        sec_pulse.append(ops.get('second_pulse3'))
    elif pt_4 == fst_pulse:
        sec_pulse.append(ops.get('second_pulse4'))
    return sec_pulse[-1]


def third_pulse(fst_pulse, sec_pulse, pt_1, pt_2, pt_3, pt_4):
    thrd_pulse = []
    ops = {
        'third_pulse1': get_minimum(pt_3, pt_4),
        'third_pulse2': get_minimum(pt_3, pt_4),
        'third_pulse3': get_minimum(pt_1, pt_4),
        'third_pulse4': get_minimum(pt_1, pt_4),
        'third_pulse5': get_minimum(pt_1, pt_2),
        'third_pulse6': get_minimum(pt_2, pt_1)
    }

    if pt_1 == fst_pulse and pt_2 == sec_pulse:
        thrd_pulse.append(ops.get('third_pulse1'))
    elif pt_2 == fst_pulse and pt_1 == sec_pulse:
        thrd_pulse.append(ops.get('third_pulse2'))
    elif pt_2 == fst_pulse and pt_3 == sec_pulse:
        thrd_pulse.append(ops.get('third_pulse3'))
    elif pt_3 == fst_pulse and pt_2 == sec_pulse:
        thrd_pulse.append(ops.get('third_pulse4'))
    elif pt_3 == fst_pulse and pt_4 == sec_pulse:
        thrd_pulse.append(ops.get('third_pulse5'))
    elif pt_4 == fst_pulse and pt_3 == sec_pulse:
        thrd_pulse.append(ops.get('third_pulse6'))
    if thrd_pulse:
        return thrd_pulse[-1]
    else:
        pass


def fourth_pulse(fst_pulse, sec_pulse, thrd_pulse, pt_1, pt_2, pt_3, pt_4):
    if thrd_pulse:
        frth_pulse = []
        if pt_1 != fst_pulse and pt_1 != sec_pulse and pt_1 != thrd_pulse:
            frth_pulse.append(pt_1)
        elif pt_2 != fst_pulse and pt_2 != sec_pulse and pt_2 != thrd_pulse:
            frth_pulse.append(pt_2)
        elif pt_3 != fst_pulse and pt_3 != sec_pulse and pt_3 != thrd_pulse:
            frth_pulse.append(pt_3)
        elif pt_4 != fst_pulse and pt_4 != sec_pulse and pt_4 != thrd_pulse:
            frth_pulse.append(pt_4)
        return frth_pulse[-1]
    else:
        pass


def compute_location_case1(fst_1, sec_2, thrd_3, frth_4, shield_loc):
    if thrd_3 in thrd_3:
        # distance between pulse locations
        result_sum = sum_calc(dist_pt1_to_pt2, dist_pt2_to_pt3)

        # velocity of each pressure wave
        Vmg = div_calc(result_sum, diff_calc(frth_4, fst_1))
        vel_total = sum_calc(PW_to_TG, PW_to_MG)  # pressure wave to MG (headwind) and to TG (tailwind)
        Vtg = sum_calc(Vmg, vel_total)  # pressure_wave_vol tailgate m/s

        # Event location determination
        diff_to_SecNdandTailtGate = diff_calc(thrd_3, sec_2)
        total_vel = sum_calc(Vmg, Vtg)
        dist_diff = mult_calc(total_vel, diff_to_SecNdandTailtGate)

        # shield difference
        shield_diff = div_calc(dist_diff, shield_width)
        event_location = abs(diff_calc(shield_loc[0], shield_diff))
        return round(event_location), round(shield_diff, 2), shield_loc

    else:
        pass


def compute_location_case2(fst_1, sec_2, thrd_3, frth_4, shield_loc):
    if thrd_3 in thrd_3:
        # distance between pulse locations
        dist_from_mg = sum_calc(dist_pt1_to_pt2, dist_pt2_to_pt3)
        dist_from_tg = sum_calc(dist_pt3_to_pt4, dist_pt2_to_pt3)

        # velocity of each pressure wave
        vel_from_mg = div_calc(dist_from_mg, diff_calc(frth_4, sec_2))
        vel_from_tg = div_calc(dist_from_tg, diff_calc(thrd_3, fst_1))

        # velocities of veneration
        vel_vent_mg = sum_calc(vel_from_mg, PW_to_MG)
        vel_vent_tg = diff_calc(vel_from_tg, PW_to_TG)

        # total time of velocities
        total_vel = diff_calc(vel_vent_mg, vel_vent_tg)

        # solve for x
        x = cal_equ(total_vel, vel_from_mg, vel_from_tg, dist_pt2_to_pt3)

        # shield difference
        shield_diff_x = div_calc(x, shield_width)
        event_location_X = abs(sum_calc(shield_loc[0], abs(shield_diff_x)))

        # solve for y
        y = diff_calc(dist_pt2_to_pt3, x)
        shield_diff_y = div_calc(y, shield_width)
        return round(event_location_X), round(abs(shield_diff_x), 2), shield_loc
    else:
        pass


def main(pt1, pt2, pt3, pt4):

    try:
        fst_pulse, pt_1, pt_2, pt_3, pt_4 = fist_pulse(pt1, pt2, pt3, pt4)
        sec_pulse = second_pulse(fst_pulse, pt_1, pt_2, pt_3, pt_4)
        thrd_pulse = third_pulse(fst_pulse, sec_pulse, pt_1, pt_2, pt_3, pt_4)
        frth_pulse = fourth_pulse(fst_pulse, sec_pulse, thrd_pulse, pt_1, pt_2, pt_3, pt_4)

        pulse_list = [fst_pulse, sec_pulse, thrd_pulse, frth_pulse]
        loc_list = []

        for i in pulse_list:
            loc = get_shield_no(pt_1, pt_2, pt_3, pt_4, i)
            loc_list.append(loc)

        shield_loc = [loc_list[0][0], loc_list[0][1], loc_list[0][2], loc_list[0][3]]

        if not check_if_empty(shield_loc):
            a = diff_calc(sec_pulse, fst_pulse)
            b = diff_calc(thrd_pulse, fst_pulse)

            # when calculating Vmg and the denom is very small (when pulses 2 and 3 are very close together)
            # with a large nominator, makes a huge distance, so have to multiply
            if a < 1 and b < 1:
                location = compute_location_case1(fst_pulse, sec_pulse, thrd_pulse, frth_pulse, shield_loc)
            else:
                location = compute_location_case2(fst_pulse, sec_pulse, thrd_pulse, frth_pulse, shield_loc)
            return location
        else:
            print('no thrid')
            pass
    except Exception as e:
        pass
