from google import genai

# ---------------- API KEY ----------------

client = genai.Client(api_key="AIzaSyDvwcJJt08aNefN3Mj2l0mcXm2_C93dODs")

# ---------------- CHATBOT ----------------

def ask_chatbot(summary, question):

    prompt = f"""
    You are MediSum AI, an intelligent healthcare assistant.

    Medical Report Summary:
    {summary}

    User Question:
    {question}

    Give a professional, medically informative, and easy-to-understand response.
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return f"AI Error: {str(e)}"