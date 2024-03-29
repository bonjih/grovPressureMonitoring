from sqlalchemy import create_engine
import pandas as pd
import pyodbc
from datetime import datetime

current_date = datetime.date(datetime.now())


class SQL:
    '''
    SQL class for MSSQL access, query and insert
    '''
    def __init__(self, user, pwd, db, driver, server):
        self.user = user
        self.pwd = pwd
        self.db = db
        self.driver = driver
        self.server = server
        self.engine = create_engine(f'mssql+pyodbc://{user}:{pwd}@{server}/{db}?driver={driver}')
        self.conn = pyodbc.connect(user=user, password=pwd, database=db, driver=driver, server=server)

    def check_entry_exist(self, event_id):
        cur = self.conn.cursor()
        cur.execute('SELECT event_id FROM pulse_shield_locator WHERE event_id = ?', event_id)
        exits = cur.fetchone()
        if exits is None:
            return False
        if event_id == str(exits[0]):
            return True
        if event_id != str(exits[0]):
            return False

    def insert(self, event_data, db_fields):
        df = pd.DataFrame(event_data)
        df = df.apply(lambda x: x.explode().astype(str).groupby(level=0).agg(", ".join))
        df = df.transpose()
        df.columns = db_fields
        df['fst_pulse_time'] = df['fst_pulse_time'].astype('datetime64[ns]')
        df['sec_pulse_time'] = df['sec_pulse_time'].astype('datetime64[ns]')
        df['trd_pulse_time'] = df['trd_pulse_time'].astype('datetime64[ns]')
        df['fth_pulse_time'] = df['fth_pulse_time'].astype('datetime64[ns]')
        df.to_csv('events.csv', mode='a', index=False)  # if db connection fails
        df.to_sql('pulse_shield_locator', con=self.engine, if_exists='append', index=False)
