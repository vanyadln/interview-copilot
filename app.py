from question_generator import generate_questions, parse_questions
from resume_insights import get_resume_insights
from resume_parser import extract_text
from feedback_generator import generate_feedback

import streamlit as st
import json

st.set_page_config(
    page_title="AI Interview Preparation Copilot",
    page_icon="🤖",
    layout="wide"
)

with open("styles.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

st.markdown("""
<div class="hero">
    <div class="hero-title">
        🤖 AI Interview Preparation Copilot
    </div>
    <div class="hero-subtitle">
        Upload your resume and generate role-specific interview questions with AI
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:

    uploaded_file = st.file_uploader(
        "📄 Upload Resume (PDF)",
        type=["pdf"]
    )

with col2:

    role = st.selectbox(
        "💼 Choose Interview Type",
        [
            "Software Engineer",
            "Machine Learning Engineer",
            "Data Analyst",
            "Backend Developer",
            "Frontend Developer",
            "Full Stack Developer",
            "Data Scientist",
            "DevOps Engineer"
        ]
    )

st.divider()

if uploaded_file:

    st.success("Resume uploaded successfully!")

    resume_text = extract_text(uploaded_file)

    skills = get_resume_insights(resume_text)

    left, right = st.columns([1, 2])

    with left:

        st.subheader("🛠 Detected Skills")

        if skills:

            for skill in skills:

                st.markdown(
                    f"""
                    <div class="skill-box">
                    ✅ {skill}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "No known skills detected."
            )

    with right:

        st.subheader(
            "📋 Interview Configuration"
        )

        st.write(
            f"Selected Role: **{role}**"
        )

        st.write(
            f"Detected Skills: **{len(skills)}**"
        )

    st.divider()

    questions_text = generate_questions(
        resume_text,
        role
    )

    questions = parse_questions(
        questions_text
    )

    st.subheader(
        "🤖 AI Generated Questions"
    )

    for i, question in enumerate(
        questions,
        start=1
    ):

        st.markdown(
            f"""
            <div class="question-card">
            <b>Question {i}</b><br><br>
            {question}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.text_area(
            "Your Answer",
            key=f"answer_{i}",
            height=120
        )

    st.divider()

    if st.button(
        "🚀 Submit Interview"
    ):

        total_answers = 0

        results = []

        for i, question in enumerate(
            questions,
            start=1
        ):

            answer = st.session_state.get(
                f"answer_{i}",
                ""
            )

            if answer.strip():

                total_answers += 1

            results.append(
                {
                    "question": question,
                    "answer": answer
                }
            )

        with open(
            "results.json",
            "w"
        ) as f:

            json.dump(
                results,
                f,
                indent=4
            )

        with st.spinner(
            "Generating AI feedback..."
        ):

            feedback = generate_feedback(
                results
            )

        with open(
            "feedback.txt",
            "w"
        ) as f:

            f.write(
                feedback
            )

        completion_score = int(
            (
                total_answers
                / len(questions)
            ) * 100
        )

        st.divider()

        st.subheader(
            "📊 Interview Summary"
        )

        metric1, metric2 = st.columns(
            2
        )

        with metric1:

            st.metric(
                "Questions Answered",
                f"{total_answers}/{len(questions)}"
            )

        with metric2:

            st.metric(
                "Completion Score",
                f"{completion_score}%"
            )

        st.divider()

        st.subheader(
            "🧠 AI Interview Feedback"
        )

        st.write(
            feedback
        )

        st.download_button(
            label="📄 Download Feedback Report",
            data=feedback,
            file_name="interview_feedback.txt",
            mime="text/plain"
        )

    with st.expander(
        "View Extracted Resume Text"
    ):

        st.text(
            resume_text
        )