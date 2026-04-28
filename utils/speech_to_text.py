import speech_recognition as sr

def audio_to_text(file_path):
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        return "Speech could not be understood"

    except sr.RequestError as e:
        return f"API request failed: {e}"

    except Exception as e:
        return f"Error: {str(e)}"