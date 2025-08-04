import re
import torch
from transformers import CamembertTokenizerFast, CamembertForTokenClassification

# === 1. Chargement du modèle ===
MODEL_DIR = r"D:/camembert_ner_d14/results/checkpoint-735"
tokenizer = CamembertTokenizerFast.from_pretrained(MODEL_DIR)
model = CamembertForTokenClassification.from_pretrained(MODEL_DIR)
model.eval()

# === 2. Label mapping ===
label2id = {
    "O": 0, "B-title": 1, "I-title": 2, "B-experience": 3, "I-experience": 4,
    "B-education": 5, "I-education": 6, "B-hard_skills": 7, "I-hard_skills": 8,
    "B-soft_skills": 9, "I-soft_skills": 10, "B-language": 11, "I-language": 12,
    "B-location": 13, "I-location": 14
}
id2label = {v: k for k, v in label2id.items()}

def simple_word_tokenize(text):
    return re.findall(r"\w+[\w\-’']*|[^\w\s]", text, flags=re.UNICODE)

def join_tokens(tokens):
    text = ""
    for t in tokens:
        if re.match(r"^[.,;:!?]$", t):
            text = text.rstrip() + t + " "
        else:
            text += t + " "
    return text.strip()

def predict_entities_from_words(words):
    encoded = tokenizer(words, is_split_into_words=True, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**encoded).logits
    predictions = torch.argmax(logits, dim=-1).squeeze(0).tolist()
    word_ids = encoded.word_ids(batch_index=0)

    word_level_labels = []
    seen = set()
    for idx, w_id in enumerate(word_ids):
        if w_id is not None and w_id not in seen:
            seen.add(w_id)
            label_name = id2label[predictions[idx]]
            word_level_labels.append((words[w_id], label_name))

    entities = []
    current_tokens = []
    current_label_type = None

    def flush():
        nonlocal current_tokens, current_label_type, entities
        if current_tokens and current_label_type:
            entities.append({
                'text': [join_tokens(current_tokens)],
                'label': current_label_type.replace('_', ' ').lower()
            })
        current_tokens = []
        current_label_type = None

    for word, full_label in word_level_labels:
        if full_label == "O":
            flush()
            continue
        prefix, ent_type = full_label.split('-', 1)
        if prefix == 'B':
            flush()
            current_tokens = [word]
            current_label_type = ent_type
        elif prefix == 'I':
            if current_label_type == ent_type:
                current_tokens.append(word)
            else:
                flush()
                current_tokens = [word]
                current_label_type = ent_type
    flush()
    return entities

def merge_adjacent_entities(entities):
    if not entities:
        return []
    merged = []
    current = entities[0]
    for ent in entities[1:]:
        if ent['label'] == current['label']:
            current['text'][0] += ' ' + ent['text'][0]
        else:
            merged.append(current)
            current = ent
    merged.append(current)
    return merged
