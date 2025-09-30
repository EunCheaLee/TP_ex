# pip install git+https://github.com/haven-jeon/PyKoSpacing.git
from pykospacing import Spacing

spacing = Spacing()

input_path = "../data/txt/sentences_nospace.txt"
output_path = "../data/txt/sentences_corrected_kospacing.txt"

with open(input_path, "r", encoding="utf-8") as f_in, \
     open(output_path, "w", encoding="utf-8") as f_out:

    # 1. 한 줄씩 읽어서 KoSpacing 적용
    for line in f_in:
        line = line.strip()
        if not line:
            continue

        corrected = spacing(line)
        f_out.write(corrected + "\n")

print(f"전처리 완료! 결과는 {output_path}에 저장되었습니다.")
