from utils.speech_to_text import audio_to_text
from utils.text_analysis import analyze_text

file_path = "sample.wav"

text = audio_to_text(file_path)

result = analyze_text(text, file_path)

print("Text:", text)
print("Analysis:", result)