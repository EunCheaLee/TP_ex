import json
import re


def clean_hwp_text(json_file_path, output_file_path):
    """
    HWP에서 추출한 JSON 파일의 텍스트를 정제합니다.

    Args:
        json_file_path: 입력 JSON 파일 경로
        output_file_path: 출력 JSON 파일 경로
    """
    # JSON 파일 읽기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = {}

    for title, text in data.items():
        # 1. 제어 문자 패턴 제거 (\u0000 ~ \u001F 범위)
        cleaned_text = re.sub(r'[\u0000-\u001F]+', '', text)

        # 2. 특수 유니코드 문자 제거 (예: \u0002, \u0003, \u0004 등)
        cleaned_text = re.sub(r'[\u0002\u0003\u0004\u0011\u0012\u0015]+', '', cleaned_text)

        # 3. 한자나 특수 기호 패턴 제거
        cleaned_text = re.sub(r'[捤獥汤捯湰灧†普湯慴汫]+', '', cleaned_text)

        # 4. \r을 \n으로 통일
        cleaned_text = cleaned_text.replace('\r\n', '\n').replace('\r', '\n')

        # 5. 연속된 공백 제거
        cleaned_text = re.sub(r' +', ' ', cleaned_text)

        # 6. 연속된 줄바꿈 정리 (3개 이상을 2개로)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

        # 7. 앞뒤 공백 제거
        cleaned_text = cleaned_text.strip()

        cleaned_data[title] = cleaned_text

    # 정제된 데이터를 JSON으로 저장
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"정제 완료: {len(cleaned_data)}개 문서 처리됨")
    print(f"저장 위치: {output_file_path}")

    return cleaned_data


def clean_and_save_as_txt(json_file_path, output_folder='cleaned_texts'):
    """
    JSON 파일을 정제하고 각 이야기를 개별 txt 파일로 저장합니다.
    """
    import os

    # 출력 폴더 생성
    os.makedirs(output_folder, exist_ok=True)

    # JSON 파일 읽기
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for title, text in data.items():
        # 텍스트 정제
        cleaned_text = re.sub(r'[\u0000-\u001F]+', '', text)
        cleaned_text = re.sub(r'[\u0002\u0003\u0004\u0011\u0012\u0015]+', '', cleaned_text)
        cleaned_text = re.sub(r'[捤獥汤捯湰灧†普湯慴汫]+', '', cleaned_text)
        cleaned_text = cleaned_text.replace('\r\n', '\n').replace('\r', '\n')
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        cleaned_text = cleaned_text.strip()

        # 개별 txt 파일로 저장
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        output_path = os.path.join(output_folder, f"{safe_filename}.txt")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        print(f"저장됨: {output_path}")

    print(f"\n총 {len(data)}개 파일 저장 완료")


# 사용 예시
if __name__ == "__main__":
    # 방법 1: JSON으로 저장
    cleaned_data = clean_hwp_text('../data/json/hwp_texts.json', '../data/json/cleaned_hwp.json')

    # 방법 2: 개별 txt 파일로 저장
    # clean_and_save_as_txt('input.json', 'cleaned_texts')

    # 정제된 텍스트 미리보기
    for title, text in list(cleaned_data.items())[:1]:
        print(f"\n=== {title} (처음 500자) ===")
        print(text[:500])