import re
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# =========================
# 1. 모델/토크나이저 로드
# =========================
model_path = "sooh098/kanana-ko-rag"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"모델이 사용하는 장치: {device}")

# =========================
# 2. 입력/출력 파일
# =========================
input_path = "../data/txt/sentences_nospace.txt"
output_path = "../data/txt/sentences_corrected_kanana.txt"

# =========================
# 3. 교정용 프롬프트 설정
# =========================
instruction = """당신은 한국어 어문 규범(맞춤법, 띄어쓰기, 표준어, 문장부호 등)에 따라 문장에서 올바른 표현을 선택하세요.
답변은 반드시 고친 문장만 작성하고 이유는 쓰지 마십시오."""

# =========================
# 4. 파일 읽기
# =========================
with open(input_path, "r", encoding="utf-8") as f_in:
    lines = [line.strip() for line in f_in if line.strip()]

# =========================
# 5. 한 줄씩 교정 및 저장
# =========================
with open(output_path, "w", encoding="utf-8") as f_out:
    for idx, line in enumerate(lines, 1):
        question = f"\"{line}\" 가운데 올바른 것을 선택하세요."
        prompt = (
            "<|begin_of_text|>\n"
            f"[|system|]{instruction}<|eot_id|>\n"
            f"[|user|]문제: {question}\n정답:<|eot_id|>\n"
            "[|assistant|]"
        )

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        inputs.pop("token_type_ids", None)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id
            )

        # 결과 추출 (문장만)
        result = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        match = re.search(r'"(.*?)"', result)
        corrected_sentence = match.group(1) if match else result.strip()

        f_out.write(corrected_sentence + "\n")

        if idx % 10 == 0:
            print(f"[{idx}] lines processed...")

print(f"모든 문장 교정 완료! 결과는 {output_path}에 저장되었습니다.")
