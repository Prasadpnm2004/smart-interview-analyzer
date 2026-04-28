from utils.speech_to_text import audio_to_text

file_path = "sample.wav"   # make sure this file exists

text = audio_to_text(file_path)

print("Transcribed Text:")
print(text)