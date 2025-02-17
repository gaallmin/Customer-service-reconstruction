from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "nlp04/korean_sentiment_analysis_kcelectra"  
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
# print(model.config.id2label)

id2label = model.config.id2label if hasattr(model.config, "id2label") else {
    0: '기쁨(행복한)', 1: '고마운', 2: '설레는(기대하는)', 3: '사랑하는', 4: '즐거운(신나는)',
    5: '일상적인', 6: '생각이 많은', 7: '슬픔(우울한)', 8: '힘듦(지침)', 9: '짜증남', 10: '걱정스러운(불안한)'
}


def predict_sentiments(texts: list) -> list: # batch processing
    inputs = tokenizer(texts, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_ids = logits.argmax(dim=1).tolist()
    return [id2label.get(cid, "Unknown") for cid in predicted_class_ids]