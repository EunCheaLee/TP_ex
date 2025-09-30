from bareunpy import Corrector

# Corrector 초기화
API_KEY = "(API key)"  # 본인의 API 키를 입력하세요
HOST = "api.bareun.ai"             # 로컬 서버를 사용하는 경우
PORT = 443                     # 포트 번호
corrector = Corrector(apikey=API_KEY, host=HOST, port=PORT)

input_file = '../data/txt/sentences_spaced_pykospacing.txt'
output_file = '../data/txt/sentences_corrected_api.txt'

# 파일 처리
with open(input_file, 'r', encoding='utf-8') as fin, \
     open(output_file, 'w', encoding='utf-8') as fout:

    for i, line in enumerate(fin, 1):
        line = line.strip()
        if not line:
            fout.write("\n")
            continue

        try:
            res = corrector.correct_error(content=line)
            fout.write(res.revised + "\n")
        except Exception as e:
            print(f"[{i}] 오류 발생: {e}")
            fout.write(line + "\n")  # 오류 시 원문 그대로 저장

        if i % 100 == 0:
            print(f"[진행] {i} / 약 9900 문장 처리 완료")

print("맞춤법 교정 완료! 결과는", output_file, "에 저장되었습니다.")