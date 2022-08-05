import pyodbc
import pandas as pd
import datetime
import warnings

warnings.filterwarnings("ignore")

# get last 5 mins of events
x = 300
end_date = datetime.datetime.now()
start_date = datetime.datetime.now() - datetime.timedelta(seconds=x)

# for testing historical
# start_date  = '2022-08-02'
# end_date = '2022-08-03'


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
                   and a.TimeStamp between '{start_date}' and '{end_date}'
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
                and a.TimeStamp between '{start_date}' and '{end_date}'
                '''
    df = pd.read_sql(select, conn)
    df = df.iloc[-1:]
    df = df['Value_Double']
    return df.to_string()[7:]


