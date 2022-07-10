import calc_methods
import config_parser
import db_manager
import global_conf_variables
import pressure_event_location

import pandas as pd

values = global_conf_variables.get_values()
sensor_loc_1 = values[10]
sensor_loc_2 = values[11]
sensor_loc_3 = values[12]
sensor_loc_4 = values[13]

# Note: assumes air flow always moves from maingate to tailgate

pt1 = []
pt2 = []
pt3 = []
pt4 = []


def get_pulse_location(data):
    # defines the times of the first, second, third and fourth pules
    for j in range(len(data)):
        time_event1 = data.at[j, 'Time stamp']
        diff_pressure_MG = data.at[j, 'MG test value event 1']
        # time_event2 = data.at[j, 'Time stamp2']
        diff_pressure_TG = data.at[j, 'TG test value event 1']

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


def db_manager_controller(dbfields, shielddiff, eventlocation, event_id=111):
    fstPulse = calc_methods.get_minimum(pt1, pt2, pt3, pt4)
    values = global_conf_variables.get_values()  # get db creds
    event_data = event_id, shielddiff, eventlocation, pt1[0], pt2[0], pt3[0], pt4[0], sensor_loc_1, sensor_loc_2, \
                 sensor_loc_3, sensor_loc_4, fstPulse

    sql = db_manager.SQL(values[6], values[7], values[8], values[9])  # db creds
    sql.image_data(event_data, dbfields)


if __name__ == "__main__":
    #df = './test_data/LW pressure event sample data_210826.csv'
    df = './test_data/LW pressure event sample data_211204 - Copy.csv'
    # parsedates = lambda x: datetime.strptime(x, '%M:%S.%f')
    df = pd.read_csv(df)

    get_pulse_location(df)
    event_location, shield_diff = pressure_event_location.main(pt1, pt2, pt3, pt4)
    db_fields = config_parser.db_json_parser()
    db_manager_controller(db_fields, shield_diff, event_location)
