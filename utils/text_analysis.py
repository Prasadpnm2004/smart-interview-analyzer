from pydub import AudioSegment
from pydub.utils import which
import nltk
from textblob import TextBlob

# 🔹 Ensure ffmpeg is used
AudioSegment.converter = which("ffmpeg")

nltk.download('punkt')

FILLER_WORDS = ["um", "uh", "like", "you know", "basically"]

def analyze_text(text, file_path):
    
    words = nltk.word_tokenize(text.lower())
    total_words = len(words)

    filler_count = sum(words.count(fw) for fw in FILLER_WORDS)

    audio = AudioSegment.from_file(file_path)
    duration_minutes = len(audio) / 1000 / 60

    if duration_minutes > 0:
        wpm = total_words / duration_minutes
    else:
        wpm = 0

    return {
        "total_words": total_words,
        "filler_words": filler_count,
        "wpm": round(wpm, 2)
    }

# 🔹 Sentiment Analysis
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity