import requests
import time
import os

def collect_all_advice(file_path="advice.txt", delay=0.5, max_retry=1000):
    url = "https://korean-advice-open-api.vercel.app/api/advice"

    # 기존 파일 읽어서 중복 방지
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            collected = set(line.strip() for line in f if line.strip())
    else:
        collected = set()

    print(f"현재까지 수집된 명언: {len(collected)} 개")

    retry = 0
    while retry < max_retry:  # 너무 무한루프 안 돌게 안전장치
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            advice = data.get("message")
            if advice and advice not in collected:
                collected.add(advice.strip())
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(advice.strip() + "\n")
                print(f"[{len(collected)}] 새 명언 저장: {advice}")
                retry = 0  # 새로운 게 나오면 다시 카운터 초기화
            else:
                retry += 1  # 중복이면 시도 횟수 증가
                print(f"중복 발생 ({retry}/{max_retry})")
        else:
            retry += 1
            print(f"요청 실패 {response.status_code} ({retry}/{max_retry})")

        time.sleep(delay)

    print("🔚 더 이상 새로운 명언을 못 찾았거나, 최대 시도 횟수에 도달했습니다.")
    print(f"최종 수집된 명언 개수: {len(collected)}")

if __name__ == "__main__":
    collect_all_advice(file_path="../data/advice.txt", delay=0.5, max_retry=200)
