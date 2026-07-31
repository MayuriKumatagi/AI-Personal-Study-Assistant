import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Groq API setup
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# AI Chat Assistant
def ask_ai(question):

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"



# AI Quiz Generator
def generate_quiz(topic):

    prompt = f"""
Create 5 multiple choice questions.

Topic: {topic}

Format:

Question 1:
A)
B)
C)
D)

Correct Answer:

Make questions simple for BCA students.
"""

    return ask_ai(prompt)



# Study Recommendation
def study_recommendation(progress_data):

    prompt = f"""
Analyze this student's study progress:

{progress_data}

Give:
1. Topics to study next
2. Weak areas
3. Daily study advice
4. Improvement tips

Keep it simple.
"""

    return ask_ai(prompt)