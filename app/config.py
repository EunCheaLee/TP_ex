# config.py: 경로 및 하이퍼파라미터 설정
# DATA_PATH = "data/한국어 학습용 어휘 목록.xlsx"
# MODEL_PATH = "model_weights/word_classifier.pth"
DATA_PATH = r"C:\Users\tj\Desktop\ECL\teamProject\ex\data\한국어 학습용 어휘 목록.xlsx"
MODEL_PATH = r"C:\Users\tj\Desktop\ECL\teamProject\ex\model_weights\word_classifier.pth"

# 학습/모델 설정
EMBED_DIM = 200  # 좀 더 세밀한 의미 학습
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 5e-4  # 조금 낮춰서 안정적 학습