import pandas as pd
import sqlalchemy as sal
import pyodbc
from sqlalchemy import create_engine

import datetime
import warnings

warnings.filterwarnings("ignore")
current_dateTime = datetime.datetime.now()

# get last 5 seconds of events
x = 5
result = datetime.datetime.now() - datetime.timedelta(seconds=x)


def PI_connect():
    conn = pyodbc.connect(
        "Driver=PI SQL Client; AF Server=AISGROOSI01; AF Database='Grosvenor MAC'; Integrated Security=SSPI;",
        autocommit=True)
    return conn


pressureMG = "Differential pressure reading MG"
pressureTG = "Differential pressure reading TG"


# gets last ventilation velocity value
def pi_query_vent():
    conn = PI_connect()

    select = f'''
                SELECT a.TimeStamp
                ,a.Value_Double
                FROM Element.Element e
                inner join Element.Attribute ea ON ea.ElementID = e.ID
                inner join Element.Archive a ON a.AttributeID = ea.ID
                inner join Element.ElementHierarchy eh ON eh.ElementID = ea.ElementID
                WHERE e.Name in ('Pressure Monitoring')
                and ea.name in ('Ventillation Velocity')
                and a.TimeStamp > '{current_dateTime}'
                '''
    df = pd.read_sql(select, conn)
    df = df.iloc[-1:]
    df = df['Value_Double']
    return df.to_string()[7:]


def PI_values_query():
    frames = []
    att_lst = [pressureMG, pressureTG]

    for i in att_lst:
        conn = PI_connect()
        select = f'''
                    SELECT a.TimeStamp
                    ,a.Value_Double
                    FROM Element.Element e
                    inner join Element.Attribute ea ON ea.ElementID = e.ID
                    inner join Element.Archive a ON a.AttributeID = ea.ID
                    inner join Element.ElementHierarchy eh ON eh.ElementID = ea.ElementID
                    WHERE e.Name in ('Pressure Monitoring')
                    and ea.name in ('{i}')
                    and a.TimeStamp between '{result}' and '{current_dateTime}'
                    '''
        df = pd.read_sql(select, conn)
        # df = df.iloc[-1:]
        df['Field_Name'] = i

        frames.append(df)
    return frames


def make_PI_frame():
    try:
        frames = PI_values_query()
        df2 = pd.concat(frames)

        mg = df2.loc[df2['Field_Name'].isin(['Differential pressure reading MG'])]
        tg = df2.loc[df2['Field_Name'].isin(['Differential pressure reading TG'])]
        mg.rename(columns={'TimeStamp': 'TimeStampMG', 'Value_Double': 'PValuesMG'}, inplace=True)
        mg = mg.drop('Field_Name', axis=1)
        tg.rename(columns={'TimeStamp': 'TimeStampTG', 'Value_Double': 'PValuesTG'}, inplace=True)
        tg = tg.drop('Field_Name', axis=1)
        df3 = pd.concat([mg, tg], axis=1)
        df3.to_csv('./test_data/8_sec_events.csv', sep=',', encoding='utf-8', index=False)
        return df3
    except Exception as e:
        print(f'Most likely a PI query time out: {e}')
