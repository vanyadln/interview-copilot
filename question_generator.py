import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_questions(resume_text, role):

    prompt = f"""
You are an experienced interviewer.

Candidate Resume:
{resume_text}

Target Role:
{role}

Generate exactly 10 interview questions.

Rules:
- Mix technical and behavioral questions
- Focus on resume projects and skills
- Match the target role
- Return only questions
- One question per line
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


def parse_questions(text):

    questions = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if (
            len(line) > 2
            and line[0].isdigit()
            and "." in line
        ):
            line = line.split(
                ".",
                1
            )[1].strip()

        questions.append(
            line
        )

    return questions