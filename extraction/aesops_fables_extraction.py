import sys
import json
import re


def extract_fables_from_txt(filename):
    """
    이솝 우화 텍스트 파일에서 우화 추출
    형식:
    1. 제목
    내용...
    (우화 끝)
    """

    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"✅ 파일 읽기 완료 (총 {len(text):,} 글자)")

    # 줄바꿈 정규화
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    fables = []
    lines = text.split('\n')

    current_fable = None
    content_lines = []
    skip_until_first_fable = True  # 목차 건너뛰기 플래그

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # 빈 줄 - 빈 줄은 무시 (추가하지 않음)
        if not line_stripped:
            continue

        # 목차 섹션 건너뛰기
        if '■ 목 차' in line_stripped or '목차' in line_stripped:
            skip_until_first_fable = True
            continue

        # 제목 패턴: 숫자. 제목
        title_match = re.match(r'^(\d{1,3})\.\s+(.+)$', line_stripped)

        if title_match:
            number_str = title_match.group(1)  # 문자열로 저장
            title_str = title_match.group(2).strip()

            # 첫 번째 우화를 만나면 목차 건너뛰기 종료
            if skip_until_first_fable:
                skip_until_first_fable = False
                current_fable = {
                    'number': number_str,
                    'title': title_str,
                    'content': ''
                }
                content_lines = []
                continue

            # 이전 우화 저장
            if current_fable and content_lines:
                current_fable['content'] = ' '.join(content_lines)
                fables.append(current_fable)
                print(f"  ✅ {current_fable['number']}. {current_fable['title']} ({len(current_fable['content'])} 글자)")

            # 새 우화 시작
            current_fable = {
                'number': number_str,
                'title': title_str,
                'content': ''
            }
            content_lines = []
            continue

        # (우화 끝) 패턴
        if re.search(r'\(우화\s*끝\)', line_stripped):
            if current_fable:
                # (우화 끝) 이전 내용까지만 추가
                before_end = re.split(r'\(우화\s*끝\)', line_stripped)[0].strip()
                if before_end:
                    content_lines.append(before_end)

                current_fable['content'] = ' '.join(content_lines)
                fables.append(current_fable)
                print(f"  ✅ {current_fable['number']}. {current_fable['title']} ({len(current_fable['content'])} 글자)")

                current_fable = None
                content_lines = []
            continue

        # 내용 수집 (목차 건너뛰기가 끝난 후에만)
        if current_fable and not skip_until_first_fable:
            content_lines.append(line_stripped)

    # 마지막 우화 저장 (끝 표시가 없을 경우)
    if current_fable and content_lines:
        current_fable['content'] = ' '.join(content_lines)
        fables.append(current_fable)
        print(f"  ✅ {current_fable['number']}. {current_fable['title']} ({len(current_fable['content'])} 글자)")

    return fables


def save_to_json(fables, output_file='aesop_fables.json'):
    """JSON 파일로 저장"""
    result = {
        'total_count': len(fables),
        'fables': fables
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 총 {len(fables)}개의 우화가 '{output_file}'에 저장되었습니다.")


def save_aesop_json():
    """이솝 우화 TXT → JSON 변환 메인 함수"""
    print("=" * 60)
    print("이솝 우화 TXT → JSON 변환기")
    print("=" * 60)

    # 파일명 설정
    txt_file = "../data/txt/aesops_fables.txt"
    output_file = '../data/json/aesop_fables.json'

    try:
        print(f"\n📖 파일 읽는 중: {txt_file}")

        # 우화 추출
        fables = extract_fables_from_txt(txt_file)

        if not fables:
            print("\n❌ 우화를 추출하지 못했습니다.")
            print("\n파일 형식을 확인해주세요:")
            print("  - 각 우화는 '숫자. 제목' 형식으로 시작")
            print("  - 각 우화는 '(우화 끝)'으로 종료")
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"✅ 총 {len(fables)}개의 우화를 추출했습니다!")
        print(f"{'=' * 60}")

        # JSON 저장
        save_to_json(fables, output_file)

        # 통계
        print(f"\n{'=' * 60}")
        print("📊 통계")
        print(f"{'=' * 60}")

        total_chars = sum(len(f['content']) for f in fables)
        avg_chars = total_chars // len(fables) if fables else 0

        print(f"총 우화 수: {len(fables)}개")
        print(f"총 글자 수: {total_chars:,}자")
        print(f"평균 길이: {avg_chars:,}자")

        # 미리보기
        print(f"\n{'=' * 60}")
        print("📖 첫 번째 우화 미리보기")
        print(f"{'=' * 60}")

        first = fables[0]
        print(f"번호: {first['number']}")
        print(f"제목: {first['title']}")
        print(f"내용 (처음 300자):")
        print(first['content'][:300])
        if len(first['content']) > 300:
            print("...")

        print(f"\n{'=' * 60}")
        print("✅ 완료!")
        print(f"{'=' * 60}")
        print(f"출력 파일: {output_file}")

    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {txt_file}")
    except UnicodeDecodeError:
        print("❌ 파일 인코딩 오류")
        print("다른 인코딩(cp949, euc-kr)으로 저장된 파일일 수 있습니다.")
        print("메모장에서 UTF-8로 다시 저장해보세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


# 실행
if __name__ == "__main__":
    save_aesop_json()