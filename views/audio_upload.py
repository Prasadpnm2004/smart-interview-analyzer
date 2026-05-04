import streamlit as st
import os
import time
from analyzer_core import transcribe_audio, analyze_text, calculate_scores
from ui_components import metric_card, create_donut_chart, feedback_box
import soundfile as sf
import io

def render_audio_upload():
    st.header("📂 Audio Upload Mode")
    st.markdown("Upload a recorded interview response to analyze your performance.")

    uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'm4a'])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        
        if st.button("Analyze Audio", type="primary"):
            with st.spinner("Analyzing audio... This may take a moment."):
                # Save uploaded file temporarily
                temp_file = "temp_uploaded_audio.wav"
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Try to get duration
                    data, samplerate = sf.read(temp_file)
                    duration = len(data) / samplerate
                except Exception as e:
                    # Fallback duration if sf.read fails (e.g. for non-wav)
                    duration = len(uploaded_file.getbuffer()) / (16000 * 2) # Rough estimate assuming 16kHz 16bit mono
                
                text = transcribe_audio(temp_file)
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)

                if not text:
                    st.error("Could not transcribe the audio. Please ensure it contains clear speech and is in a supported format.")
                    return
                
                analysis = analyze_text(text, duration)
                scores = calculate_scores(analysis)

                st.success("Analysis Complete!")
                
                # Layout
                st.markdown("### Transcription")
                st.info(text)

                st.markdown("### Performance Overview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    metric_card("Overall Score", f"{scores['overall_score']}/100")
                with col2:
                    metric_card("WPM", f"{analysis['wpm']}", "Ideal: 130-160")
                with col3:
                    metric_card("Filler Words", f"{analysis['filler_count']}", f"Across {analysis['word_count']} words")

                st.markdown("### Detailed Metrics")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.plotly_chart(create_donut_chart(scores['speed_score'], "Pacing (Speed)", "#3B82F6"), use_container_width=True)
                with c2:
                    st.plotly_chart(create_donut_chart(scores['clarity_score'], "Clarity (Fillers)", "#10B981"), use_container_width=True)
                with c3:
                    st.plotly_chart(create_donut_chart(scores['tone_score'], "Tone (Sentiment)", "#F59E0B"), use_container_width=True)

                st.markdown("### AI Feedback")
                if scores['speed_score'] < 70:
                    feedback_box("You are speaking either too fast or too slow. Aim for a conversational pace of 130-160 WPM.", "warning")
                else:
                    feedback_box("Great speaking pace. Easy to follow and engaging.", "positive")
                    
                if scores['clarity_score'] < 70:
                    feedback_box("We detected several filler words. Try pausing instead of filling the silence.", "warning")
                else:
                    feedback_box("Your speech is very clear with minimal filler words. Excellent clarity!", "positive")
                    
                if scores['tone_score'] > 60:
                    feedback_box("Your tone came across as positive and confident.", "positive")
                else:
                    feedback_box("Your tone leaned towards neutral or nervous. Try to speak with a bit more enthusiasm and confidence.", "info")
