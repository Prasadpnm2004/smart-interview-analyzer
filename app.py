import streamlit as st
from ui_components import apply_custom_css
from views.live_interview import render_live_interview
from views.audio_upload import render_audio_upload
from views.video_upload import render_video_upload

# Configure the Streamlit page
st.set_page_config(
    page_title="Smart Interview Analyzer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling (Premium UI)
apply_custom_css()

def main():
    st.sidebar.title("🎙️ Smart Interview Analyzer")
    st.sidebar.markdown("AI-powered interview practice and feedback.")
    
    st.sidebar.markdown("---")
    
    mode = st.sidebar.radio(
        "Select Mode",
        ["Live Interview", "Audio Analysis", "Video Analysis"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Tips for Success:**\n\n"
        "- Speak clearly and at a moderate pace.\n"
        "- Try to minimize filler words (um, like).\n"
        "- Maintain a confident tone.\n"
        "- Ensure good lighting for video analysis."
    )

    if mode == "Live Interview":
        render_live_interview()
    elif mode == "Audio Analysis":
        render_audio_upload()
    elif mode == "Video Analysis":
        render_video_upload()

if __name__ == "__main__":
    main()
