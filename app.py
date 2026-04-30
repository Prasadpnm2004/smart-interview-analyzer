import streamlit as st
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np

from utils.speech_to_text import audio_to_text
from utils.text_analysis import analyze_text, get_sentiment

st.set_page_config(page_title="Smart Interview Analyzer", page_icon="🎤", layout="centered")

st.title("🎤 Smart Interview Analyzer")

# ✅ Upload folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Interview state
if "interview_running" not in st.session_state:
    st.session_state.interview_running = False

st.subheader("🎤 Live Interview Mode")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start Interview"):
        st.session_state.interview_running = True

with col2:
    if st.button("⏹️ Stop Interview"):
        st.session_state.interview_running = False

# ✅ Status
if st.session_state.interview_running:
    st.success("Interview is running... Speak now 🎤")
else:
    st.info("Click 'Start Interview' to begin")

# ==================================================
# 🎤 INTERVIEW MODE
# ==================================================
if st.session_state.interview_running:

    # 🎤 Audio Recording
    st.subheader("🎤 Record Your Answer")
    audio_data = st.audio_input("Speak now...")

    if audio_data is not None:

        interview_audio_path = os.path.join(UPLOAD_DIR, "interview_recording.wav")

        with open(interview_audio_path, "wb") as f:
            f.write(audio_data.getbuffer())

        st.success("Recording captured!")

        # 🎤 Speech to Text
        with st.spinner("Transcribing audio..."):
            text = audio_to_text(interview_audio_path)

        st.subheader("📝 Transcribed Text")
        st.write(text)

        # 📊 Analysis
        result = analyze_text(text, interview_audio_path)

        total_words = result.get("total_words", 0)
        filler_count = result.get("filler_words", 0)
        wpm = result.get("wpm", 0)

        sentiment = get_sentiment(text)

        # 📊 Metrics
        st.subheader("📊 Performance Overview")

        m1, m2, m3 = st.columns(3)
        m1.metric("WPM", wpm)
        m2.metric("Filler Words", filler_count)
        m3.metric("Sentiment", round(sentiment, 2))

        # 📊 Charts
        col1, col2 = st.columns(2)

        with col1:
            st.write("### WPM")
            fig1, ax1 = plt.subplots()
            ax1.bar(['WPM'], [wpm])
            ax1.set_ylim(0, 200)
            st.pyplot(fig1)

        with col2:
            st.write("### Fillers")
            fig2, ax2 = plt.subplots()
            ax2.bar(['Fillers'], [filler_count])
            ax2.set_ylim(0, 20)
            st.pyplot(fig2)

        # 🧠 Sentiment
        st.subheader("🧠 Sentiment Analysis")

        if sentiment > 0:
            st.success("Positive tone detected")
        elif sentiment < 0:
            st.warning("Negative tone detected")
        else:
            st.info("Neutral tone")

        # 🎯 Score
        st.subheader("🎯 Overall Performance Score")

        score = 0

        if 100 <= wpm <= 160:
            score += 40
        else:
            score += 20

        if filler_count == 0:
            score += 30
        elif filler_count <= 5:
            score += 20
        else:
            score += 10

        if sentiment > 0:
            score += 30
        elif sentiment == 0:
            score += 20
        else:
            score += 10

        st.markdown(f"## 🎯 Score: {score}/100")
        st.progress(score / 100)

        # 🧠 Feedback
        st.subheader("🧠 Detailed Feedback")

        feedback = []

        if wpm < 100:
            feedback.append("You are speaking too slowly.")
        elif wpm > 160:
            feedback.append("You are speaking too fast.")
        else:
            feedback.append("Your speaking speed is good.")

        if filler_count == 0:
            feedback.append("Excellent clarity. No filler words.")
        elif filler_count <= 5:
            feedback.append("Some filler words present.")
        else:
            feedback.append("Too many filler words.")

        if sentiment > 0:
            feedback.append("Positive and confident tone.")
        elif sentiment < 0:
            feedback.append("Tone seems negative. Try to sound confident.")
        else:
            feedback.append("Neutral tone. Add more energy.")

        for f in feedback:
            st.write(f"• {f}")

    # ==================================================
    # 📸 IMAGE + CV
    # ==================================================
    st.subheader("📸 Capture Facial Expression")

    image = st.camera_input("Take a picture during interview")

    if image is not None:

        image_path = os.path.join(UPLOAD_DIR, "face.jpg")

        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

        st.image(image, caption="Captured Frame", width="stretch")

        file_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        st.subheader("🟢 Face Detection Result")
        st.image(img, caption="Detected Face", width="stretch")
        st.write(f"Faces Detected: {len(faces)}")

        # 😊 Emotion Estimation
        st.subheader("😊 Emotion Estimation")

        if len(faces) == 0:
            st.warning("No face detected clearly.")
            emotion = "unknown"
        else:
            if filler_count > 5:
                emotion = "nervous"
            elif wpm > 160:
                emotion = "anxious"
            elif sentiment > 0:
                emotion = "confident"
            else:
                emotion = "neutral"

            st.write(f"Estimated Emotion: **{emotion.capitalize()}**")

        # ==================================================
        # 🧠 FINAL AI INSIGHT
        # ==================================================
        st.subheader("🧠 Final AI Insight")

        insight = ""

        if (100 <= wpm <= 160) and filler_count <= 5 and sentiment > 0:
            if emotion == "confident":
                insight = "Excellent performance. You spoke clearly, maintained a good pace, and appeared confident. This is interview-ready."
            else:
                insight = "Strong communication skills. Improve facial expressions for better engagement."

        elif (100 <= wpm <= 160) and filler_count <= 5:
            insight = "Good speaking pace and clarity, but confidence and expression can be improved."

        elif filler_count > 5:
            insight = "Too many filler words affecting clarity. Try pausing instead."

        elif wpm > 160:
            insight = "Speaking too fast. Slow down for better clarity."

        elif wpm < 100:
            insight = "Speaking too slowly. Try a more natural pace."

        else:
            insight = "Overall performance is moderate. Work on clarity, confidence, and engagement."

        st.success(insight)

# ==================================================
# 📂 FILE UPLOAD MODE
# ==================================================
st.write("---")
st.subheader("📂 Upload Audio File Instead")

uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:

    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully!")
    st.audio(file_path)

    text = audio_to_text(file_path)

    st.subheader("📝 Transcribed Text")
    st.write(text)

    result = analyze_text(text, file_path)
    st.write(result)