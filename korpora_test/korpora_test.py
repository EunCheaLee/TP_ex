import json
import pandas as pd
from Korpora import Korpora

def Korpora_list_save():
    # k_list = json.dumps(Korpora.corpus_list(),
    #                     ensure_ascii=False, # 한글이 깨지지 않음
    #                     indent=2)           # 보기 좋게 들여쓰기

    # 코퍼스 리스트 가져오기
    k_list = Korpora.corpus_list()

    # 2. JSON으로 저장
    with open("../data/Korpora_list.json", "w", encoding="utf-8") as f:
        json.dump(k_list, f, ensure_ascii=False, indent=2)  # dumps() 제거

def Korpora_pair_question():
    pair_question = Korpora.fetch("question_pair")

    train_path = r"C:\Users\tj\Korpora\question_pair\kor_pair_train.csv"
    test_path = r"C:\Users\tj\Korpora\question_pair\kor_pair_test.csv"

    train_df = pd.read_csv(train_path)
    # Index(['id', 'qid1', 'qid2', 'question1', 'question2', 'is_duplicate'], dtype='object')
    test_df = pd.read_csv(test_path)
    # Index(['test_id', 'question1', 'question2', 'is_duplicate', 'Unnamed: 4'], dtype='object')

def Korpora_kor_wiki():
    kor_wiki = Korpora.fetch("kowikitext")

    # 경로 설정
    train_path = r"C:\Users\tj\Korpora\kowikitext\kowikitext_20200920.train"
    test_path = r"C:\Users\tj\Korpora\kowikitext\kowikitext_20200920.test"
    dev_path = r"C:\Users\tj\Korpora\kowikitext\kowikitext_20200920.dev"

    # 파일 읽기
    with open(train_path, "r", encoding="utf-8") as f:
        train_lines = f.readlines()

    with open(test_path, "r", encoding="utf-8") as f:
        test_lines = f.readlines()

    with open(dev_path, "r", encoding="utf-8") as f:
        dev_lines = f.readlines()

    # 확인
    print(f"train sample: {train_lines[:5]}")
    print(f"총 train 문장 수: {len(train_lines)}")

if __name__ == '__main__':
    Korpora_kor_wiki()