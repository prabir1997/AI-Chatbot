import google.generativeai as genai
from django.conf import settings
import re 
import json
# Load API key from settings.py
genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def evaluate_answer(question_text: str, user_answer: str):
    """
    Send a question and user answer to Gemini and return
    feedback text and a numeric score (0–10).
    """
    prompt = f"""
    You are a Python interviewer evaluating a candidate.

    Question:
    {question_text}

    Candidate Answer:
    {user_answer}

    Tasks:
    1. Give short, friendly feedback (max 4–5 lines).
    2. Rate correctness from 0 to 10 based on clarity and accuracy.
    3. Return result in this JSON format:

    {{
      "feedback": "your short explanation",
      "score": number_between_0_and_10
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Simple JSON parsing fallback
        # import json
        # 🧹 Clean markdown fences if Gemini adds them
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()
        try:
            data = json.loads(text)
            feedback = data.get("feedback", "")
            score = float(data.get("score", 0))
        except Exception:
            # If response not pure JSON, return raw text
            feedback = text
            score = 0

        return {"feedback": feedback, "score": score}

    except Exception as e:
        return {"feedback": f"Error: {str(e)}", "score": 0}
