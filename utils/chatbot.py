import re

def ask_chatbot(summary, question):

    q = question.lower()

    # ---------------- CHOLESTEROL ----------------

    if "cholesterol" in q:

        return (
            "Cholesterol is a fatty substance found in the blood. "
            "High cholesterol levels may increase the risk of heart disease and stroke. "
            "Doctors usually recommend exercise, healthy diet, and medication if required."
        )

    # ---------------- DIABETES ----------------

    elif "diabetes" in q:

        return (
            "Diabetes is a condition where blood sugar levels become too high. "
            "Common symptoms include excessive thirst, fatigue, and frequent urination. "
            "It can be managed through medication, exercise, and healthy eating."
        )

    # ---------------- FEVER ----------------

    elif "fever" in q:

        return (
            "Fever usually indicates infection or inflammation in the body. "
            "Rest, hydration, and proper medication are commonly recommended."
        )

    # ---------------- HEART ----------------

    elif "heart" in q or "bp" in q or "blood pressure" in q:

        return (
            "High blood pressure and heart-related problems should be monitored carefully. "
            "Lifestyle improvements and regular medical consultation are important."
        )

    # ---------------- CANCER ----------------

    elif "cancer" in q or "tumor" in q:

        return (
            "Cancer refers to abnormal cell growth in the body. "
            "Early diagnosis and specialist consultation are very important for treatment."
        )

    # ---------------- SUMMARY ----------------

    elif "summary" in q or "report" in q or "meaning" in q:

        return (
            f"The uploaded medical report mainly indicates: {summary}. "
            "The patient should follow medical advice and regular monitoring if symptoms continue."
        )

    # ---------------- MEDICINE ----------------

    elif "medicine" in q or "treatment" in q:

        return (
            "Medicines should always be taken according to the doctor's prescription. "
            "Do not self-medicate without professional guidance."
        )

    # ---------------- DEFAULT ----------------

    return (
        "Based on the medical report, the condition should be monitored carefully. "
        "Please consult a healthcare professional for accurate diagnosis and treatment."
    )