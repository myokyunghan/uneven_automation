from import_files import *
import argparse
import lib.annotation.D_Annotation as da
import lib.annotation.Self_Consistency as sc
import lib.annotation.Sample_Insert as si
import lib.annotation.Q_Extract as qe
import lib.annotation.SampleSelf_Consistency as ssc


def main(ver):
    print ("start main!")
    ver = re.findall(r"\d+",ver)[0]
    print("start main! : ", ver)
    t_extract = qe.Q_Extract(ver)

    # while True :
    print("t_extract start")
    cnt = t_extract.chk_left()
    print(f"t_extract end_{cnt}")
    if cnt[0][0] > 0 : 
        print(f"Q_Extract start_{cnt[0][1]}")
        df = t_extract.db_extract()
        q_output = t_extract.tb_extract(df)
        print(f"Q_Extract end_{cnt[0][1]}")

        print(f"SampleSelf_Consistency start_{cnt[0][1]}")
        sample_sc = ssc.SampleSelf_Consistency(q_output) 
        print(f"SampleSelf_Consistency end_{cnt[0][1]}")

        print(f"write_promt start_{cnt[0][1]}")
        chk_list = sample_sc.write_promt()
        print(f"write_promt end_{cnt[0][1]}")

        print(f"calc_acc_for_l start_{cnt[0][1]}")
        result_df = sample_sc.calc_acc_for_l()
        print(f"calc_acc_for_l end_{cnt[0][1]}")
    else :
        print("Nothing left")





    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="이 프로그램은 파라미터를 처리합니다.")
    parser.add_argument("param1", type=str, help="")
    args = parser.parse_args()
    print(f"param1: {args.param1}")


    main(args.param1)

