import pdfplumber
from pathlib import Path
import json


def extract_text_pdfplumber(pdf_path):
    text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text())

    return '\n'.join(text)


# 폴더 내 모든 PDF 파일 처리
def process_all_pdf_files(folder_path='../data/pdf'):
    """폴더 내 모든 PDF 파일을 처리"""
    folder = Path(folder_path)
    pdf_files = list(folder.glob('*.pdf'))  # 현재 폴더만
    # 또는 pdf_files = list(folder.rglob('*.pdf'))  # 하위 폴더 포함

    print(f"Found {len(pdf_files)} PDF files\n")

    all_texts = {}
    success_count = 0
    fail_count = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
            text = extract_text_pdfplumber(str(pdf_file))
            all_texts[pdf_file.name] = text
            success_count += 1
            print(f"  ✓ Success\n")
        except Exception as e:
            fail_count += 1
            print(f"  ✗ Error: {e}\n")

    print(f"=== Summary ===")
    print(f"Total: {len(pdf_files)}")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")

    return all_texts


# 사용 예시
texts = process_all_pdf_files('../data/pdf')

# 결과 확인
for filename, text in texts.items():
    print(f"\n=== {filename} ===")
    print(text[:200])  # 처음 200자만 출력
    print("...")


# JSON으로 저장
def save_to_json(texts, output_file='pdf_texts.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_file}")


save_to_json(texts, '../data/json/pdf_texts.json')