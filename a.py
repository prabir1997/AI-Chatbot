import google.generativeai as genai
import random

# Configure Gemini
genai.configure(api_key="AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0")
model = genai.GenerativeModel("gemini-2.5-flash")

# List of Python interview questions
python_questions = [
    "What is the difference between a list and a tuple in Python?",
    "Explain the concept of decorators in Python.",
    "What are Python generators and how do they work?",
    "What is the difference between shallow copy and deep copy?",
    "How does Python manage memory?",
    "Explain the concept of *args and **kwargs in Python functions.",
    "What are Python's data types?",
    "What is the difference between 'is' and '==' in Python?",
    "Explain list comprehension with an example.",
    "What is a lambda function?"
]

print("🤖 AI Interviewer: Welcome to your Python interview simulation!")
print("Type 'exit' anytime to stop.\n")

for i, question in enumerate(random.sample(python_questions, 5), start=1):
    print(f"Q{i}. {question}")
    user_answer = input("Your Answer: ")

    if user_answer.lower() in ["exit", "quit", "bye"]:
        print("Interview ended. Thank you!")
        break

    prompt = f"""
    You are a friendly AI interviewer conducting a Python interview.

    The question was:
    "{question}"

    The candidate's answer:
    "{user_answer}"

    Your task:
    1. If the answer is wrong, incomplete, or the candidate says they don’t know,
       respond kindly with a short and encouraging tone.
    2. Then, **explain the correct answer clearly in 3–4 lines**.
    3. End with a positive note and smoothly transition to the next question (like “Let’s try another one!”).
    """
    response = model.generate_content(prompt)
    print("🤖 Feedback:", response.text)
    print("-" * 80)
