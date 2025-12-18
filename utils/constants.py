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

    
    tag_monthly_data_dir = "../result/tag/run_id_0/data"
    lda_monthly_data_dir = "../result/lda/run_id_1/data"

    bert_difficulty_data_dir = "../result/bert_based/difficulty_annotated/data"
    lda_difficulty_data_dir = "../result/lda/difficulty_annotated/data"
    tag_difficulty_data_dir = "../result/bert_based/difficulty_annotated/data"
    
    all_topics_list = list(range(0, 50))