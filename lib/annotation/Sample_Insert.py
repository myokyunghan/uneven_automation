from lib.annotation.import_files import *

class Sample_Insert: 
    def __init__(self, st_dt, end_dt, sample_num, seed, posttype, num_of_date):

        self.st_dt          = st_dt     
        self.end_dt         = end_dt    
        self.sample_num     = sample_num
        self.seed           = seed      
        self.posttype       = posttype  
        self.seq_nm         = sequence[num_of_date]
    
    def get_id_list(self, posttype, st_dt, end_dt):
        print("sample_insert> get_id_list") 
        if posttype == "1" : 
            print("sample_insert> get_id_list> posttype==1") 
            posttype = "'1'"
            q_sql = """select to_char(a.creationdate, 'yyyy-mm-dd') as creationdate, 
                            a.id 
                        from posts a 
                where a.tags like '%<python>%' 
                and a.posttypeid = {0}  
                and a.creationdate between '{1}' and '{2}'
                and not exists (select 1 
                                    from tt_posts_difficulty_annotated x 
                                where a.id = x.id)
                """ 
            # tt_posts_difficulty_annotated : human annoated questions
            conn = psycopg2.connect(host = conf.database_user['host'], dbname=conf.database_user['dbname'], user=conf.database_user['user'], password=conf.database_user['password'])
            try:
                cur = conn.cursor()
                cur.execute(q_sql.format(posttype, st_dt, end_dt))
                rows = cur.fetchall()

            except psycopg2.DatabaseError as db_err:
                print(db_err)
            finally : 
                cur.close()

            q_output = pd.DataFrame(rows, columns = ['creationdate','id'])
            return q_output

        else : 
            print("sample_insert> get_id_list> posttype==2") 
            posttype = "'2'"


    def chk_targ_yn(posttype, st_dt, end_dt, num_p):
        print("sample_insert> chk_targ_yn> ") 

        st_day  = datetime(int(st_dt.split('-')[0]), int(st_dt.split('-')[1]), int(st_dt.split('-')[2])) # 비교할 날짜(2020.1.1)
        end_day = datetime(int(end_dt.split('-')[0]), int(end_dt.split('-')[1]), int(end_dt.split('-')[2])) # 비교할 날짜(2020.1.1)
        diff = end_day - st_day


        if posttype == "1" : 
            print("sample_insert> chk_targ_yn> posttype==1") 
            posttype = "'1'"
            q_sql = """select z.std_date, count(*) as cnt
                        from (
                                select to_char(x.date, 'yyyy-mm-dd') as std_date, y.id
                                from date_master x
                                            left join (select a.id, to_char(b.creationdate, 'yyyy-mm-dd') as date
                                                    from tt_posts_difficulty a
                                                        , posts b
                                                    where a.id = b.id
                                                    and b.posttypeid = {0}  ) y
                                                    on to_char(x.date, 'yyyy-mm-dd') = y.date
                                where x.date between '{1}' and '{2}'
                            ) z
                        group by z.std_date
                """ 
            conn = psycopg2.connect(host = conf.database_user['host'], dbname=conf.database_user['dbname'], user=conf.database_user['user'], password=conf.database_user['password'])
            try:
                cur = conn.cursor()
                cur.execute(q_sql.format(posttype, st_dt, end_dt))
                rows = cur.fetchall()

            except psycopg2.DatabaseError as db_err:
                print(db_err)
            finally : 
                cur.close()

            q_output = pd.DataFrame(rows, columns = ['std_date', 'cnt'])
            return ((diff.days - q_output.shape[0]) == 0) & (q_output[q_output['cnt']!=num_p].shape[0]==0)
            # return q_output

        else : 
            print("sample_insert> get_id_list> posttype==2") 
            posttype = "'2'"


    def insert_sample(self):
        print("sample_insert") 

        p_id_df = self.get_id_list(self.posttype, self.st_dt, self.end_dt)
        dt_list = list(p_id_df['creationdate'].unique())

        print("sample_insert > create connection")
        engine_str = "postgresql://{}:{}@{}/{}".format(conf.database_user['user'],conf.database_user['password'],conf.database_user['host'],conf.database_user['dbname'])
        engine = sa.create_engine(engine_str, client_encoding='utf8')
        conn = engine.raw_connection()
        cursor = conn.cursor()
        try:
            c_sql = """select nextval('{0}');""" 
            cursor.execute(c_sql.format(self.seq_nm))
            var = cursor.fetchall()[0]
            print(type(var))

            for dt in dt_list : 
                dt_p_id_list = p_id_df.loc[p_id_df['creationdate'] == dt, 'id'].values
                print("sample_insert > create connection> dt_p_id_list>", dt, len(dt_p_id_list))

                first_ann_q_id = [[int(var[0]),dt , int(x)] for x in np.random.choice(dt_p_id_list, size=self.sample_num, replace=False)]
                print("sample_insert > create connection> first_ann_q_id>", dt, first_ann_q_id)

                sql = 'INSERT INTO public.tt_posts_difficulty_target  VALUES %s'


                psycopg2.extras.execute_values(cursor, sql, first_ann_q_id, template=None, page_size=100)
                conn.commit()
        except Exception as e:
            print('Error : ', e)
        else:
            print("insert_db : else - ")
        finally:
            conn.commit()
            cursor.close()
            conn.close()            

    

