def ask_chatbot(summary, question):

    question = question.lower()

    # CHOLESTEROL
    if "cholesterol" in question:
        return (
            "High cholesterol means excess fatty substances "
            "in the blood which may increase heart disease risk."
        )

    # FEVER
    elif "fever" in question:
        return (
            "Fever usually indicates infection or inflammation. "
            "Proper hydration and medication are important."
        )

    # DIABETES
    elif "diabetes" in question:
        return (
            "Diabetes is a condition where blood sugar levels "
            "remain higher than normal."
        )

    # HEART
    elif "heart" in question:
        return (
            "Heart-related problems may require consultation "
            "with a cardiologist for further evaluation."
        )

    # REPORT MEANING
    elif "report" in question or "summary" in question:
        return (
            "This medical report indicates the patient's "
            "current health condition based on symptoms, "
            "diagnosis, and prescribed treatment."
        )

    # DEFAULT
    else:
        return (
            "Based on the uploaded medical report, "
            "further clinical evaluation may be recommended."
        )