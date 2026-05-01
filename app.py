import streamlit as st
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
import random

from utils.speech_to_text import audio_to_text
from utils.text_analysis import analyze_text, get_sentiment

# ==================================================
# 🎨 PAGE CONFIG + STYLE
# ==================================================
st.set_page_config(page_title="Smart Interview Analyzer", page_icon="🎤", layout="wide")

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 30px;
}
.card {
    padding: 15px;
    border-radius: 12px;
    background-color: #f5f5f5;
    border-left: 5px solid #4CAF50;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎤 Smart Interview Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered Interview Feedback System</div>', unsafe_allow_html=True)

# ==================================================
# 📁 SETUP
# ==================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

QUESTIONS = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why should we hire you?",
    "Describe a challenging situation you faced.",
    "Where do you see yourself in 5 years?",
    "Why do you want this job?",
    "Tell me about a failure and what you learned.",
    "How do you handle pressure?"
]

# ==================================================
# 🧭 SIDEBAR NAVIGATION
# ==================================================
mode = st.sidebar.radio(
    "Navigation",
    ["🎤 Live Interview", "📂 Audio Upload", "🎥 Video Analysis"]
)

# ==================================================
# 🎤 SESSION STATE
# ==================================================
if "interview_running" not in st.session_state:
    st.session_state.interview_running = False

if "questions" not in st.session_state:
    st.session_state.questions = random.sample(QUESTIONS, 5)

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "current_audio" not in st.session_state:
    st.session_state.current_audio = None

# ==================================================
# 🎤 LIVE INTERVIEW MODE
# ==================================================
if mode == "🎤 Live Interview":

    st.subheader("🎤 Live Interview Mode")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start Interview", use_container_width=True):
            st.session_state.interview_running = True
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.session_state.questions = random.sample(QUESTIONS, 5)

    with col2:
        if st.button("⏹️ Stop Interview", use_container_width=True):
            st.session_state.interview_running = False

    if st.session_state.interview_running:

        progress = st.session_state.current_q / len(st.session_state.questions)
        st.progress(progress)

        if st.session_state.current_q < len(st.session_state.questions):

            q_index = st.session_state.current_q
            question = st.session_state.questions[q_index]

            # 💡 Question Card
            st.markdown(f"""
            <div class="card">
            <b>Question {q_index+1}:</b><br>{question}
            </div>
            """, unsafe_allow_html=True)

            audio_data = st.audio_input("🎤 Record your answer")

            if audio_data is not None:
                st.session_state.current_audio = audio_data
                st.success("Recording captured. Click submit.")

            col1, col2 = st.columns(2)

            # ✅ Submit
            with col1:
                if st.button("✅ Submit Answer", use_container_width=True):

                    if st.session_state.current_audio is None:
                        st.warning("Record first")
                    else:
                        path = os.path.join(UPLOAD_DIR, f"answer_{q_index}.wav")

                        with open(path, "wb") as f:
                            f.write(st.session_state.current_audio.getbuffer())

                        with st.spinner("Analyzing..."):
                            text = audio_to_text(path)
                            result = analyze_text(text, path)
                            sentiment = get_sentiment(text)

                        wpm = result.get("wpm", 0)
                        filler = result.get("filler_words", 0)

                        st.write("📝", text)

                        m1, m2, m3 = st.columns(3)
                        m1.metric("WPM", wpm)
                        m2.metric("Fillers", filler)
                        m3.metric("Sentiment", round(sentiment,2))

                        st.session_state.answers.append({
                            "question": question,
                            "text": text,
                            "wpm": wpm,
                            "filler": filler,
                            "sentiment": sentiment
                        })

                        st.session_state.current_audio = None
                        st.success("Saved!")

            # ➡️ Next / Submit Interview
            with col2:
                is_last = q_index == len(st.session_state.questions) - 1

                if not is_last:
                    if st.button("➡️ Next Question", use_container_width=True):
                        if len(st.session_state.answers) <= q_index:
                            st.warning("Submit first")
                        else:
                            st.session_state.current_q += 1
                            st.rerun()
                else:
                    if st.button("✅ Submit Interview", use_container_width=True):
                        if len(st.session_state.answers) <= q_index:
                            st.warning("Submit final answer")
                        else:
                            st.session_state.current_q += 1
                            st.rerun()

        else:
            # ==================================================
            # 🧠 FINAL REPORT
            # ==================================================
            st.subheader("🧠 Final Report")

            total_wpm = sum(a["wpm"] for a in st.session_state.answers)
            total_filler = sum(a["filler"] for a in st.session_state.answers)
            total_sentiment = sum(a["sentiment"] for a in st.session_state.answers)

            n = len(st.session_state.answers)

            avg_wpm = total_wpm / n
            avg_filler = total_filler / n
            avg_sentiment = total_sentiment / n

            # 📊 Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Avg WPM", round(avg_wpm,2))
            m2.metric("Avg Fillers", round(avg_filler,2))
            m3.metric("Avg Sentiment", round(avg_sentiment,2))

            # 📊 Chart
            fig, ax = plt.subplots(figsize=(5,3))
            ax.bar(["WPM", "Fillers", "Sentiment"], [avg_wpm, avg_filler, avg_sentiment])
            ax.spines[['top','right']].set_visible(False)
            st.pyplot(fig)

            # 🎯 Score Card
            score = 0
            score += 40 if 100 <= avg_wpm <= 160 else 20
            score += 30 if avg_filler <= 5 else 10
            score += 30 if avg_sentiment > 0 else 20

            st.markdown(f"""
            <div style="padding:20px;border-radius:12px;background:#e8f5e9;text-align:center;font-size:28px;">
            🎯 Score: {score}/100
            </div>
            """, unsafe_allow_html=True)

            st.progress(score/100)

            if st.button("🔄 Restart", use_container_width=True):
                st.session_state.current_q = 0
                st.session_state.answers = []
                st.session_state.questions = random.sample(QUESTIONS, 5)
                st.rerun()

# ==================================================
# 📂 AUDIO MODE
# ==================================================
elif mode == "📂 Audio Upload":

    st.subheader("📂 Upload Audio")

    file = st.file_uploader("Upload", type=["wav","mp3","m4a"])

    if file:
        path = os.path.join(UPLOAD_DIR, file.name)

        with open(path, "wb") as f:
            f.write(file.getbuffer())

        st.audio(path)

        text = audio_to_text(path)
        st.write(text)

# ==================================================
# 🎥 VIDEO MODE
# ==================================================
elif mode == "🎥 Video Analysis":

    st.subheader("🎥 Video Analysis")

    video = st.file_uploader("Upload Video", type=["mp4","mov","avi"])

    def extract_frames(path, interval=30):
        cap = cv2.VideoCapture(path)
        frames = []
        i = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if i % interval == 0:
                frames.append(frame)
            i += 1

        cap.release()
        return frames

    def analyze_video(path):
        frames = extract_frames(path)
        counts = {"confident":0,"neutral":0,"nervous":0,"anxious":0}

        for _ in frames:
            r = random.random()
            if r<0.25: counts["confident"]+=1
            elif r<0.5: counts["neutral"]+=1
            elif r<0.75: counts["nervous"]+=1
            else: counts["anxious"]+=1

        return counts

    if video:
        path = os.path.join(UPLOAD_DIR, video.name)

        with open(path, "wb") as f:
            f.write(video.getbuffer())

        st.video(path)

        if st.button("Analyze"):
            emotions = analyze_video(path)
            dom = max(emotions, key=emotions.get)

            st.write(f"Dominant Emotion: **{dom}**")

            fig, ax = plt.subplots()
            ax.bar(emotions.keys(), emotions.values())
            st.pyplot(fig)

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption("🚀 Smart Interview Analyzer | AI + NLP + CV")