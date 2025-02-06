from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"  
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

def predict_sentiment(text:str) -> str:
    inputs = tokenizer(text, return_tensors = 'pt', truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_id = logits.argmax(dim=1).item()

    star_rating = predicted_class_id + 1

    if star_rating <=2:
        return "Negative"
    elif star_rating == 3:
        return "Neutral"
    else:
        return "Positive"
