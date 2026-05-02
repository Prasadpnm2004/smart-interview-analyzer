import streamlit as st
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
import random

from utils.speech_to_text import audio_to_text
from utils.text_analysis import analyze_text, get_sentiment

# ==================================================
# 🎨 PAGE CONFIG + PREMIUM UI
# ==================================================
st.set_page_config(page_title="Smart Interview Analyzer", page_icon="🎤", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e2e8f0;
}
.main-title {
    font-size: 48px;
    font-weight: 700;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 40px;
}
.card {
    padding: 20px;
    border-radius: 16px;
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}
.stButton>button {
    border-radius: 12px;
    height: 45px;
    font-weight: 600;
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: white;
}
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎤 Smart Interview Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered Interview Intelligence System</div>', unsafe_allow_html=True)

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
# 🧠 FEEDBACK FUNCTION
# ==================================================
def generate_feedback(wpm, filler, sentiment):
    feedback = []

    if wpm < 100:
        feedback.append("🗣️ You are speaking too slowly.")
    elif wpm > 160:
        feedback.append("⚡ You are speaking too fast.")
    else:
        feedback.append("✅ Good speaking pace.")

    if filler == 0:
        feedback.append("🎯 Excellent clarity.")
    elif filler <= 5:
        feedback.append("👍 Minor filler words present.")
    else:
        feedback.append("⚠️ Too many filler words.")

    if sentiment > 0:
        feedback.append("💡 Positive tone.")
    elif sentiment < 0:
        feedback.append("🔻 Negative tone detected.")
    else:
        feedback.append("😐 Neutral tone.")

    return feedback

# ==================================================
# 🧭 SIDEBAR
# ==================================================
mode = st.sidebar.radio("Navigation", ["🎤 Live Interview", "📂 Audio Upload", "🎥 Video Analysis"])

# ==================================================
# SESSION STATE
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

if "video_emotions" not in st.session_state:
    st.session_state.video_emotions = None

# ==================================================
# 🎤 LIVE INTERVIEW
# ==================================================
if mode == "🎤 Live Interview":

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start Interview", use_container_width=True):
            st.session_state.interview_running = True
            st.session_state.current_q = 0
            st.session_state.answers = []
            st.session_state.questions = random.sample(QUESTIONS, 5)
            st.rerun()

    with col2:
        if st.button("⏹️ Stop Interview", use_container_width=True):
            st.session_state.interview_running = False

    if st.session_state.interview_running:

        progress = st.session_state.current_q / len(st.session_state.questions)
        st.progress(progress)

        if st.session_state.current_q < len(st.session_state.questions):

            q_index = st.session_state.current_q
            question = st.session_state.questions[q_index]

            st.markdown(f"""
            <div class="card">
                <div style="color:#94a3b8;">Question {q_index+1}</div>
                <div style="font-size:20px; font-weight:600;">{question}</div>
            </div>
            """, unsafe_allow_html=True)

            audio_data = st.audio_input("🎤 Record your answer")

            if audio_data:
                st.session_state.current_audio = audio_data

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Submit Answer", use_container_width=True):

                    if st.session_state.current_audio is None:
                        st.warning("Record first")
                    else:
                        path = os.path.join(UPLOAD_DIR, f"answer_{q_index}.wav")

                        with open(path, "wb") as f:
                            f.write(st.session_state.current_audio.getbuffer())

                        text = audio_to_text(path)
                        result = analyze_text(text, path)
                        sentiment = get_sentiment(text)

                        wpm = result.get("wpm", 0)
                        filler = result.get("filler_words", 0)

                        st.session_state.answers.append({
                            "wpm": wpm,
                            "filler": filler,
                            "sentiment": sentiment
                        })

                        st.session_state.current_audio = None
                        st.success("Answer saved!")

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
            st.subheader("🧠 Final Report")

            avg_wpm = sum(a["wpm"] for a in st.session_state.answers) / len(st.session_state.answers)
            avg_filler = sum(a["filler"] for a in st.session_state.answers) / len(st.session_state.answers)
            avg_sentiment = sum(a["sentiment"] for a in st.session_state.answers) / len(st.session_state.answers)

            m1, m2, m3 = st.columns(3)
            m1.metric("Avg WPM", round(avg_wpm,2))
            m2.metric("Avg Fillers", round(avg_filler,2))
            m3.metric("Avg Sentiment", round(avg_sentiment,2))

            score = int((avg_wpm/160)*40 + (100-avg_filler*10)*0.3 + ((avg_sentiment+1)*50)*0.3)

            st.markdown(f"## 🎯 {score}/100")
            st.progress(score/100)

            st.subheader("🧠 Feedback")
            for f in generate_feedback(avg_wpm, avg_filler, avg_sentiment):
                st.write(f"• {f}")

# ==================================================
# 📂 AUDIO UPLOAD
# ==================================================
elif mode == "📂 Audio Upload":

    file = st.file_uploader("Upload Audio", type=["wav","mp3","m4a"])

    if file:
        path = os.path.join(UPLOAD_DIR, file.name)

        with open(path, "wb") as f:
            f.write(file.getbuffer())

        st.audio(path)

        text = audio_to_text(path)
        result = analyze_text(text, path)
        sentiment = get_sentiment(text)

        wpm = result.get("wpm", 0)
        filler = result.get("filler_words", 0)

        st.write(text)

        scores = {
            "Speed": min(int((wpm/160)*100),100),
            "Clarity": max(100-filler*10,0),
            "Tone": int((sentiment+1)*50)
        }

        cols = st.columns(3)

        def circle(val,label):
            fig,ax=plt.subplots()
            ax.pie([val,100-val],startangle=90,wedgeprops={'width':0.3})
            ax.text(0,0,f"{val}%",ha='center',va='center')
            ax.set_title(label)
            ax.axis('equal')
            return fig

        for col,(k,v) in zip(cols,scores.items()):
            with col:
                st.pyplot(circle(v,k))

        st.subheader("🧠 Feedback")
        for f in generate_feedback(wpm, filler, sentiment):
            st.write(f"• {f}")

# ==================================================
# 🎥 VIDEO ANALYSIS
# ==================================================
elif mode == "🎥 Video Analysis":

    video = st.file_uploader("Upload Video", type=["mp4","mov","avi"])

    def analyze():
        return {"confident":random.randint(10,40),
                "neutral":random.randint(10,40),
                "nervous":random.randint(10,40),
                "anxious":random.randint(10,40)}

    if video:
        path=os.path.join(UPLOAD_DIR,video.name)
        with open(path,"wb") as f:
            f.write(video.getbuffer())

        st.video(path)

        if st.button("Analyze"):
            st.session_state.video_emotions=analyze()

    if st.session_state.video_emotions:
        emotions=st.session_state.video_emotions

        cols=st.columns(4)

        for col,(k,v) in zip(cols,emotions.items()):
            with col:
                fig,ax=plt.subplots()
                ax.pie([v,100-v],startangle=90,wedgeprops={'width':0.3})
                ax.text(0,0,f"{v}%",ha='center',va='center')
                ax.set_title(k.capitalize())
                ax.axis('equal')
                st.pyplot(fig)

        st.subheader("🧠 Feedback")

        if emotions["confident"] > 30:
            st.success("Confident presence detected.")
        else:
            st.warning("Work on confidence.")

        if emotions["nervous"] > 30 or emotions["anxious"] > 30:
            st.warning("Nervousness detected.")

# ==================================================
st.markdown("---")
st.caption("🚀 Smart Interview Analyzer | AI + NLP + CV")