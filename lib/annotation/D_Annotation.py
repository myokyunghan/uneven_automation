from lib.annotation.import_files import *
# https://github.com/meta-llama/llama-recipes/blob/main/recipes/quickstart/Prompt_Engineering_with_Llama_3.ipynb
class D_Annotation:

    def __init__(self, llm_model, few_shot_n, test_n, q_src_yn, ver, p_ver):  
            self.ollama         = 'llama-3.1-70b-instruct-lorablated.Q4_K_M:latest'
            self.chatgpt        = OpenAI(api_key= conf.OEPN_AI_KEY)
            self.vllm           = '/usr/share/d_ollama/.ollama/models/hf_model/Llama-3.2-1B-Instruct'

            self.df             = pd.DataFrame()
            self.fewshot_q_id   = []
            self.eval_q_id      = []
            self.eval_prompt    = []
            self.result         = []
            self.message_list   = []
            self.eval_q_list    = []

            # param
            self.test_n         = test_n
            self.sys_prompt     = prompt[p_ver] 
            self.p_ver          = p_ver
            self.version        = str(ver)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>__init__")
            
            for n in range(test_n) :
                self.write_promt(few_shot_n, q_src_yn, n )
            
            self.calc_acc(llm_model, few_shot_n, q_src_yn)

    def random_selection(self, few_shot_n, q_src_yn):
        if q_src_yn == "Y":
            self.df = pd.read_csv('../../data/q_output_code_y.csv', index_col = 0)
        else :
            self.df = pd.read_csv('../../data/q_output.csv', index_col = 0)

        diff_dict = {'Difficulty Level : Basic':        '<Difficulty Level>0</Difficulty Level>' ,
                    'Difficulty Level : Intermediate':  '<Difficulty Level>1</Difficulty Level>', 
                    'Difficulty Level : Advanced':      '<Difficulty Level>2</Difficulty Level>'}
        self.df['answer_encode'] = self.df['answer'].apply(lambda x : diff_dict[x])
        diff_idx = {x : list(self.df[self.df['answer']==x].index) for x in list(diff_dict.keys())}

        diff_s_idx = {}
        for key, value in diff_idx.items():
            dic_col = f'{key}_sample_idx'
            diff_population = value
            diff_s_idx[dic_col] = np.random.choice(diff_population, size=few_shot_n, replace=False)
        self.fewshot_q_id   = list(chain.from_iterable(diff_s_idx.values()))
        self.eval_q_id      = np.setdiff1d(list(self.df.index), self.fewshot_q_id)

        examples = []
        for idx in self.fewshot_q_id:
            temp_dict = {"question" : str(self.df.loc[idx, 'question']),
                        "answer"   : str(self.df.loc[idx, 'answer_encode'])}
            examples.append(temp_dict)
        return examples
            

    def write_promt(self, few_shot_n, q_src_yn, n) : 
        examples = self.random_selection(few_shot_n, q_src_yn)
        # write system prompt & examples
        message = []
        message.append({"role": "system", "content": self.sys_prompt})
        for q_a in examples : 
            q_prompt = """\nHere is the examples of question\n"""
            q_prompt = q_prompt+f"{q_a['question']}\n"

            message.append({"role": "user", "content": q_prompt})
            message.append({"role": "assistant", "content": q_a['answer']})

        # select the random evaluate question
        eval_q_idx = np.random.choice(self.eval_q_id, size=1, replace=False)[0]
        self.eval_q_list.append(eval_q_idx)
        
        target_post="""\nHere is the target post. Answer the "Difficulty Level".\n"""
        target_post = target_post+"""\n<target_post>\n"""
        target_post = target_post+self.df.loc[eval_q_idx, 'question']+'\n'
        target_post = target_post+"""</target_post>\n"""

        message.append({"role": "user", "content": target_post})

        self.message_list.append(message)


    def calc_acc_for_v(self, llm_model, few_shot_n, q_src_yn):
        vllm = a_vllm()
        for idx, message in tqdm(enumerate(self.message_list)):
            tmp = []
            response = vllm.llm.chat(message, sampling_params=vllm.params) 

            tmp.append(self.df.loc[self.eval_q_list[idx], 'id'])
            print(response)
            tmp.append(response['message']['content'])
            self.result.append(tmp)
        result_df = pd.DataFrame(self.result, columns = ['id', 'result'])
        result_df = pd.merge(self.df, result_df, on = 'id')
        result_df.to_csv(f'./result/{llm_model}_result_{few_shot_n}_{self.test_n}_{q_src_yn}_{self.version}_{self.p_ver}.csv')

 
    def calc_acc_for_l(self, llm_model, few_shot_n, q_src_yn):
        for idx, message in tqdm(enumerate(self.message_list)):
            tmp = []
            response = chat( model      = self.ollama,
                            messages    = message
                            )
            tmp.append(self.df.loc[self.eval_q_list[idx], 'id'])
            tmp.append(response['message']['content'])
            self.result.append(tmp)
        result_df = pd.DataFrame(self.result, columns = ['id', 'result'])
        result_df = pd.merge(self.df, result_df, on = 'id')
        result_df.to_csv(f'./result/{llm_model}_result_{few_shot_n}_{self.test_n}_{q_src_yn}_{self.version}_{self.p_ver}.csv')

    def calc_acc_for_c(self, llm_model, few_shot_n, q_src_yn):
        for idx, message in tqdm(enumerate(self.message_list)):
            tmp = []
            MODEL = "gpt-4o"
            response = self.chatgpt.chat.completions.create(
                model=MODEL,
                messages=message,
                temperature=0,
            )
            tmp.append(self.df.loc[self.eval_q_list[idx], 'id'])
            tmp.append([response.choices[0].message.content])
            self.result.append(tmp)
        result_df = pd.DataFrame(self.result, columns = ['id', 'result'])
        result_df = pd.merge(self.df, result_df, on = 'id')
        result_df.to_csv(f'./result/{llm_model}_result_{few_shot_n}_{self.test_n}_{q_src_yn}_{self.version}_{self.p_ver}.csv')


    def calc_acc(self, llm_model, few_shot_n, q_src_yn) :
        if llm_model == 'l' : # ollama 
            # print(self.eval_prompt)
            self.calc_acc_for_l(llm_model, few_shot_n, q_src_yn)
        elif llm_model == 'c' : # chatgpt 
            # print(self.eval_prompt)
            self.calc_acc_for_c(llm_model, few_shot_n, q_src_yn)
        elif llm_model == 'v' : # chatgpt 
            print("VLLM")
            self.calc_acc_for_v(llm_model, few_shot_n, q_src_yn)



               
                
