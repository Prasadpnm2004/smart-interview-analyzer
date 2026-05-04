import streamlit as st
import os
import time
from analyzer_core import analyze_video
from ui_components import metric_card, create_donut_chart, feedback_box

def render_video_upload():
    st.header("🎥 Video Analysis Mode")
    st.markdown("Upload an interview video to analyze your non-verbal communication and emotions.")

    uploaded_file = st.file_uploader("Upload Video File", type=['mp4', 'mov', 'avi'])

    if uploaded_file is not None:
        st.video(uploaded_file)
        
        if st.button("Analyze Video", type="primary"):
            with st.spinner("Processing video frames..."):
                # Save uploaded file temporarily
                temp_file = "temp_uploaded_video.mp4"
                with open(temp_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Simulate a progress bar for UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                analysis = analyze_video(temp_file)
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)

                if not analysis:
                    st.error("Could not process the video. Please ensure it is a valid video file.")
                    return

                st.success("Video Analysis Complete!")
                
                emotions = analysis['emotions']
                dominant = analysis['dominant_emotion']
                
                st.markdown("### Emotional State Distribution")
                
                # We show 4 donut charts for the emotions
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.plotly_chart(create_donut_chart(emotions['Confident'], "Confident", "#10B981"), use_container_width=True)
                with c2:
                    st.plotly_chart(create_donut_chart(emotions['Neutral'], "Neutral", "#3B82F6"), use_container_width=True)
                with c3:
                    st.plotly_chart(create_donut_chart(emotions['Nervous'], "Nervous", "#F59E0B"), use_container_width=True)
                with c4:
                    st.plotly_chart(create_donut_chart(emotions['Anxious'], "Anxious", "#EF4444"), use_container_width=True)

                st.markdown("### Analysis Feedback")
                metric_card("Dominant Emotion", dominant, f"Detected across {analysis['frames_processed']} frames")

                if dominant == "Confident":
                    feedback_box("Excellent! You maintained a confident and strong presence throughout the video.", "positive")
                elif dominant == "Neutral":
                    feedback_box("You appeared calm and neutral. This is good, but try adding a bit more energy and smiling to show enthusiasm.", "info")
                elif dominant in ["Nervous", "Anxious"]:
                    feedback_box("You showed signs of nervousness. Try to maintain eye contact, sit up straight, and take deep breaths before answering.", "warning")
                
                st.info("Note: Emotion detection is currently using a heuristic simulation model to provide quick feedback.")
