from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_status(text: str):
    return classifier(text, ["Completed", "In Progress", "Blocked", "Planned"])