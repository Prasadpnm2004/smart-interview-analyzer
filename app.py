import streamlit as st
import matplotlib.pyplot as plt
import os

from utils.speech_to_text import audio_to_text
from utils.text_analysis import analyze_text, get_sentiment

st.set_page_config(page_title="Smart Interview Analyzer", page_icon="🎤", layout="centered")

st.title("🎤 Smart Interview Analyzer")
st.write("Upload an audio file and get feedback on your speaking performance.")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:

    try:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully!")

        # 🔊 Audio Player
        st.audio(file_path)

        # 🎤 Speech to Text
        with st.spinner("Transcribing audio..."):
            text = audio_to_text(file_path)

        if not text:
            st.error("Could not transcribe audio.")
            st.stop()

        st.subheader("📝 Transcribed Text")

        # 🔹 Highlight filler words
        highlighted_text = text
        filler_words = ["um", "uh", "like", "you know", "basically"]

        for fw in filler_words:
            highlighted_text = highlighted_text.replace(fw, f"**{fw}**")

        st.markdown(highlighted_text)

        # 📊 Analysis
        with st.spinner("Analyzing performance..."):
            result = analyze_text(text, file_path)

        total_words = result.get("total_words", 0)
        filler_count = result.get("filler_words", 0)
        wpm = result.get("wpm", 0)

        st.subheader("📊 Analysis Report")
        st.write(f"Total Words: {total_words}")
        st.write(f"Filler Words: {filler_count}")
        st.write(f"Speaking Speed (WPM): {wpm}")

        # 📊 Performance Charts (UPGRADED)
        st.subheader("📊 Performance Charts")

        # 🔹 Chart 1: WPM
        st.write("### Speaking Speed (WPM)")
        fig1, ax1 = plt.subplots()
        ax1.bar(['WPM'], [wpm])
        st.pyplot(fig1)

        # 🔹 Chart 2: Filler Words
        st.write("### Filler Word Usage")
        fig2, ax2 = plt.subplots()
        ax2.bar(['Filler Words'], [filler_count])
        st.pyplot(fig2)

        # 🔹 Insight
        if filler_count == 0:
            st.success("Great! No filler words detected.")
        elif filler_count <= 5:
            st.info("Minor filler usage.")
        else:
            st.warning("High filler word usage.")

        # 🧠 Sentiment Analysis
        sentiment = get_sentiment(text)

        st.subheader("🧠 Sentiment Analysis")
        st.write(f"Sentiment Score: {round(sentiment, 2)}")

        if sentiment > 0:
            st.success("Positive tone detected")
        elif sentiment < 0:
            st.warning("Negative tone detected")
        else:
            st.info("Neutral tone")
        # 🎯 Scoring System
        st.subheader("🎯 Overall Performance Score")
        score = 0
        # 🔹 WPM Score (40)
        if 100 <= wpm <= 160:
            score += 40
        else:
            score += 20
        # 🔹 Filler Words Score (30)
        if filler_count == 0:
            score += 30
        elif filler_count <= 5:
            score += 20
        else:
            score += 10
        # 🔹 Sentiment Score (30)
        if sentiment > 0:
            score += 30
        elif sentiment == 0:
            score += 20
        else:
            score += 10

        st.markdown(f"## 🎯 Score: {score}/100")
        st.progress(score / 100)
        if score >= 80:
          st.success("🔥 Excellent performance!")
        elif score >= 60:
          st.info("👍 Good, but can improve.")
        else:
          st.warning("⚠️ Needs improvement.")
       # 🧠 Smart Feedback System
        st.subheader("🧠 Detailed Feedback")

        feedback = []

        # 🔹 WPM Feedback
        if wpm < 100:
            feedback.append("You are speaking too slowly. Try to increase your pace.")
        elif wpm > 160:
            feedback.append("You are speaking too fast. Slow down for better clarity.")
        else:
            feedback.append("Your speaking speed is well-balanced.")

        # 🔹 Filler Words Feedback
        if filler_count == 0:
            feedback.append("Excellent clarity! No filler words detected.")
        elif filler_count <= 5:
            feedback.append("Minor filler word usage. Can be improved.")
        else:
            feedback.append("High filler word usage. Practice reducing unnecessary words.")

        # 🔹 Sentiment Feedback
        if sentiment > 0:
            feedback.append("Your tone sounds positive and confident.")
        elif sentiment < 0:
            feedback.append("Your tone seems negative. Try to sound more confident.")
        else:
            feedback.append("Your tone is neutral. Add more energy to your speech.")

        # 🔹 Final Combined Insight
        if score >= 80:
            feedback.append("Overall, you performed very well. Keep it up!")
        elif score >= 60:
            feedback.append("Good performance, but there is room for improvement.")
        else:
            feedback.append("You need more practice to improve your communication skills.")

        # 🔹 Display Feedback
        for point in feedback:
            st.write(f"• {point}")
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")