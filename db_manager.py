from sqlalchemy import create_engine
import pandas as pd
import pyodbc
from datetime import datetime

current_date = datetime.date(datetime.now())


class SQL:
    def __init__(self, user, pwd, db, driver, server):
        self.user = user
        self.pwd = pwd
        self.db = db
        self.driver = driver
        self.server = server
        self.engine = create_engine(f'mssql+pyodbc://{user}:{pwd}@{server}/{db}?driver={driver}')

    def pi_data(self, event_data, db_fields):
        cur = self.engine.connect()
        # cur.execute(
        #     "INSERT INTO pulse_shield_locator (date_time_create) VALUES (CURRENT_TIMESTAMP)", )
        # df = pd.DataFrame(event_data)
        # df = df.transpose()
        # df.columns = db_fields
        # df.to_sql('pulse_shield_locator', con=self.engine, if_exists='append', index=False)


# gets last ventilation velocity value
def pi_query_vent():
    conn = pyodbc.connect(
        "Driver=PI SQL Client; AF Server=AISGROOSI01; AF Database='Grosvenor MAC'; Integrated Security=SSPI;",
        autocommit=True)
    select_statement = f'''
                SELECT a.TimeStamp
                ,a.Value_Double
                FROM Element.Element e
                inner join Element.Attribute ea ON ea.ElementID = e.ID
                inner join Element.Archive a ON a.AttributeID = ea.ID
                inner join Element.ElementHierarchy eh ON eh.ElementID = ea.ElementID
                WHERE e.Name in ('Pressure Monitoring')
                and ea.name in ('Ventillation Velocity')
                and a.TimeStamp > '{current_date}'
                '''
    df = pd.read_sql(select_statement, conn)
    df = df.iloc[-1:]
    df = df['Value_Double']
    return df.to_string()[7:]




