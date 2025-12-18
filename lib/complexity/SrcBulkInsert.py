import config.config as conf
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

class SrcBulkInsert:
    def __init__(self):
        self.conn = '' 
        
    def get_conn(self) :
        return psycopg2.connect(   host      =conf.database_user['host'], 
                                        dbname    =conf.database_user['dbname'], 
                                        user      =conf.database_user['user'], 
                                        password  =conf.database_user['password'], 
                                        port      =conf.database_user['port']
                                        ) 
        
    def get_from_db(self, idx, id):
        """

        Args:
            idx: index for the src
            id: id for the src

        Returns:
            Boolean
        """
        self.conn = self.get_conn()

        b_re = False
        q_sql = """select coalesce(nullif(max(1), 0), 0) as cnt
                     from posts_src
                    where idx = {0} 
                      and id = {1}
            """ 
    
        try:
            cursor = self.conn.cursor()
            cursor.execute(q_sql.format(idx, id))
            rows = cursor.fetchall()

        except psycopg2.DatabaseError as db_err:
            print(db_err)
        finally : 
            self.conn.close()

        q_output = pd.DataFrame(rows, columns = ['cnt'])

        if q_output.iloc[0, 0] ==1 : 
            b_re = True

        return b_re

    def insert_posts_src(self, df):
        """

        Args:
            df: a dataframe

        Returns:
            None
        """
        self.conn = self.get_conn()
        tuples = [tuple(x) for x in df.loc[:, :].to_numpy()]

       
        try:
            cursor=self.conn.cursor()
            sql = f"INSERT INTO posts_src VALUES %s;"
            execute_values(cursor, sql, tuples, page_size=1000)
        except psycopg2.DatabaseError as db_err:
            print(db_err)
        finally : 
            self.conn.commit()
            self.conn.close()
