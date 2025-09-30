# pip install transformers[sentencepiece] accelerate
import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# =========================
# 1. 모델/토크나이저 정보
# =========================
model_name = "sionic-ai/nllb-200-ko-gec-600M"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
offload_dir = "./offload"
os.makedirs(offload_dir, exist_ok=True)

# =========================
# 2. 모델과 토크나이저 로드
# =========================
print("모델과 토크나이저를 불러오는 중...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    offload_folder=offload_dir
)

model.to(device)
model.eval()
print("모델 로드 완료!")
print(f"모델이 사용하는 장치: {device}")  # 🔹 GPU/CPU 확인

# =========================
# 3. 입력/출력 파일
# =========================
input_path = "../data/txt/sentences_spaced_pykospacing.txt"
output_path = "../data/txt/sentences_corrected_kogec.txt"

# =========================
# 4. 한 번에 배치 처리 (GPU 메모리 최적화)
# =========================
# VRAM 여유에 맞춰 배치 크기 계산
if device.type == "cuda":
    # 예시: GTX 1660 기준, 줄 수와 길이 고려
    batch_size = 16
else:
    batch_size = 1  # CPU는 한 번에 하나씩

# 입력 문장 모두 읽기
with open(input_path, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

output_lines = []

for i in range(0, len(lines), batch_size):
    batch = lines[i:i+batch_size]

    # 토큰화 + GPU 이동
    inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=False
        )

    # 디코딩 후 리스트에 저장
    for out in outputs:
        corrected = tokenizer.decode(out, skip_special_tokens=True)
        output_lines.append(corrected)

    print(f"[{i + len(batch)}] lines processed...")

# 결과 저장
with open(output_path, "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(output_lines))

print("모든 문장 교정 완료! 결과는", output_path, "에 저장되었습니다.")
