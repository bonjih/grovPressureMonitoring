import pyodbc
import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")
current_date = datetime.date(datetime.now())


def PI_connect():
    conn = pyodbc.connect(
        "Driver=PI SQL Client; AF Server=AISGROOSI01; AF Database='Grosvenor MAC'; Integrated Security=SSPI;",
        autocommit=True)
    cursor = conn.cursor()
    return cursor, conn


pressureMG = "Differential pressure reading MG"
pressureTG = "Differential pressure reading TG"


def query():
    frames = []
    att_lst = [pressureMG, pressureTG]

    for i in att_lst:
        cursor, conn = PI_connect()
        select = f'''
                    SELECT a.TimeStamp
                    ,a.Value_Double
                    FROM Element.Element e
                    inner join Element.Attribute ea ON ea.ElementID = e.ID
                    inner join Element.Archive a ON a.AttributeID = ea.ID
                    inner join Element.ElementHierarchy eh ON eh.ElementID = ea.ElementID
                    WHERE e.Name in ('Pressure Monitoring')
                    and ea.name in ('{i}')  
                    and a.TimeStamp > '{current_date}'
                 '''
        df = pd.read_sql(select, conn)
        df.to_csv('pi_gm_tg')
        df = df.iloc[-1:]
        df['Field_Name'] = i
        frames.append(df)
    return frames


def makePI_frame():

    try:
        frames = query()
        df2 = pd.concat(frames)
        mg = df2.loc[df2['Field_Name'].isin(['Differential pressure reading MG'])]
        tg = df2.loc[df2['Field_Name'].isin(['Differential pressure reading TG'])]
        date_mg = mg['TimeStamp'].to_string()[11:]
        date_tg = tg['TimeStamp'].to_string()[11:]
        value_mg = mg['Value_Double'].to_string()[9:]
        value_tg = tg['Value_Double'].to_string()[9:]

        data = {'TimeStampMG': [date_mg],
                'PValuesMG': [value_mg],
                'TimeStampTG': [date_tg],
                'PValuesTG': [value_tg],
                }
        df3 = pd.DataFrame(data)
        return df3
    except Exception as e:
        pass

