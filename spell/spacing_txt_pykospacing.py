from pykospacing import Spacing

if __name__ == '__main__':
    # 1. 모델 초기화
    spacing = Spacing()

    # 2. 파일 경로
    input_path = '../data/txt/tales_sentences_fixed.txt'
    output_path = '../data/txt/sentences_spaced_pykospacing.txt'

    # 3. txt 불러오기
    with open(input_path, 'r', encoding='utf-8') as f:
        sentences = [line.strip() for line in f if line.strip()]
    print("txt 불러오기 완료!")

    # 4. 띄어쓰기 교정
    corrected_sentences = []
    for sentence in sentences:
        corrected = spacing(sentence)
        corrected_sentences.append(corrected)
    print("교정 완료!",corrected_sentences[:10])

    # 5. 결과 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        for s in corrected_sentences:
            f.write(s + '\n')
    print("띄어쓰기 교정 완료! 교정된 문장 수:", len(corrected_sentences))