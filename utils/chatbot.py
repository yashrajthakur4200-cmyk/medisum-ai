from google import genai

# ---------------- GEMINI CLIENT ----------------

client = genai.Client(api_key="YOUR_API_KEY")

# ---------------- SMART CHATBOT ----------------

def ask_chatbot(summary, question):

    q = question.lower()

    # -------- BASIC MEDICAL RESPONSES --------

    if "cholesterol" in q or "cholestrol" in q:
        return """
Cholesterol is a fatty substance present in the blood. 
High cholesterol levels can increase the risk of heart disease and stroke. 
Doctors usually recommend exercise, healthy diet, and medications if necessary.
"""

    elif "diabetes" in q or "sugar" in q:
        return """
Diabetes is a medical condition where blood sugar levels become too high. 
It may require lifestyle changes, regular monitoring, exercise, and medication.
"""

    elif "blood pressure" in q or "bp" in q:
        return """
Blood pressure refers to the force of blood flowing through arteries. 
High BP can increase risks of heart disease and should be monitored regularly.
"""

    elif "fever" in q:
        return """
Fever is usually a sign of infection or inflammation. 
Hydration, rest, and prescribed medicines are commonly recommended.
"""

    elif "what does this report say" in q or "report meaning" in q:
        return f"""
According to the uploaded medical report summary:

{summary}

Please consult a healthcare professional for accurate diagnosis and treatment guidance.
"""

    # -------- AI FALLBACK --------

    try:

        prompt = f"""
You are MediSum AI, a healthcare assistant.

Medical Report Summary:
{summary}

User Question:
{question}

Give a professional and simple medical response.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except:

        return """
MediSum AI could not access advanced AI services currently. 
However, based on the medical report, regular monitoring and consultation with a healthcare professional is recommended.
"""