import olefile
import zlib
import struct
from pathlib import Path
import json


def get_hwp_text(filename):
    f = olefile.OleFileIO(filename)
    dirs = f.listdir()

    # HWP 파일 검증
    if ["FileHeader"] not in dirs:
        raise Exception("Not valid HWP.")

    # 문서 포맷 압축 여부 확인
    header = f.openstream("FileHeader")
    header_data = header.read()
    if header_data[36] & 1:
        compressed = True
    else:
        compressed = False

    # Body Sections 불러오기
    nums = []
    for d in dirs:
        if d[0] == "BodyText":
            nums.append(int(d[1][len("Section"):]))
    nums.sort()

    # 전체 text 추출
    text = ""
    for num in nums:
        bodytext = f.openstream("BodyText/Section" + str(num))
        data = bodytext.read()

        if compressed:
            unpacked_data = zlib.decompress(data, -15)
        else:
            unpacked_data = data

        # 텍스트 추출
        section_text = ""
        i = 0
        size = len(unpacked_data)

        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type == 67:  # 67은 문자 데이터
                rec_data = unpacked_data[i + 4:i + 4 + rec_len]
                section_text += rec_data.decode('utf-16')

            if rec_len == 0:
                i += 4
            else:
                i += 4 + rec_len

        text += section_text

    f.close()
    return text


# 폴더 내 모든 HWP 파일 처리
def process_all_hwp_files(folder_path='../data/hwp'):
    """폴더 내 모든 HWP 파일을 처리"""
    folder = Path(folder_path)
    hwp_files = list(folder.glob('*.hwp'))  # 현재 폴더만
    # 또는 hwp_files = list(folder.rglob('*.hwp'))  # 하위 폴더 포함

    print(f"Found {len(hwp_files)} HWP files\n")

    all_texts = {}
    success_count = 0
    fail_count = 0

    for i, hwp_file in enumerate(hwp_files, 1):
        try:
            print(f"[{i}/{len(hwp_files)}] Processing: {hwp_file.name}")
            text = get_hwp_text(str(hwp_file))
            all_texts[hwp_file.name] = text
            success_count += 1
            print(f"  ✓ Success\n")
        except Exception as e:
            fail_count += 1
            print(f"  ✗ Error: {e}\n")

    print(f"=== Summary ===")
    print(f"Total: {len(hwp_files)}")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")

    return all_texts


# 사용 예시
texts = process_all_hwp_files('../data/hwp')

# 결과 확인
for filename, text in texts.items():
    print(f"\n=== {filename} ===")
    print(text[:200])  # 처음 200자만 출력
    print("...")


# JSON으로 저장
def save_to_json(texts, output_file='output.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_file}")


save_to_json(texts, '../data/json/hwp_texts.json')