import sys
import json
import re


def extract_stories_from_txt(filename):
    """
    텍스트 파일에서 동화 추출
    형식:
    1. 제목
    내용...
    (끝) 또는 (동화 끝)
    """

    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"✅ 파일 읽기 완료 (총 {len(text):,} 글자)")

    # 줄바꿈 정규화
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    stories = []
    lines = text.split('\n')

    current_story = None
    content_lines = []

    for i, line in enumerate(lines):
        original_line = line
        line = line.strip()

        # 빈 줄
        if not line:
            if current_story and content_lines:
                content_lines.append('')
            continue

        # 제목 패턴: 숫자. 제목
        # 1. 개구리 왕자 형식
        title_match = re.match(r'^(\d{1,3})\.\s+(.+)$', line)

        if title_match:
            # 이전 동화 저장
            if current_story and content_lines:
                current_story['content'] = '\n'.join(content_lines).strip()
                stories.append(current_story)
                print(f"  ✅ {current_story['number']}. {current_story['title']} ({len(current_story['content'])} 글자)")

            # 새 동화 시작
            current_story = {
                'number': title_match.group(1),
                'title': title_match.group(2).strip(),
                'content': ''
            }
            content_lines = []
            continue

        # (끝) 또는 (동화 끝) 또는 (동화끝) 패턴
        if re.search(r'\((?:동화\s*)?끝\)', line):
            if current_story:
                # (끝) 이전 내용까지만 추가
                before_end = re.split(r'\((?:동화\s*)?끝\)', line)[0].strip()
                if before_end:
                    content_lines.append(before_end)

                current_story['content'] = '\n'.join(content_lines).strip()
                stories.append(current_story)
                print(f"  ✅ {current_story['number']}. {current_story['title']} ({len(current_story['content'])} 글자)")

                current_story = None
                content_lines = []
            continue

        # 내용 수집
        if current_story:
            content_lines.append(line)

    # 마지막 동화 저장 (끝 표시가 없을 경우)
    if current_story and content_lines:
        current_story['content'] = '\n'.join(content_lines).strip()
        stories.append(current_story)
        print(f"  ✅ {current_story['number']}. {current_story['title']} ({len(current_story['content'])} 글자)")

    return stories

def save_to_json(fairy_tales, output_file='fairy_tales.json'):
    """JSON 파일로 저장"""
    result = {
        'total_count': len(fairy_tales),
        'fairy_tales': fairy_tales
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 총 {len(fairy_tales)}개의 동화가 '{output_file}'에 저장되었습니다.")

def save_grim_bro_json():
    print("=" * 60)
    print("그림 형제 동화 TXT → JSON 변환기")
    print("=" * 60)

    # 파일명 입력
    txt_file = "../data/txt/grim_bro.txt"

    try:
        print(f"\n📖 파일 읽는 중: {txt_file}")

        # 동화 추출
        fairy_tales = extract_stories_from_txt(txt_file)

        if not fairy_tales:
            print("\n❌ 동화를 추출하지 못했습니다.")
            print("\n파일 형식을 확인해주세요:")
            print("  - 각 동화는 '숫자. 제목' 형식으로 시작")
            print("  - 각 동화는 '(끝)' 또는 '(동화 끝)'으로 종료")
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"✅ 총 {len(fairy_tales)}개의 동화를 추출했습니다!")
        print(f"{'=' * 60}")

        # 출력 파일명 입력
        output_file = '../data/json/grim_bro.json'

        # JSON 저장
        save_to_json(fairy_tales, output_file)

        # 통계
        print(f"\n{'=' * 60}")
        print("📊 통계")
        print(f"{'=' * 60}")

        total_chars = sum(len(s['content']) for s in fairy_tales)
        avg_chars = total_chars // len(fairy_tales) if fairy_tales else 0

        print(f"총 동화 수: {len(fairy_tales)}개")
        print(f"총 글자 수: {total_chars:,}자")
        print(f"평균 길이: {avg_chars:,}자")

        # 미리보기
        print(f"\n{'=' * 60}")
        print("📖 첫 번째 동화 미리보기")
        print(f"{'=' * 60}")

        first = fairy_tales[0]
        print(f"번호: {first['number']}")
        print(f"제목: {first['title']}")
        print(f"내용 (처음 500자):")
        print(first['content'][:500])
        if len(first['content']) > 500:
            print("...")

        print(f"\n{'=' * 60}")
        print("✅ 완료!")
        print(f"{'=' * 60}")

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

def remove_newlines_from_json(input_file, output_file=None):
    """
    JSON 파일에서 모든 \n을 제거
    """

    # JSON 파일 읽기
    print(f"📖 JSON 파일 읽는 중: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✅ 파일 읽기 완료")
    print(f"   총 동화 수: {data.get('total_count', len(data.get('fairy_tales', [])))}개")

    # \n 제거
    print("\n🔄 줄바꿈 제거 중...")

    fairy_tales = data.get('fairy_tales', [])

    for i, story in enumerate(fairy_tales):
        if 'content' in story:
            original_length = len(story['content'])

            # \n을 공백으로 변환
            story['content'] = story['content'].replace('\n', ' ')

            # 연속된 공백을 하나로
            story['content'] = ' '.join(story['content'].split())

            new_length = len(story['content'])

            if (i + 1) % 50 == 0:
                print(f"   처리 중... {i + 1}/{len(fairy_tales)}")

    print(f"✅ 줄바꿈 제거 완료!")

    # 출력 파일명 결정
    if output_file is None:
        # 입력 파일명에 '_no_newlines' 추가
        if input_file.endswith('.json'):
            output_file = input_file.replace('.json', '_no_newlines.json')
        else:
            output_file = input_file + '_no_newlines.json'

    # JSON 저장
    print(f"\n💾 저장 중: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 저장 완료!")

    return output_file


def clean_json(input_file, output_file=None):
    """
    JSON 파일 정리:
    1. ■로 시작해서 (본문 시작) 또는 (분문 시작)으로 끝나는 주석 제거
    2. 모든 \n을 공백으로 변환
    3. 연속된 공백 정리
    """

    print(f"📖 JSON 파일 읽는 중: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fairy_tales = data.get('fairy_tales', [])
    print(f"✅ 총 {len(fairy_tales)}개의 동화 로드 완료")

    # 1단계: 주석 제거
    print("\n🗑️  ■ 주석 제거 중...")
    removed_count = 0

    for story in fairy_tales:
        if 'content' in story:
            original = story['content']

            # ■로 시작해서 (본문 시작) 또는 (분문 시작)으로 끝나는 패턴 제거
            story['content'] = re.sub(
                r'■[^■]*?\((?:본문|분문)\s*시작\)',
                '',
                story['content'],
                flags=re.DOTALL
            )

            if original != story['content']:
                removed_count += 1

    print(f"✅ {removed_count}개 동화에서 주석 제거 완료")

    # 2단계: 줄바꿈 제거 및 정리
    print("\n🔄 줄바꿈 제거 및 텍스트 정리 중...")

    for i, story in enumerate(fairy_tales):
        if 'content' in story:
            # \n을 공백으로 변환
            story['content'] = story['content'].replace('\n', ' ')

            # 연속된 공백을 하나로
            story['content'] = ' '.join(story['content'].split())

            # 앞뒤 공백 제거
            story['content'] = story['content'].strip()

    print(f"✅ 텍스트 정리 완료")

    # 출력 파일명 결정
    if output_file is None:
        if input_file.endswith('.json'):
            output_file = input_file.replace('.json', '_cleaned.json')
        else:
            output_file = input_file + '_cleaned.json'

    # JSON 저장
    print(f"\n💾 저장 중: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 저장 완료: {output_file}")

    return output_file

# 실행
if __name__ == "__main__":
    print("=" * 60)
    print("JSON 줄바꿈(\\n) 제거 도구")
    print("=" * 60)

    # 입력 파일
    input_file = "../data/json/grim_bro.json"

    # 출력 파일 (선택사항)
    output_file = "../data/json/grim_bro.json"

    try:
        result = clean_json(input_file, output_file)

        print(f"\n{'=' * 60}")
        print("✅ 완료!")
        print(f"{'=' * 60}")
        print(f"출력 파일: {result}")

    except FileNotFoundError:
        print(f"\n❌ 파일을 찾을 수 없습니다: {input_file}")
    except json.JSONDecodeError:
        print(f"\n❌ JSON 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()