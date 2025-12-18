class CONSTANTS:
    verbose_loading = False
    color_map_str = ["cool", "viridis"]
    chatgpt_release_date = "2022.11.30"
    start_date = "2021.11.30"
    end_date = "2023.11.30"
    monthly_timestamps = [
        "2021.11.30", "2021.12.31", "2022.01.31", "2022.02.28", "2022.03.31",
        "2022.04.30", "2022.05.31", "2022.06.30", "2022.07.31", "2022.08.31",
        "2022.09.30", "2022.10.31", "2022.11.30", "2022.12.31", "2023.01.31",
        "2023.02.28", "2023.03.31", "2023.04.30", "2023.05.31", "2023.06.30",
        "2023.07.31", "2023.08.31", "2023.09.30", "2023.10.31", "2023.11.30"
    ]
    bert_monthly_data_dir = "../result/bert_based/run_id_0/data"
    # 2021년 01 월부터의 데이터
    bert_monthly_data_dir_2 = "../result/bert_based/run_id_2/data"
    # snapshot2 data
    bert_monthly_data_dir_3 = "../result/bert_based/run_id_3/data"

    tag_monthly_data_dir    = "../result/tag/run_id_0/data"
    #2021.11 ~ 2024.11
    tag_monthly_data_dir_2  = "../result/tag/run_id_2/data"

    tag_monthly_data_dir_2_py  = "../result/tag/run_id_2/python/data"
    tag_monthly_data_dir_2_cpp  = "../result/tag/run_id_2/cpp/data"

    lda_monthly_data_dir = "../result/lda/run_id_1/data"

    bert_difficulty_data_dir = "../result/bert_based/difficulty_annotated/data"
    lda_difficulty_data_dir = "../result/lda/difficulty_annotated/data"
    tag_difficulty_data_dir = "../result/bert_based/difficulty_annotated/data"
    
    all_topics_list = list(range(0, 50))

    lang_tag_dict = {'python' : 'python',
                'cpp': 'c++',
                'java':'java',
                'vba':'vba'
                }
    

    tag_lang_dict = {'python' : 'python',
                'c++': 'cpp',
                'java':'java',
                'vba':'vba'
    }

    data_availability_dir='../../visualization'

    data_dir = '/usr/share/d_ollama/data/' 

    ######################submission option below
    s_llm_result_path = '../data/difficulty/q_diff'
    s_com_result_path = '../data/difficulty/c_diff'
