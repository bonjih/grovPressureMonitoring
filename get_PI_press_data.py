import pyodbc
import pandas as pd
import datetime
import warnings

warnings.filterwarnings("ignore")

current_dateTime = datetime.datetime.now()

# get last 30 seconds of events
x = 30
result = datetime.datetime.now() - datetime.timedelta(seconds=x)

# for testing historical
start = '2022-02-25'
end = '2022-02-27'
start1 = '2022-04-01'
end1 = '2022-04-30'
start2 = '2022-05-01'
end2 = '2022-05-31'
start3 = '2022-06-01'
end3 = '2022-06-30'
start4 = '2022-07-01'
end4 = '2022-07-31'

conn = pyodbc.connect(
    "Driver=PI SQL Client; AF Server=AISGROOSI01; AF Database='Grosvenor MAC'; Integrated Security=SSPI;",
    autocommit=True)


def pi_query_pressure():
    select = f'''
               SELECT eh.Name as Element
                   ,ea.Name as Attribute
                   ,Format(a.TimeStamp, 'yyyy/MM/dd HH:mm:ss.ffffff') as TimeStamp
                   ,coalesce(a.Value_Double, a.Value_Int, case when a.Value_String = 'true' then 1 when a.Value_String 
                   = 'false' then 0 else null end) Value
                   FROM Element.ElementHierarchy eh
                   inner join Element.Attribute ea ON ea.ElementID = eh.ElementID
                   inner join Element.Archive a ON a.AttributeID = ea.ID
                   WHERE ea.IsValueGood = 1 
                   and ea.IsValueQuestionable = 0
                   and eh.name in ('Pressure Monitoring')
                   and ea.name in ('Differential pressure reading MG', 'Differential pressure reading TG') 
                   and a.TimeStamp between '{result}' and '{current_dateTime}'
             '''
    df = pd.read_sql(select, conn)
    df.drop('Element', axis=1, inplace=True)
    mg = df.loc[df['Attribute'].isin(['Differential pressure reading MG'])]
    mg.drop('Attribute', axis=1, inplace=True)
    tg = df.loc[df['Attribute'].isin(['Differential pressure reading TG'])]
    tg.drop('Attribute', axis=1, inplace=True)
    mg.rename(columns={'TimeStamp': 'TimeStampMG', 'Value': 'PValuesMG'}, inplace=True)
    tg.rename(columns={'TimeStamp': 'TimeStampTG', 'Value': 'PValuesTG'}, inplace=True)
    tg.reset_index(drop=True, inplace=True)
    df1 = pd.concat([mg, tg], join='outer', axis=1)
    return df1


# gets last ventilation velocity value
def pi_query_vent():
    select = f'''
                SELECT a.TimeStamp
                ,a.Value_Double
                FROM Element.Element e
                inner join Element.Attribute ea ON ea.ElementID = e.ID
                inner join Element.Archive a ON a.AttributeID = ea.ID
                inner join Element.ElementHierarchy eh ON eh.ElementID = ea.ElementID
                WHERE e.Name in ('Pressure Monitoring')
                and ea.name in ('Ventillation Velocity')
                and a.TimeStamp between '{start}' and '{end}'
                '''
    df = pd.read_sql(select, conn)
    df = df.iloc[-1:]
    df = df['Value_Double']
    return df.to_string()[7:]


