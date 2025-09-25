from transformers import pipeline

fill_mask = pipeline("fill-mask",
                     model="bert-base-uncased",
                     tokenizer="bert-base-uncased")

result = fill_mask("인생이란 자신을 [MASK] 것이 아니라 자신을 만드는 것이다.")
for r in result:
    print(r["sequence"], r["score"])