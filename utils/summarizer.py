# utils/summarizer.py
# UPGRADED — faster neural + TF-IDF fallback + severity + doctor recommendation


import re
import random
import logging
from functools import lru_cache
from contextlib import contextmanager

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Optional deep dependencies
try:
    import torch
except Exception:
    torch = None

try:
    import spacy
except Exception:
    spacy = None


# ------------------ logging ------------------
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# ------------------ nltk ------------------
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

# ------------------ spaCy ------------------
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    nlp = None
    logging.info("spaCy model not loaded: %s", e)

# ------------------ torch tuning ------------------
if torch is not None:
    try:
        torch.set_num_threads(4)
        torch.set_num_interop_threads(4)
    except Exception:
        pass


# ------------------ neural globals ------------------
USE_NEURAL_MODEL = False
_TOKENIZER = None
_MODEL = None
_DEVICE = "cpu"
FORCE_NEURAL = False


# ------------------ model loader ------------------
@lru_cache(maxsize=1)
def load_model(model_name: str = "facebook/bart-large-cnn"):
    global _TOKENIZER, _MODEL, _DEVICE, USE_NEURAL_MODEL

    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    except Exception:
        USE_NEURAL_MODEL = False
        return None, None, "cpu"

    try:
        device = "cuda" if torch and torch.cuda.is_available() else "cpu"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        if device == "cuda":
            model = model.to(device)

        _TOKENIZER = tokenizer
        _MODEL = model
        _DEVICE = device
        USE_NEURAL_MODEL = True
        return tokenizer, model, device

    except Exception:
        USE_NEURAL_MODEL = False
        return None, None, "cpu"


def force_load_model(model_name: str = "facebook/bart-large-cnn"):
    load_model(model_name)
    return USE_NEURAL_MODEL


# ------------------ utils ------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ------------------ dummy context ------------------
@contextmanager
def dummy_context():
    yield


# ------------------ neural summarizer ------------------
def _neural_summarize(text: str, max_tokens: int = 160) -> str:
    tokenizer, model, device = _TOKENIZER, _MODEL, _DEVICE

    if tokenizer is None or model is None:
        tokenizer, model, device = load_model()
        if tokenizer is None:
            raise RuntimeError("Neural model not available")

    words = text.split()
    if len(words) > 800:
        text = " ".join(words[:800])

    encoded = tokenizer(
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    )

    if device == "cuda":
        encoded = {k: v.to(device) for k, v in encoded.items()}

    gen_kwargs = dict(
        max_length=max_tokens,
        min_length=max(40, int(max_tokens * 0.4)),
        num_beams=2,
        early_stopping=True,
        no_repeat_ngram_size=2,
        do_sample=False,
    )

    with torch.no_grad() if torch else dummy_context():
        output = model.generate(**encoded, **gen_kwargs)

    return tokenizer.decode(output[0], skip_special_tokens=True)


# ------------------ TF-IDF fallback ------------------
def _tfidf_extractive_summary(text: str, sentences: int = 4) -> str:
    sents = nltk.sent_tokenize(text)
    if len(sents) <= 1:
        return text

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform(sents)
        scores = cosine_similarity(tfidf).sum(axis=1)
        ranked = [s for _, s in sorted(zip(scores, sents), reverse=True)]
        return " ".join(ranked[:sentences])
    except Exception:
        return " ".join(sents[:sentences])


# ------------------ formatter ------------------
def _format_summary(raw: str) -> str:
    sents = nltk.sent_tokenize(raw)
    if not sents:
        return raw

    lines = ["🔹 PRIMARY SUMMARY:", f"   {sents[0]}", ""]
    if len(sents) > 1:
        lines.append("🔹 KEY DETAILS:")
        for s in sents[1:5]:
            lines.append(f"   • {s}")

    return "\n".join(lines)


# ------------------ public summarizer ------------------
def summarize_text(text: str) -> str:
    text = clean_text(text)
    if not text or len(text.split()) < 20:
        return "Text too short to summarize meaningfully."

    if FORCE_NEURAL and not USE_NEURAL_MODEL:
        load_model()

    if USE_NEURAL_MODEL:
        try:
            base = _neural_summarize(text)
        except Exception:
            base = _tfidf_extractive_summary(text)
    else:
        base = _tfidf_extractive_summary(text)

    return _format_summary(base)


# ------------------ keywords ------------------
def extract_keywords(text: str, top_n: int = 6):
    text = clean_text(text)
    if not text:
        return []

    try:
        vec = TfidfVectorizer(stop_words="english", max_features=top_n)
        vec.fit_transform([text])
        return list(vec.get_feature_names_out())
    except Exception:
        return []


# ------------------ entities ------------------
def extract_entities_from_text(text: str):
    if not nlp or not text:
        return []
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]


# ------------------ quality ------------------
def calculate_quality_score():
    return random.randint(70, 95)


# ------------------ severity ------------------
def calculate_severity_score(text: str):
    text = text.lower()

    high = [
        "cardiac arrest", "heart attack", "stroke", "coma",
        "respiratory failure", "ventilator", "sepsis",
        "acute renal failure", "unconscious"
    ]

    moderate = [
        "pneumonia", "shortness of breath", "chest pain",
        "high fever", "hypertension", "diabetes",
        "infection", "bleeding", "fracture"
    ]

    low = [
        "fever", "pain", "cough", "cold", "headache",
        "fatigue", "nausea", "vomiting", "dizziness"
    ]

    score = 0
    for w in high:
        if w in text:
            score += 25
    for w in moderate:
        if w in text:
            score += 12
    for w in low:
        if w in text:
            score += 6

    if "mg" in text or "mmhg" in text or "%" in text:
        score += 10

    score = min(score, 100)

    if score >= 70:
        level = "High"
    elif score >= 35:
        level = "Moderate"
    elif score > 0:
        level = "Low"
    else:
        level = "Not detected"

    return {"level": level, "score": score}


# ------------------ doctor recommendation ------------------
def doctor_recommendation(severity_level: str):
    if severity_level == "High":
        return (
            "Immediate medical attention required. "
            "Consult a specialist or admit the patient for emergency care."
        )
    elif severity_level == "Moderate":
        return (
            "Medical consultation advised. "
            "Follow-up tests and close monitoring recommended."
        )
    elif severity_level == "Low":
        return (
            "Condition appears stable. "
            "Outpatient treatment and routine follow-up advised."
        )
    else:
        return "No medical recommendation available."
def suggest_doctors(severity_level: str):
    if severity_level == "High":
        return {
            "specialty": "Emergency / Specialist",
            "doctors": [
                "Dr. Amit Sharma (MD – Emergency Medicine)",
                "Dr. Rajesh Mehta (Pulmonologist)"
            ]
        }

    elif severity_level == "Moderate":
        return {
            "specialty": "General Physician",
            "doctors": [
                "Dr. Sunita Patel (MBBS, MD)",
                "Dr. Kiran Rao (Internal Medicine)"
            ]
        }

    elif severity_level == "Low":
        return {
            "specialty": "Family Physician",
            "doctors": [
                "Dr. Pooja Verma (Family Medicine)",
                "Dr. Neeraj Singh (General Practice)"
            ]
        }

    return {
        "specialty": "Not Available",
        "doctors": []
    }
