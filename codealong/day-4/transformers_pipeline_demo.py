from transformers import pipeline

print("=== Pipeline Stages & Tasks ===\n")
print("Stages: Load model & tokenizer → Preprocess input → Infer → Postprocess")

# Pipeline stages: 1) Load model & tokenizer, 2) Preprocess input, 3) Model inference, 4) Postprocess output

print("--- QUESTION ANSWERING ---")
# Stage 1: Load pipeline
qa_pipe = pipeline("question-answering", model="deepset/roberta-base-squad2")
# Stage 2-4: Execute pipeline
result = qa_pipe(question="What is Transformers?", 
                context="Transformers is a library by Hugging Face for NLP tasks.")
print(f"Q: What is Transformers?")
print(f"A: {result['answer']}\n")

print("--- SUMMARIZATION ---")
# Stage 1: Load pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
# Stage 2-4: Execute pipeline
text = "Artificial intelligence (AI) is intelligence demonstrated by machines. Leading AI textbooks define the field as the study of intelligent agents that perceive their environment and take actions to achieve goals."
summary = summarizer(text)
print(f"Summary: {summary[0]['summary_text']}\n")

print("--- TRANSLATION ---")
# Stage 1: Load pipeline
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")
# Stage 2-4: Execute pipeline
translation = translator("Hello, how are you today?")
print(f"EN→ES: {translation[0]['translation_text']}\n")

print("--- SENTIMENT ANALYSIS ---")
# Stage 1: Load pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# Stage 2-4: Execute pipeline
texts = ["I love this movie!", "This is terrible.", "It's okay."]
for text in texts:
    result = sentiment_analyzer(text)[0]
    print(f"'{text}': {result['label']} ({result['score']:.3f})")
print()

print("--- NAMED ENTITY RECOGNITION ---")
# Stage 1: Load pipeline
ner_pipe = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
# Stage 2-4: Execute pipeline
entities = ner_pipe("Apple Inc. CEO Tim Cook announced new products in Cupertino, California.")
print(f"Entities: {[(e['word'], e['entity_group']) for e in entities]}")