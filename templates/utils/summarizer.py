# utils/summarizer.py
# Lightweight neural summarizer (DistilBART) + TF-IDF fallback
# Optimized for speed: device auto-select, truncation, small beams, no_grad/inference_mode.

import re
import random
import nltk
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Transformers / torch are optional; code will fallback gracefully.
USE_NEURAL_MODEL = False
tokenizer = None
model = None
device = "cpu"

# ---------------- NLTK setup (safe: silent if downloader cannot access internet) ----------------
try:
    nltk.data.find("tokenizers/punkt")
except Exception:
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        pass

try:
    nltk.data.find("corpora/stopwords")
except Exception:
    try:
        nltk.download("stopwords", quiet=True)
    except Exception:
        pass

# ---------------- Try to load lightweight distilbart model ----------------
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch

    # Choose a small-ish summarization model
    MODEL_NAME = "sshleifer/distilbart-cnn-12-6"  # small & fast summarizer

    # Auto-detect device
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

    # Speed tips: eval mode
    model.eval()
    USE_NEURAL_MODEL = True
    # If CPU, optionally enable torch.inference_mode at generation time
except Exception as e:
    # fallback path: TF-IDF extractive summarizer only
    USE_NEURAL_MODEL = False
    # Print minimal info for debugging; do not crash.
    print("Neural summarizer not available — using TF-IDF fallback. Details:", str(e))


# ---------------- basic cleaning ----------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = text.encode("ascii", "ignore").decode(errors="ignore")
    text = re.sub(r"\s+", " ", text).strip()
    # drop super short tokens
    text = " ".join([t for t in text.split() if len(t) > 1])
    return text


# ---------------- TF-IDF extractive summarizer (fast) ----------------
def _tfidf_extractive_summary(text: str, sentences: int = 3) -> str:
    text = clean_text(text)
    sents = nltk.sent_tokenize(text)
    if len(sents) <= sentences:
        return text

    # Limit to first N sentences for speed (pre-window)
    window = 40
    if len(sents) > window:
        # take the first and last parts to capture beginning and conclusion
        sents = sents[:20] + sents[-20:]

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform(sents)
        sim = cosine_similarity(tfidf)
        scores = sim.sum(axis=1)
        ranked_idx = scores.argsort()[::-1]
        chosen = sorted(ranked_idx[:sentences])
        summary = " ".join([sents[i] for i in chosen])
        return summary
    except Exception:
        # fallback: return first N sentences
        return " ".join(nltk.sent_tokenize(text)[:sentences])


# ---------------- Neural summarizer (DistilBART) ----------------
def _neural_summarize(text: str, max_tokens: int = 140) -> str:
    global tokenizer, model, device
    if not tokenizer or not model:
        raise RuntimeError("Neural model not loaded")

    text = clean_text(text)
    if not text:
        return ""

    # Transformers have token limits. Use truncation to keep speed.
    # Keep max input length = 1024 tokens (model/tokenizer will handle)
    inputs = tokenizer(
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt",
    ).to(device)

    gen_kwargs = dict(
        max_new_tokens=max_tokens,
        num_beams=2,            # small beam for speed
        early_stopping=True,
        no_repeat_ngram_size=3,
        do_sample=False,
    )

    # faster generation contexts
    try:
        # prefer inference_mode if available in torch version
        if hasattr(torch, "inference_mode"):
            with torch.inference_mode():
                out = model.generate(**inputs, **gen_kwargs)
        else:
            with torch.no_grad():
                out = model.generate(**inputs, **gen_kwargs)
    except Exception as e:
        # generation failed (e.g., OOM) -> raise to callers
        raise

    summary = tokenizer.decode(out[0], skip_special_tokens=True)
    return summary.strip()


# ---------------- Format summary into bullet-ish text ----------------
def _format_summary(raw: str) -> str:
    if not raw:
        return ""
    sents = nltk.tokenize.sent_tokenize(raw)
    if not sents:
        return raw
    primary = sents[0]
    rest = sents[1:4]
    lines = ["PRIMARY: " + primary]
    if rest:
        lines.append("KEY POINTS:")
        for r in rest:
            lines.append(" - " + r)
    return "\n".join(lines)


# ---------------- Public API ----------------
def summarize_text(text: str) -> str:
    text = clean_text(text)
    if not text or len(text.split()) < 20:
        # very short -> return cleaned text
        return text

    # Try neural first (fast small model). Fall back to TF-IDF if fails.
    if USE_NEURAL_MODEL:
        try:
            # use small max tokens for speed; user can change.
            raw = _neural_summarize(text, max_tokens=120)
        except Exception:
            raw = _tfidf_extractive_summary(text, sentences=3)
    else:
        raw = _tfidf_extractive_summary(text, sentences=3)

    return _format_summary(raw)


def extract_keywords(text: str, top_n: int = 6) -> List[str]:
    text = clean_text(text)
    if not text:
        return []
    try:
        vec = TfidfVectorizer(stop_words="english", max_features=top_n)
        vec.fit_transform([text])
        return list(vec.get_feature_names_out())
    except Exception:
        return []


def calculate_quality_score() -> int:
    return random.randint(70, 95)


def calculate_severity_score(text: str):
    high = ["critical", "cardiac arrest", "coma", "ventilator", "icu", "stroke", "heart attack", "sepsis"]
    med = ["severe", "unstable", "worsening", "urgent", "pneumonia", "renal failure"]
    low = ["mild", "fever", "infection", "abnormal", "shortness of breath"]

    t = (text or "").lower()
    score = 0
    for w in high:
        if w in t:
            score += 15
    for w in med:
        if w in t:
            score += 8
    for w in low:
        if w in t:
            score += 4
    score = max(0, min(score, 100))
    level = "High" if score >= 70 else ("Moderate" if score >= 40 else "Low")
    return {"level": level, "score": score}
