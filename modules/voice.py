import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")

speaker.Volume = 100
speaker.Rate = 0


def speak(text):
    try:
        text = str(text)

        # Remove unsupported characters
        text = text.encode("ascii", "ignore").decode("ascii")

        if text.strip():
            speaker.Speak(text)

    except Exception as e:
        print("Voice Error:", e)