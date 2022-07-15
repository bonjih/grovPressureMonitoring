import time
import pandas as pd

import calc_methods
import config_parser
import db_manager
import global_conf_variables
import pressure_event_location
import get_PI_press_data

start_time = time.time()

values = global_conf_variables.get_values()

# Note: assumes air flow always moves from maingate to tailgate

pt1 = []
pt2 = []
pt3 = []
pt4 = []


def get_pulse_times(data):
    # defines the times of the first, second, third and fourth pules
    for j in range(len(data)):
        time_event1 = data.at[j, 'TimeStampMG']
        diff_pressure_MG = data.at[j, 'PValuesMG']
        # time_event2 = data.at[j, 'TimeStampTG']
        diff_pressure_TG = data.at[j, 'PValuesTG']

        try:
            # pulse at location 1
            if diff_pressure_MG >= 0.300 and diff_pressure_TG < 0.300:
                pt1.append(time_event1)
            # pulse at location 2
            elif diff_pressure_TG >= 0.300 and diff_pressure_MG > -0.300 and diff_pressure_MG < 0.300:
                pt2.append(time_event1)
            # pulse at location 3
            elif diff_pressure_MG <= -0.300 < diff_pressure_TG < 0.300:
                pt3.append(time_event1)
            # pulse at location 4
            elif diff_pressure_TG <= -0.300 < diff_pressure_MG:
                pt4.append(time_event1)
        except Exception as e:
            pass


def db_manager_controller(dbfields, shielddiff, eventlocation, shieldloc):
    event_id = calc_methods.make_eventID(' '.join(pt1))
    vent_velocity = db_manager.pi_query_vent()
    values = global_conf_variables.get_values()  # db creds

    event_data = int(event_id), shielddiff, eventlocation, pt1[0], pt2[0], pt3[0], pt4[0], shieldloc[0][0], \
                 shieldloc[1][1], shieldloc[2][2], shieldloc[3][3], float(vent_velocity[1:])

    sql = db_manager.SQL(values[5], values[6], values[7], values[8], values[9])
    exists = sql.check_entry_exist(event_id)
    if not exists:
        sql.insert(event_data, dbfields)
    else:
        print(f"Event [{event_id}] already in the database, skipping....")


if __name__ == "__main__":
    while True:
        time.sleep(1)
        try:
            #df = './test_data/LW pressure event sample data_210826.csv'
            #df = pd.read_csv(df)
            df = get_PI_press_data.makePI_frame()
            # for some reason df.isnull().any() did not resolve to True wih a NaN
            # check_null = df['PValuesMG'].iloc[0]
            get_pulse_times(df)

            # to ensure only send data to db if conditions in get_pulse_location are met
            list_of_lists = [pt1, pt2, pt3, pt4]
            result = calc_methods.check_if_empty(list_of_lists)

            if not result:
                event_location, shield_diff, shield_loc = pressure_event_location.main(pt1, pt2, pt3, pt4)
                db_fields = config_parser.db_json_parser()
                db_manager_controller(db_fields, shield_diff, event_location, shield_loc)
                pressure_event_location.shield_no_fst_pulse.clear()
                print('Event detected')
                print(event_location)

            else:
                print('No event detected')

        except Exception as e:
            print(e)

        # print(time.time() - start_time)
