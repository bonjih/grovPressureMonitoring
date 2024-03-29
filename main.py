###################################
#
#  - This scripts detects the location of a gas event coming out of the LW face.
#  - The resulting pressure wave >+/- 0.3kPa direction is tracked as it passes the MG and TG pressure sensors
#  - Waits 299 seconds between queries and queries the prior 300 seconds of values
#  - The results are recoded in the MAC database, table 'pulse_shield_locator'
#
# - Refer to the following Confluence page for the documentation:
#   https://anglo-data-analytics.atlassian.net/wiki/spaces/MAC/pages/45971144811/GRO+Differential+Pressure+Monitoring
#
# ##################################

import time

import config_parser
import db_manager
import get_PI_press_data
import global_conf_variables
import pressure_event_location
from calc_methods import check_if_empty, make_eventID, w_query_time, save_to_csv

now = time.strftime("%Y%m%d-%H%M%S")

pt1 = []
pt2 = []
pt3 = []
pt4 = []


def get_pulse_times(data):
    """
    defines the times of the first, second, third and fourth pules
    """
    for j in range(len(data)):
        time_event1 = data.at[j, 'TimeStampMG']
        diff_pressure_MG = data.at[j, 'PValuesMG']
        # time_event2 = data.at[j, 'TimeStampTG'] # todo
        diff_pressure_TG = data.at[j, 'PValuesTG']

        if diff_pressure_MG >= 0.3 and diff_pressure_TG < 0.3:
            save_to_csv(time_event1, 'location 1', now)
            pt1.append(time_event1)
        elif diff_pressure_TG >= 0.3 and diff_pressure_MG > -0.3 and diff_pressure_MG < 0.3:
            save_to_csv(time_event1, 'location 2', now)
            pt2.append(time_event1)
        elif diff_pressure_MG <= -0.3 < diff_pressure_TG < 0.3:
            save_to_csv(time_event1, 'location 3', now)
            pt3.append(time_event1)
        elif diff_pressure_TG <= -0.3 < diff_pressure_MG:
            save_to_csv(time_event1, 'location 4', now)
            pt4.append(time_event1)


def db_manager_controller(dbfields, event_id, shielddiff, eventlocation, shieldloc, vent_velocity):
    """
    calls db_manager, with event data
    """
    value = global_conf_variables.get_values()  # db creds

    event_data = int(event_id), shielddiff, eventlocation, pt1, pt2, pt3, pt4, shieldloc[0][0], shieldloc[0][1], \
                 shieldloc[0][2], shieldloc[0][3], vent_velocity[1:]

    sql = db_manager.SQL(value[5], value[6], value[7], value[8], value[9])
    exists = sql.check_entry_exist(event_id)
    if not exists:
        print(f'Event detected id: [{event_id}] at {pt2[0]}')  # todo add case when pt1 etc not empty
        sql.insert(event_data, dbfields)
    else:
        pass


if __name__ == "__main__":
    """
    In a forever loop, querying PI every 60 seconds
    The PI queries take the last 5 mins of data to analyse
    """
    try:
        time_q = []

        while True:
            start_time = time.time()
            df = get_PI_press_data.pi_query_pressure()

            # a check to find average query times
            q_time = time.time() - start_time
            time_q.append(q_time)
            q_time = int(time_q[-1])
            if q_time > 30:
                w_query_time(time_q)

            get_pulse_times(df)

            # if pt1 -> pt4 is empty
            list_of_lists = [pt1, pt2, pt3, pt4]
            result = check_if_empty(list_of_lists)

            if not result:
                event_location, shield_diff, shield_loc, v_velocity = pressure_event_location.main(pt1, pt2, pt3, pt4)
                event_id = make_eventID(pt1, pt2, pt3, pt4)
                db_fields = config_parser.db_json_parser()
                db_manager_controller(db_fields, event_id, shield_diff, event_location, shield_loc, v_velocity)
                pressure_event_location.shield_no_pulse.clear()
            time.sleep(299)  # wait for 299 seconds before another query
            time_q.clear()
            pt1.clear(), pt2.clear(), pt3.clear(), pt4.clear()
    except Exception as e:
        if KeyError:
            pass
