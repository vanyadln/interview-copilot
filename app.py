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

# Load custom styling layout
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

# Initialize Session States for the Live Simulation Trackers
if "sim_started" not in st.session_state:
    st.session_state.sim_started = False
if "current_q_idx" not in st.session_state:
    st.session_state.current_q_idx = 0
if "sim_answers" not in st.session_state:
    st.session_state.sim_answers = {}

# --- TEXT TO SPEECH COMPONENT ---
def speak_text(text):
    """Embeds safe Javascript voice engine that bypasses browser permission lockouts."""
    safe_text = text.replace('"', '\\"').replace("'", "\\'")
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{safe_text}");
        var voices = window.speechSynthesis.getVoices();
        var preferredVoice = voices.find(v => 
            v.name.includes('Google US English') || 
            v.name.includes('Microsoft Zira') || 
            v.name.includes('Samantha')
        );
        if (preferredVoice) msg.voice = preferredVoice;
        msg.rate = 1.0; 
        msg.pitch = 1.15; 
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

# --- RESUME UPLOAD SECTION ---
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
            st.info("No known skills detected.")

    with right:
        st.subheader("📋 Interview Configuration")
        st.write(f"Selected Role: **{role}**")
        st.write(f"Detected Skills: **{len(skills)}**")

    st.divider()

    # Generate and parse questions from your backend modules
    questions_text = generate_questions(resume_text, role)
    questions = parse_questions(questions_text)

    # --- Mode Selection Toggle Block ---
    st.subheader("🎯 Choose Your Interview Mode")
    mode = st.radio(
        "Select how you want to complete this interview:",
        ["Traditional (Text-based Layout)", "⚡ Live Simulated Interview (Voice & Audio)"],
        horizontal=True
    )
    
    st.divider()

    # ==================== MODE 1: TRADITIONAL TEXT MODE ====================
    if mode == "Traditional (Text-based Layout)":
        st.subheader("🤖 AI Generated Questions")
        
        for i, question in enumerate(questions, start=1):
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

        if st.button("🚀 Submit Interview", key="submit_traditional"):
            total_answers = 0
            results = []

            for i, question in enumerate(questions, start=1):
                answer = st.session_state.get(f"answer_{i}", "")
                if answer.strip():
                    total_answers += 1
                results.append({"question": question, "answer": answer})

            with open("results.json", "w") as f:
                json.dump(results, f, indent=4)

            with st.spinner("Generating AI feedback..."):
                feedback = generate_feedback(results)

            with open("feedback.txt", "w") as f:
                f.write(feedback)

            completion_score = int((total_answers / len(questions)) * 100)

            st.divider()
            st.subheader("📊 Interview Summary")
            metric1, metric2 = st.columns(2)
            with metric1:
                st.metric("Questions Answered", f"{total_answers}/{len(questions)}")
            with metric2:
                st.metric("Completion Score", f"{completion_score}%")

            st.divider()
            st.subheader("🧠 AI Interview Feedback")
            st.write(feedback)

            st.download_button(
                label="📄 Download Feedback Report",
                data=feedback,
                file_name="interview_feedback.txt",
                mime="text/plain"
            )

    # ==================== MODE 2: SIMULATED LIVE INTERVIEW MODE ====================
    else:
        st.subheader("🎙️ Live Simulation Dashboard")
        
        if not st.session_state.sim_started:
            st.info("In this mode, you will interact with the AI using your voice. Click below to start.")
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
                
                # Voice Reader Button
                if st.button("🔊 Play / Read Question Out Loud", key=f"speak_btn_{current_idx}"):
                    speak_text(current_q)
                
                st.write("")
                
                # --- IFRAME-PROOF JAVASCRIPT AUDIO ENGINE ---
                st.markdown("#### 🎤 Answer Voice Recorder")
                
                js_mic_html = f"""
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; font-family: sans-serif;">
                    <p style="margin-top:0; font-weight: bold; color: #333;">Universal Microphone Controller</p>
                    <button id="start-rec-btn" style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; margin-right: 10px;">🔴 Start Recording</button>
                    <button id="stop-rec-btn" style="background-color: #333; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold;" disabled>⏹️ Stop</button>
                    
                    <p id="recording-status" style="color: #777; font-style: italic; margin-top: 15px; margin-bottom: 5px;">Status: Standby</p>
                    
                    <label style="display:block; margin-top:15px; font-weight:bold; color:#444;">Your Transcribed Response:</label>
                    <textarea id="transcript-box" style="width: 100%; height: 80px; margin-top: 5px; padding: 10px; border-radius: 4px; border: 1px solid #ccc; font-family: inherit;" placeholder="Your spoken text will appear here instantly when you click Stop..."></textarea>
                    <p style="font-size: 12px; color: #666; margin-top: 5px;">⚠️ Copy the text above and verify it in the edit block below to ensure the AI reviewer logs your response correctly.</p>
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
                        recognition.interimResults = false;
                        recognition.lang = 'en-US';

                        let finalTranscript = '';

                        recognition.onstart = () => {{
                            statusText.innerHTML = "🔴 Status: Listening... Speak clearly into your mic!";
                            statusText.style.color = "#ff4b4b";
                            startBtn.disabled = true;
                            stopBtn.disabled = false;
                            finalTranscript = '';
                            transcriptBox.value = '';
                        }};

                        recognition.onerror = (event) => {{
                            statusText.innerHTML = "❌ Error: " + event.error;
                            statusText.style.color = "red";
                            startBtn.disabled = false;
                            stopBtn.disabled = true;
                        }};

                        recognition.onend = () => {{
                            statusText.innerHTML = "✅ Processing complete! Copy your text into the verification field below.";
                            statusText.style.color = "green";
                            startBtn.disabled = false;
                            stopBtn.disabled = true;
                        }};

                        recognition.onresult = (event) => {{
                            for (let i = event.resultIndex; i < event.results.length; ++i) {{
                                if (event.results[i].isFinal) {{
                                    finalTranscript += event.results[i][0].transcript + ' ';
                                }}
                            }}
                            transcriptBox.value = finalTranscript.trim();
                        }};

                        startBtn.onclick = () => {{ recognition.start(); }};
                        stopBtn.onclick = () => {{ recognition.stop(); }};

                    }} else {{
                        statusText.innerHTML = "❌ Web Speech API not supported.";
                        statusText.style.color = "red";
                    }}
                </script>
                """
                st.components.v1.html(js_mic_html, height=260)
                
                # --- BULLETPROOF TRANSCRIPTION VERIFICATION ---
                # This box allows you to type, edit, or copy-paste the text generated above.
                # Because it's a native Streamlit component, it is guaranteed to log to your AI engine.
                user_final_text = st.text_area(
                    "✏️ Verify / Edit your answer for the AI Reviewer:", 
                    key=f"live_text_confirmation_{current_idx}",
                    height=100,
                    placeholder="Copy the text from your recorder block above and paste it here to lock it into submission memory..."
                )
                
                st.write("")
                if st.button("Submit Answer & Next Question ➡️", key=f"next_btn_{current_idx}"):
                    # Log the text typed or pasted into the native field directly
                    if user_final_text.strip():
                        st.session_state.sim_answers[current_idx] = user_final_text.strip()
                    else:
                        st.session_state.sim_answers[current_idx] = "No response provided by candidate."
                    
                    st.session_state.current_q_idx += 1
                    st.rerun()
            else:
                st.balloons()
                st.success("🎉 Live Interview Simulation Complete!")
                
                compiled_results = []
                for i, question in enumerate(questions):
                    ans_text = st.session_state.sim_answers.get(i, "No response provided by candidate.")
                    compiled_results.append({"question": question, "answer": ans_text})
                
                with st.spinner("Compiling simulated data & generating feedback..."):
                    feedback = generate_feedback(compiled_results)
                
                st.divider()
                st.subheader("🧠 AI Live Evaluation Feedback")
                st.write(feedback)
                
                st.download_button(
                    label="📄 Download Feedback Report",
                    data=feedback,
                    file_name="simulated_interview_feedback.txt",
                    mime="text/plain"
                )
                
                if st.button("Reset Simulation Mode"):
                    st.session_state.sim_started = False
                    st.session_state.current_q_idx = 0
                    st.session_state.sim_answers = {}
                    st.rerun()

    with st.expander("View Extracted Resume Text"):
        st.text(resume_text)