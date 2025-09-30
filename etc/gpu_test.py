# pip install torch==2.5.1+cu118 torchvision==0.20.1+cu118 torchaudio==2.5.1+cu118 --index-url https://download.pytorch.org/whl/cu118

import torch
print("PyTorch 버전:", torch.__version__)
print("빌드된 CUDA 버전:", torch.version.cuda)
print("CUDA 사용 가능?:", torch.cuda.is_available())
print("GPU 개수:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("GPU 이름:", torch.cuda.get_device_name(0))
