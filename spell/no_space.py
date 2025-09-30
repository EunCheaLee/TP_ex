import re

input_path = "../data/txt/sentences_spaced_pykospacing.txt"
output_path = "../data/txt/sentences_nospace.txt"

with open(input_path, "r", encoding="utf-8") as f_in, \
     open(output_path, "w", encoding="utf-8") as f_out:

    text = f_in.read()

    # 1. 모든 따옴표 제거 (내용 살리기)
    text_no_quotes = text.replace('"', '').replace("'", '').replace('“','').replace('”','')

    # 2. 문장 단위 분리 후 줄바꿈
    sentences = re.split(r'(?<=\.)', text_no_quotes)
    sentences = [s.strip() for s in sentences if s.strip()]

    # 3. 띄어쓰기 제거 & 출력 파일에 저장
    for s in sentences:
        no_space = s.replace(" ", "")
        f_out.write(no_space + "\n")

print(f"전처리 완료! 결과는 {output_path}에 저장되었습니다.")
