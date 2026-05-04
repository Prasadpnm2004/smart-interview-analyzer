# 🎤 Smart Interview Analyzer

An AI-powered system that analyzes interview performance using **Speech Processing, NLP, and Computer Vision** to provide actionable feedback on communication skills.

---

## 🚀 Features

### 🎤 Live Interview Mode
- Real-time interview simulation with 5 random questions  
- Audio recording for each answer  
- Question-wise analysis (WPM, fillers, sentiment)  
- Final performance report with score and feedback  

### 📂 Audio Analysis
- Upload audio files (`.wav`, `.mp3`, `.m4a`)  
- Speech-to-text transcription  
- Performance breakdown:
  - Speaking speed (WPM)
  - Filler words detection
  - Sentiment analysis  
- Circular progress UI + feedback  
- 📄 Downloadable PDF report  

### 🎥 Video Analysis
- Upload interview videos (`.mp4`, `.mov`, `.avi`)  
- Frame-based facial analysis (prototype)  
- Emotion distribution:
  - Confidence
  - Neutral
  - Nervous
  - Anxious  
- Visual circular charts + feedback  

---

## 🧠 Tech Stack

- **Frontend/UI:** Streamlit  
- **Backend:** Python  
- **Speech Processing:** Custom Speech-to-Text module  
- **NLP:** NLTK (text analysis & sentiment)  
- **Computer Vision:** OpenCV  
- **Visualization:** Matplotlib  
- **Reporting:** ReportLab (PDF generation)  

---

## 📊 How It Works

1. 🎤 Capture or upload audio/video  
2. 🧠 Convert speech → text  
3. 📈 Analyze:
   - Words per minute (WPM)
   - Filler words
   - Sentiment  
4. 🎯 Generate:
   - Scores
   - Visual insights
   - Feedback  
5. 📄 Export results as PDF  

---

## 🖥️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/smart-interview-analyzer.git
cd smart-interview-analyzer