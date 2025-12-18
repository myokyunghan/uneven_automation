from lib.annotation.import_files import *
from lib.annotation.VLLM import VLLM
# https://github.com/meta-llama/llama-recipes/blob/main/recipes/quickstart/Prompt_Engineering_with_Llama_3.ipynb
class SampleSelf_Consistency:
    def __init__(self, annoate_target):  
        self.ollama         = 'llama-3.1-70b-instruct-lorablated.Q4_K_M:latest'
        self.chatgpt        = OpenAI(api_key= conf.OEPN_AI_KEY)

        self.df             = pd.DataFrame()
        # self.fewshot_q_id   = []
        self.eval_q_id      = []
        self.eval_prompt    = []
        self.result         = []
        self.message_list   = []
        self.eval_q_list    = []

        # param
        self.llm_model      = param['llm_model']
        self.few_shot_n     = param['few_shot_n']
        self.q_src_yn       = param['q_src_yn']
        self.sys_prompt     = param['p_ver'] 
        self.sf_num         = param['sf_num']
        self.temperature    = param['temperature']
        self.excel_ver      = param['excel_ver']
        
        self.annoate_target = annoate_target.reset_index(drop=True)
        self.annoate_target['creationdate'] = pd.to_datetime(self.annoate_target['creationdate']).dt.date
        self.date           = annoate_target.iloc[0,1]
        self.ver            = int(annoate_target.iloc[0,0])

        self.save_dir       = f'./result/{self.ver}'

        print(f'param for sample self consistency : {self.llm_model} | {self.few_shot_n} | {self.q_src_yn} | {self.sys_prompt} | {self.sf_num} | {self.temperature} | {self.excel_ver}' )
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)  # 중첩된 폴더도 생성 가능

    def random_selection(self):
        few_shot_n, q_src_yn = param['few_shot_n'], param['q_src_yn']

        file_path = f'{conf.DATA_PATH}/data/q_output'
        if q_src_yn == "Y":
            file_path = f'{file_path}_code_y'
        file_path = f'{file_path}{excel[self.excel_ver]}'
        print(f'{file_path}.csv')
        
        self.df = pd.read_csv(f'{file_path}.csv', index_col = 0)

        diff_dict = {'Difficulty Level : Basic':        '<Difficulty Level>0</Difficulty Level>' ,
                    'Difficulty Level : Intermediate':  '<Difficulty Level>1</Difficulty Level>', 
                    'Difficulty Level : Advanced':      '<Difficulty Level>2</Difficulty Level>'}
        self.df['answer_encode'] = self.df['answer'].apply(lambda x : diff_dict[x])
        # to evaluate self-consistency, pick eval target first
        # self.eval_q_id      = np.random.choice(list(self.df.index), size=test_n, replace=False)

        # and set the few shot example target
        diff_idx = {x : list(self.df[self.df['answer']==x].index) for x in list(diff_dict.keys())}

        diff_s_idx = {}
        for l in range(self.annoate_target.shape[0]):

            sc_q_list = []
            for sf in range(self.sf_num):
                tmp = []
                for key, value in diff_idx.items():
                    diff_population = value
                    tmp.append(np.random.choice(diff_population, size=few_shot_n, replace=True))
                sc_q_list.append(np.concatenate(tmp))
            diff_s_idx[self.annoate_target.loc[l, 'id']] = sc_q_list
        return diff_s_idx
            

    def write_promt(self) : 
        e_f_dict = self.random_selection()
        # {eval_q_id : [[fewshot1, ..., fewshotn],[fewshot1, ..., fewshotn]], ...} 
        dict_for_p = {}
        for e_idx, f_idx_list in e_f_dict.items():
            examples = []
            for f_idxs in f_idx_list :
                example = []
                for f_idx in f_idxs :
                    temp_dict = {"question" : str(self.df.loc[f_idx, 'question']),
                                "answer"   : str(self.df.loc[f_idx, 'answer_encode'])}
                    example.append(temp_dict)
                examples.append(example)
            dict_for_p[e_idx] = examples

        # write system prompt & examples
        for eval_id, few_list in dict_for_p.items() : 
            for few_sf_list in few_list : 
                message = []
                message.append({"role": "system", "content": prompt[self.sys_prompt]})

                for few_sf in few_sf_list:
                    q_prompt = """\nHere is the examples of question\n"""
                    q_prompt = q_prompt+f"{few_sf['question']}\n"
                    message.append({"role": "user", "content": q_prompt})
                    message.append({"role": "assistant", "content": few_sf['answer']})
                # select the random evaluate question

                self.eval_q_list.append(eval_id)
                
                target_post="""\nHere is the target post. Answer the "Difficulty Level".\n"""
                target_post = target_post+"""\n<target_post>\n"""
                target_post = target_post+self.annoate_target.loc[self.annoate_target['id']==eval_id, 'question'].values[0]+'\n'
                target_post = target_post+"""</target_post>\n"""
                message.append({"role": "user", "content": target_post})
                self.message_list.append(message)
        return self.message_list

        # print("self.eval_q_list : ", self.eval_q_list)
        # print("self.message_list :", len(self.message_list))
            # with open("list.json", "w") as file:
            #     json.dump(self.message_list, file)

    def insert_result(self, result_df):
        result_df = result_df[['ver', 'creationdate', 'id']].drop_duplicates()
        engine_str = "postgresql://{}:{}@{}/{}".format(conf.database_user['user'],conf.database_user['password'],conf.database_user['host'],conf.database_user['dbname'])
        engine = sa.create_engine(engine_str, client_encoding='utf8')
        conn = engine.raw_connection()
        cursor = conn.cursor()
        try:
            data_list = [[int(x[1]), x[2], int(x[3])] for x in result_df.to_records()]
            sql = 'INSERT INTO public.tt_posts_difficulty_done  VALUES %s'
            psycopg2.extras.execute_values(cursor, sql, data_list, template=None, page_size=100)
            conn.commit()
        except Exception as e:
            print('Error : ', e)
        else:
            print("insert_db : else - ")
        finally:
            conn.commit()
            cursor.close()
            conn.close()            

    def calc_acc_for_v(self, llm_model, few_shot_n, q_src_yn):
        vllm = VLLM()
        for idx, message in tqdm(enumerate(self.message_list)):
            tmp = []
            response = vllm.llm.chat(message, sampling_params=vllm.params) 

            tmp.append(self.df.loc[self.eval_q_list[idx], 'id'])
            tmp.append(response[0].outputs[0].text)
            self.result.append(tmp)
        result_df = pd.DataFrame(self.result, columns = ['id', 'result'])
        result_df = pd.merge(self.df, result_df, on = 'id')
        result_df.to_csv(f'./result/sc_{llm_model}_result_{few_shot_n}_{self.test_n}_{q_src_yn}_{self.version}_{self.p_ver}_{self.sf_num}_{self.temperature}_{self.excel_ver}_{self.loop_i}.csv')
 
    def calc_acc_for_l(self):           
        for idx, message in tqdm(enumerate(self.message_list)):
            data = []
            response = chat( model      = self.ollama,
                            messages    = message,
                            )
            data.append(self.eval_q_list[idx])
            data.append(response['message']['content'])
            self.result.append(data)
        
        result_df = pd.DataFrame(self.result, columns = ['id', 'result'])
        result_df = pd.merge(self.annoate_target[['ver', 'creationdate', 'id']], result_df,on = 'id')
        
        result_df.to_csv(f'{self.save_dir}/{self.date}.csv')
        print(f'{self.save_dir}/{self.date}.csv')

        self.insert_result(result_df)
        return result_df

    def calc_acc_for_c(self):
        for idx, message in tqdm(enumerate(self.message_list)):
            data = []
            MODEL = "gpt-4o"
            response = self.chatgpt.chat.completions.create(
                model=MODEL,
                messages=message,
                temperature= self.temperature,
            )
            data.append(self.eval_q_list[idx])
            data.append(response['message']['content'])
            self.result.append(data)
        result_df = pd.DataFrame(self.result, columns = ['id', 'result'])
        result_df = pd.merge(self.annoate_target[['ver', 'creationdate', 'id']], result_df,on = 'id')
        
        result_df.to_csv(f'{self.save_dir}/{self.date}.csv')
        print(f'{self.save_dir}/{self.date}.csv')

        self.insert_result(result_df)



    def calc_acc(self, llm_model, few_shot_n, q_src_yn) :
        if llm_model == 'l' : # ollama 
            # print(self.eval_prompt)
            self.calc_acc_for_l(llm_model, few_shot_n, q_src_yn)
            

        elif llm_model == 'c' : # chatgpt 
            # print(self.eval_prompt)
            self.calc_acc_for_c(llm_model, few_shot_n, q_src_yn)
            
        elif llm_model == 'v' : # vLLM
            print("VLLM")
            self.calc_acc_for_v(llm_model, few_shot_n, q_src_yn)