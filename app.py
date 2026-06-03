from question_generator import generate_questions, parse_questions
from resume_insights import get_resume_insights
from resume_parser import extract_text
from feedback_generator import generate_feedback
from database import init_db, save_session, get_all_sessions

import streamlit as st
import pandas as pd
import json

# Initialize tracking database storage schema
init_db()

st.set_page_config(
    page_title="AI Interview Preparation Copilot Pro",
    page_icon="🤖",
    layout="wide"
)

# Load layout stylesheets
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">🤖 AI Interview Preparation Copilot Pro</div>
    <div class="hero-subtitle">Upload your resume, deliver voice responses, and monitor historical improvements live</div>
</div>
""", unsafe_allow_html=True)

# Initialize Core Simulation Environment States
if "sim_started" not in st.session_state:
    st.session_state.sim_started = False
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "sim_answers" not in st.session_state:
    st.session_state.sim_answers = {}

def speak_text(text):
    safe_text = text.replace('"', '\\"').replace("'", "\\'")
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{safe_text}");
        var voices = window.speechSynthesis.getVoices();
        var preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('Microsoft Zira') || v.name.includes('Samantha'));
        if (preferredVoice) msg.voice = preferredVoice;
        msg.rate = 1.0; msg.pitch = 1.15;
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

# --- Helper Metrics Parser Engine ---
def parse_metrics_and_text(feedback_string):
    scores = {"Accuracy": 5.0, "Communication": 5.0, "Problem-Solving": 5.0, "Pacing": 5.0}
    clean_text = feedback_string
    try:
        if "[METRICS]" in feedback_string and "[END_METRICS]" in feedback_string:
            parts = feedback_string.split("[END_METRICS]")
            metric_block = parts[0].split("[METRICS]")[1]
            clean_text = parts[1].strip()
            
            for line in metric_block.split("\n"):
                if ":" in line:
                    k, v = line.split(":")
                    key_str = k.strip()
                    if key_str in scores or key_str == "Problem-Solving":
                        scores[key_str] = float(v.strip())
    except:
        pass
    return scores, clean_text

# --- Interface Setup Configuration Columns ---
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
with col2:
    role = st.selectbox("💼 Choose Interview Type", ["Software Engineer", "Machine Learning Engineer", "Data Analyst", "Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Scientist", "DevOps Engineer"])

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
                st.markdown(f'<div class="skill-box">✅ {skill}</div>', unsafe_allow_html=True)
        else:
            st.info("No known skills detected.")

    with right:
        st.subheader("📋 Interview Configuration")
        st.write(f"Selected Role: **{role}**")
        st.write(f"Detected Skills: **{len(skills)}**")

    st.divider()

    questions_text = generate_questions(resume_text, role)
    questions = parse_questions(questions_text)

    st.subheader("🎯 Choose Your Interview Mode")
    mode = st.radio("Select how you want to complete this interview:", ["Traditional (Text-based Layout)", "⚡ Live Simulated Interview (Voice & Audio)"], horizontal=True)
    st.divider()

    # ==================== MODE 1: TRADITIONAL MODE ====================
    if mode == "Traditional (Text-based Layout)":
        st.subheader("🤖 AI Generated Questions")
        for i, question in enumerate(questions, start=1):
            st.markdown(f'<div class="question-card"><b>Question {i}</b><br><br>{question}</div>', unsafe_allow_html=True)
            st.text_area("Your Answer", key=f"answer_{i}", height=120)

        st.divider()
        if st.button("🚀 Submit Interview", key="submit_traditional"):
            results = []
            for i, question in enumerate(questions, start=1):
                ans = st.session_state.get(f"answer_{i}", "")
                results.append({"question": question, "answer": ans})

            with st.spinner("Generating detailed core feedback analytics..."):
                raw_feedback = generate_feedback(results)
                scores, clean_feedback = parse_metrics_and_text(raw_feedback)
                save_session(role, scores["Accuracy"], scores["Communication"], scores["Problem-Solving"], scores["Pacing"], clean_feedback)

            st.balloons()
            st.subheader("📊 Performance Assessment Data")
            st.bar_chart(pd.DataFrame(list(scores.items()), columns=["Metric", "Rating out of 10"]).set_index("Metric"))
            st.subheader("🧠 Detailed Evaluator Analysis")
            st.write(clean_feedback)

    # ==================== MODE 2: SIMULATED LIVE INTERVIEW MODE ====================
    else:
        st.subheader("🎙️ Live Simulation Dashboard")
        
        # --- ADDED NOTIFICATIONS / WARNINGS ---
        st.warning("🌐 **macOS Safari Notice:** Safari security protocols block microphone inputs inside embedded windows. For the best interactive experience, please launch this app inside **Google Chrome** or **Microsoft Edge**.")
        st.info("💾 **Deployment History Note:** Because this app runs on a free cloud server hosting layer, data metrics inside the *Personal Journey Progression Tracking* graphs below may reset occasionally whenever the cloud platform reboots. (Your history logs save permanently when running locally!)")
        st.write("")

        if not st.session_state.sim_started:
            st.info("Engage in a voice-simulated live round. Your data logs safely map tracking patterns automatically.")
            if st.button("🔥 Start Live Simulation Now", type="primary"):
                st.session_state.sim_started = True
                st.session_state.current_q_idx = 0
                st.session_state.sim_answers = {}
                st.rerun()
        else:
            current_idx = st.session_state.current_q_idx
            if current_idx < len(questions):
                current_q = questions[current_idx]
                st.markdown(f"### 📋 Question {current_idx + 1} of {len(questions)}")
                st.markdown(f'<div class="question-card">{current_q}</div>', unsafe_allow_html=True)
                
                if st.button("🔊 Play / Read Question Out Loud", key=f"speak_btn_{current_idx}"):
                    speak_text(current_q)
                
                st.write("")
                js_mic_html = f"""
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; font-family: sans-serif;">
                    <p style="margin-top:0; font-weight: bold; color: #333;">Universal Microphone Controller</p>
                    <button id="start-rec-btn" style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 10px;">🔴 Start Recording</button>
                    <button id="stop-rec-btn" style="background-color: #333; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold;" disabled>⏹️ Stop</button>
                    <p id="recording-status" style="color: #777; font-style: italic; margin-top: 15px; margin-bottom: 5px;">Status: Standby</p>
                    <label style="display:block; margin-top:15px; font-weight:bold; color:#444;">Your Transcribed Response:</label>
                    <textarea id="transcript-box" style="width: 100%; height: 80px; margin-top: 5px; padding: 10px; border-radius: 4px; border: 1px solid #ccc; font-family: inherit;" placeholder="Your spoken text will appear here instantly when you click Stop..."></textarea>
                </div>
                <script>
                    const startBtn = document.getElementById('start-rec-btn');
                    const stopBtn = document.getElementById('stop-rec-btn');
                    const statusText = document.getElementById('recording-status');
                    const transcriptBox = document.getElementById('transcript-box');
                    let recognition;
                    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        recognition = new SpeechRecognition();
                        recognition.continuous = true;
                        recognition.lang = 'en-US';
                        let finalTranscript = '';
                        recognition.onstart = () => {{
                            statusText.innerHTML = "🔴 Status: Listening... Speak clearly into your mic!";
                            statusText.style.color = "#ff4b4b";
                            startBtn.disabled = true; stopBtn.disabled = false;
                            finalTranscript = ''; transcriptBox.value = '';
                        }};
                        recognition.onend = () => {{
                            statusText.innerHTML = "✅ Processing complete! Copy text into verification field below.";
                            statusText.style.color = "green";
                            startBtn.disabled = false; stopBtn.disabled = true;
                        }};
                        recognition.onresult = (event) => {{
                            for (let i = event.resultIndex; i < event.results.length; ++i) {{
                                if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript + ' ';
                            }}
                            transcriptBox.value = finalTranscript.trim();
                        }};
                        startBtn.onclick = () => {{ recognition.start(); }};
                        stopBtn.onclick = () => {{ recognition.stop(); }};
                    }} else {{
                        statusText.innerHTML = "❌ Browser Engine Support Missing.";
                    }}
                </script>
                """
                st.components.v1.html(js_mic_html, height=260)
                
                user_final_text = st.text_area("✏️ Verify / Edit your answer for the AI Reviewer:", key=f"live_text_confirmation_{current_idx}", height=100)
                
                st.write("")
                if st.button("Submit Answer & Next Question ➡️", key=f"next_btn_{current_idx}"):
                    st.session_state.sim_answers[current_idx] = user_final_text.strip() if user_final_text.strip() else "No response provided by candidate."
                    st.session_state.current_q_idx += 1
                    st.rerun()
            else:
                st.balloons()
                st.success("🎉 Live Interview Simulation Complete!")
                
                compiled_results = []
                for i, question in enumerate(questions):
                    compiled_results.append({"question": question, "answer": st.session_state.sim_answers.get(i, "")})
                
                with st.spinner("Processing automated assessment telemetry profiles..."):
                    raw_feedback = generate_feedback(compiled_results)
                    scores, clean_feedback = parse_metrics_and_text(raw_feedback)
                    save_session(role, scores["Accuracy"], scores["Communication"], scores["Problem-Solving"], scores["Pacing"], clean_feedback)
                
                st.subheader("📊 Performance Assessment Data")
                st.bar_chart(pd.DataFrame(list(scores.items()), columns=["Metric", "Rating out of 10"]).set_index("Metric"))
                
                st.subheader("🧠 AI Live Evaluation Feedback")
                st.write(clean_feedback)
                
                if st.button("Reset Simulation Mode"):
                    st.session_state.sim_started = False
                    st.session_state.current_q_idx = 0
                    st.session_state.sim_answers = {}
                    st.rerun()

    # ==================== HISTORICAL SYSTEM ANALYTICS ====================
    st.divider()
    st.subheader("📈 Personal Journey Progression Tracking")
    
    past_runs = get_all_sessions()
    if past_runs:
        history_df = pd.DataFrame(past_runs, columns=["Date", "Role", "Accuracy", "Communication", "Problem-Solving", "Pacing", "Feedback"])
        
        # Chronological progression plot
        chart_view = history_df[["Date", "Accuracy", "Communication", "Problem-Solving", "Pacing"]].set_index("Date")
        st.line_chart(chart_view)
        
        with st.expander("🗄️ View Complete Historical Session Logs"):
            for run in reversed(past_runs):
                st.markdown(f"📅 **{run[0]}** | 💼 Role: *{run[1]}*")
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Accuracy", f"{run[2]}/10")
                m_col2.metric("Communication", f"{run[3]}/10")
                m_col3.metric("Problem Solving", f"{run[4]}/10")
                m_col4.metric("Pacing", f"{run[5]}/10")
                st.caption(run[6])
                st.markdown("---")
    else:
        st.info("No recorded historical runs found yet. Data logs populate automatically on interview completions.")

    with st.expander("View Extracted Resume Text"):
        st.text(resume_text)