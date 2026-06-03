import os
from groq import Groq
import streamlit as st

def generate_feedback(results):
    """Calls Groq LLaMA models to extract clean evaluation metrics and prose reports."""
    
    # --- FIX: Safe Secrets / Environment Variable Fallback Engine ---
    groq_key = None
    
    try:
        # Check if running on Streamlit Cloud or if local secrets file exists
        if "GROQ_API_KEY" in st.secrets:
            groq_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        # If st.secrets throws an error locally because the file doesn't exist, ignore it
        pass

    # If st.secrets wasn't found, fallback to your local computer's environment variables
    if not groq_key:
        groq_key = os.environ.get("GROQ_API_KEY")

    # If it is still missing completely, show a friendly warning instead of crashing
    if not groq_key:
        return (
            "[METRICS]\nAccuracy: 0.0\nCommunication: 0.0\nProblem-Solving: 0.0\nPacing: 0.0\n[END_METRICS]\n\n"
            "⚠️ **API Key Missing:** Please make sure `GROQ_API_KEY` is set in your environment variables locally, "
            "or added to your Streamlit Community Cloud Secrets dashboard."
        )

    # Initialize connection using the safely retrieved key
    client = Groq(api_key=groq_key)

    # Build evaluation system prompt matrix
    prompt = (
        "You are an expert technical interviewer. Analyze the provided candidate responses. "
        "You MUST start your response with an evaluation block format strictly matching the placeholder structure below. "
        "Do not alter the labels. Use realistic score values out of 10.0 based on response accuracy:\n"
        "[METRICS]\n"
        "Accuracy: X.X\n"
        "Communication: X.X\n"
        "Problem-Solving: X.X\n"
        "Pacing: X.X\n"
        "[END_METRICS]\n\n"
        "Follow the metrics section with a professional, detailed written breakdown detailing "
        "strengths and specific guidance for conceptual improvements.\n\n"
        "Here are the questions and responses:\n"
    )

    for item in results:
        prompt += f"Question: {item['question']}\nResponse Provided: {item['answer']}\n\n"

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[METRICS]\nAccuracy: 5.0\nCommunication: 5.0\nProblem-Solving: 5.0\nPacing: 5.0\n[END_METRICS]\n\nError calling model execution layers: {e}"
    