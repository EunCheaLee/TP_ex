import json

# JSON 파일 읽기
with open('../data/json/cleaned_pdf.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 모든 값에서 \n 제거
def remove_newlines(obj):
    if isinstance(obj, dict):
        return {k: remove_newlines(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [remove_newlines(item) for item in obj]
    elif isinstance(obj, str):
        return obj.replace('\n', ' ')
    else:
        return obj

# \n 제거 적용
cleaned_data = remove_newlines(data)

# 결과를 새 JSON 파일로 저장
with open('../data/json/cleaned_pdf.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

print("완료! output.json 파일이 생성되었습니다.")