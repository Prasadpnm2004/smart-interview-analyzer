import streamlit as st
from audio_recorder_streamlit import audio_recorder
import time
import os
import random
from analyzer_core import transcribe_audio, analyze_text, calculate_scores
from ui_components import metric_card, create_donut_chart, feedback_box

QUESTIONS = [
    "Tell me about yourself.",
    "Why do you want to work here?",
    "Describe a time you faced a difficult challenge at work.",
    "What are your greatest strengths and weaknesses?",
    "Where do you see yourself in five years?",
    "Describe a time you showed leadership.",
    "How do you handle stress and pressure?"
]

def render_live_interview():
    st.header("🎤 Live Interview Mode")
    st.markdown("Practice your interview skills in real-time. We will analyze your speech, clarity, and tone.")

    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    
    if not st.session_state.interview_started:
        if st.button("Start Interview", type="primary"):
            st.session_state.interview_started = True
            st.session_state.questions = random.sample(QUESTIONS, 4)
            st.session_state.current_q_idx = 0
            st.session_state.results = []
            st.rerun()
    else:
        q_idx = st.session_state.current_q_idx
        
        if q_idx < len(st.session_state.questions):
            st.subheader(f"Question {q_idx + 1} of {len(st.session_state.questions)}")
            st.markdown(f"### {st.session_state.questions[q_idx]}")
            
            st.markdown("**Record your answer:**")
            audio_bytes = audio_recorder(text="Click to record", recording_color="#ef4444", neutral_color="#6366f1", icon_name="microphone", icon_size="2x")
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                
                if st.button("Submit Answer"):
                    with st.spinner("Analyzing your response..."):
                        # Save temp audio file
                        temp_file = f"temp_answer_{q_idx}.wav"
                        with open(temp_file, "wb") as f:
                            f.write(audio_bytes)
                        
                        # Process
                        # Approximate duration based on file size for wav (assuming 16kHz, 16bit, mono)
                        # More accurate duration can be done via soundfile, but this is a fallback.
                        import soundfile as sf
                        import io
                        data, samplerate = sf.read(io.BytesIO(audio_bytes))
                        duration = len(data) / samplerate
                        
                        text = transcribe_audio(temp_file)
                        analysis = analyze_text(text, duration)
                        
                        st.session_state.results.append({
                            "question": st.session_state.questions[q_idx],
                            "text": text,
                            "analysis": analysis,
                            "duration": duration
                        })
                        
                        # Clean up
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                        
                        st.session_state.current_q_idx += 1
                        st.rerun()
        else:
            render_final_report()

def render_final_report():
    st.header("📊 Final Interview Report")
    
    results = st.session_state.results
    if not results:
        st.warning("No data recorded.")
        if st.button("Restart Interview"):
            st.session_state.interview_started = False
            st.rerun()
        return

    # Aggregate
    total_wpm = 0
    total_fillers = 0
    total_polarity = 0
    total_duration = 0
    total_words = 0
    
    for r in results:
        a = r["analysis"]
        total_wpm += a["wpm"]
        total_fillers += a["filler_count"]
        total_polarity += a["sentiment_score"]
        total_duration += r["duration"]
        total_words += a["word_count"]
        
    num_q = len(results)
    avg_wpm = int(total_wpm / num_q)
    avg_polarity = total_polarity / num_q
    
    # Calculate overall scores
    agg_analysis = {
        "wpm": avg_wpm,
        "filler_count": total_fillers,
        "sentiment_score": avg_polarity,
        "word_count": total_words
    }
    scores = calculate_scores(agg_analysis)

    # Display Overall Score
    st.markdown("### Overall Performance")
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Overall Score", f"{scores['overall_score']}/100", "Weighted combination")
    with col2:
        metric_card("Avg WPM", f"{avg_wpm}", "Ideal: 130-160")
    with col3:
        metric_card("Total Filler Words", f"{total_fillers}", f"Across {total_words} words")

    st.markdown("### Detailed Metrics")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(create_donut_chart(scores['speed_score'], "Pacing (Speed)", "#3B82F6"), use_container_width=True)
    with c2:
        st.plotly_chart(create_donut_chart(scores['clarity_score'], "Clarity (Fillers)", "#10B981"), use_container_width=True)
    with c3:
        st.plotly_chart(create_donut_chart(scores['tone_score'], "Tone (Sentiment)", "#F59E0B"), use_container_width=True)

    # Feedback
    st.markdown("### AI Feedback")
    if scores['speed_score'] < 70:
        feedback_box("You are speaking either too fast or too slow. Aim for a conversational pace of 130-160 WPM.", "warning")
    else:
        feedback_box("Great speaking pace. Easy to follow and engaging.", "positive")
        
    if scores['clarity_score'] < 70:
        feedback_box("We detected several filler words ('um', 'like'). Try pausing instead of filling the silence.", "warning")
    else:
        feedback_box("Your speech is very clear with minimal filler words. Excellent clarity!", "positive")
        
    if scores['tone_score'] > 60:
        feedback_box("Your tone came across as positive and confident.", "positive")
    else:
        feedback_box("Your tone leaned towards neutral or nervous. Try to speak with a bit more enthusiasm and confidence.", "info")

    st.markdown("---")
    st.subheader("Question Breakdown")
    for idx, r in enumerate(results):
        with st.expander(f"Q{idx+1}: {r['question']}"):
            st.markdown(f"**Transcription:** {r['text'] if r['text'] else '(No speech detected)'}")
            a = r["analysis"]
            st.markdown(f"**WPM:** {a['wpm']} | **Fillers:** {a['filler_count']} | **Sentiment:** {a['sentiment']}")

    if st.button("Start New Interview"):
        st.session_state.interview_started = False
        st.rerun()
