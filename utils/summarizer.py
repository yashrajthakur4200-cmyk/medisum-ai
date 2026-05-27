import re

# ---------------- SUMMARY ----------------

def summarize_text(text):

    sentences = text.split(".")

    summary = ". ".join(sentences[:3])

    return summary.strip()


# ---------------- KEYWORDS ----------------

def extract_keywords(text):

    words = re.findall(r'\b\w+\b', text.lower())

    common = []

    for word in words:

        if len(word) > 5 and word not in common:
            common.append(word)

    return common[:8]


# ---------------- ENTITIES ----------------

def extract_entities_from_text(text):

    entities = []

    keywords = [
        "fever",
        "diabetes",
        "cholesterol",
        "heart",
        "cancer",
        "bp",
        "infection"
    ]

    text_lower = text.lower()

    for word in keywords:

        if word in text_lower:
            entities.append(word)

    return entities


# ---------------- QUALITY SCORE ----------------

def calculate_quality_score():

    return 87


# ---------------- SEVERITY ----------------

def calculate_severity_score(text):

    text = text.lower()

    high_words = [
        "cancer",
        "tumor",
        "heart attack",
        "stroke"
    ]

    moderate_words = [
        "cholesterol",
        "diabetes",
        "hypertension"
    ]

    for word in high_words:

        if word in text:

            return {
                "level": "High",
                "score": 85
            }

    for word in moderate_words:

        if word in text:

            return {
                "level": "Moderate",
                "score": 60
            }

    return {
        "level": "Low",
        "score": 30
    }


# ---------------- RECOMMENDATION ----------------

def doctor_recommendation(level):

    if level == "High":
        return "Immediate specialist consultation recommended."

    elif level == "Moderate":
        return "Regular monitoring and consultation advised."

    else:
        return "General health maintenance recommended."


# ---------------- DOCTOR SUGGESTION ----------------

def suggest_doctors(level):

    if level == "High":

        return {
            "specialty": "Cardiologist / Oncologist",
            "doctors": [
                "Dr. Sharma",
                "Dr. Mehta"
            ]
        }

    elif level == "Moderate":

        return {
            "specialty": "General Physician",
            "doctors": [
                "Dr. Verma",
                "Dr. Kapoor"
            ]
        }

    else:

        return {
            "specialty": "General Checkup",
            "doctors": [
                "Dr. Singh"
            ]
        }


# ---------------- MODEL LOADER ----------------

def force_load_model():
    return True