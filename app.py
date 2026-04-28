import streamlit as st
import os

from utils.speech_to_text import audio_to_text
from utils.text_analysis import analyze_text, get_sentiment

st.set_page_config(page_title="Smart Interview Analyzer", page_icon="🎤", layout="centered")

st.title("🎤 Smart Interview Analyzer")
st.write("Upload an audio file and get feedback on your speaking performance.")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "m4a"])

if uploaded_file:

    try:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully!")

        st.audio(file_path)

        # 🎤 Speech to text
        with st.spinner("Transcribing audio..."):
            text = audio_to_text(file_path)

        if not text:
            st.error("Could not transcribe audio.")
            st.stop()

        st.subheader("📝 Transcribed Text")

        highlighted_text = text
        filler_words = ["um", "uh", "like", "you know", "basically"]

        for fw in filler_words:
            highlighted_text = highlighted_text.replace(fw, f"**{fw}**")

        st.markdown(highlighted_text)

        # 📊 Analysis
        with st.spinner("Analyzing performance..."):
            result = analyze_text(text, file_path)

        st.subheader("📊 Analysis Report")
        st.write(f"Total Words: {result.get('total_words', 0)}")
        st.write(f"Filler Words: {result.get('filler_words', 0)}")
        st.write(f"Speaking Speed (WPM): {result.get('wpm', 0)}")

        # 🧠 Sentiment
        sentiment = get_sentiment(text)

        st.subheader("🧠 Sentiment Analysis")
        st.write(f"Sentiment Score: {round(sentiment, 2)}")

        if sentiment > 0:
            st.success("Positive tone detected")
        elif sentiment < 0:
            st.warning("Negative tone detected")
        else:
            st.info("Neutral tone")

        # 💡 Feedback
        st.subheader("💡 Feedback")

        if result.get("filler_words", 0) > 5:
            st.warning("Too many filler words. Try to reduce them.")
        else:
            st.success("Good speaking clarity!")

        wpm = result.get("wpm", 0)

        if wpm < 100:
            st.warning("You are speaking too slow.")
        elif wpm > 160:
            st.warning("You are speaking too fast.")
        else:
            st.success("Good speaking speed!")

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")