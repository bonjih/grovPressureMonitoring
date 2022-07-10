

import pymysql as pymysql
from sqlalchemy import create_engine
import pandas as pd


class SQL:
    def __init__(self, user, pwd, host, db):
        self.user = user
        self.pwd = pwd
        self.host = host
        self.db = db
        self.engine = create_engine('mysql+pymysql://' + user + ':' + pwd + '@' + host + '/' + db + '?charset=utf8')
        self.conn = pymysql.connect(user=self.user, passwd=self.pwd, host=self.host, database=self.db)

    # # check if event id exits in table
    # def check_entry_exist(self, event_id):
    #     print(event_id)
    #     cur = self.conn.cursor()
    #     cur.execute('SELECT file_name FROM LW_shield_locator WHERE event_id = %s', event_id)
    #     exits = cur.fetchone()
    #     if exits is None:
    #         return False
    #     if event_id == exits[0]:
    #         return True
    #     if event_id != exits[0]:
    #         return False

    def image_data(self, event_data, db_fields):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO LW_shield_locator (date_time_create) VALUES (CURRENT_TIMESTAMP)", )
        df = pd.DataFrame(event_data)
        df = df.transpose()
        df.columns = db_fields

        df.to_sql('LW_shield_locator', con=self.engine, if_exists='append', index=False)


