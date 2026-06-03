import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_feedback(results):

    interview_text = ""

    for item in results:

        interview_text += f"""
Question:
{item['question']}

Answer:
{item['answer']}

"""

    prompt = f"""
You are a senior technical interviewer.

Evaluate this interview.

Provide:

1. Overall Score out of 10
2. Strengths
3. Weaknesses
4. Topics to Improve
5. Final Hiring Recommendation

Interview:

{interview_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content