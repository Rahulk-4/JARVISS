import eel
import pyttsx3

eel.init("www")
engine = pyttsx3.init()

@eel.expose
def speak(text):
    eel.jarvisSpeaking()  # 🔥 Trigger “speaking” animation
    engine.say(text)
    engine.runAndWait()
    eel.jarvisIdle()  # 🌙 Return to idle glow

eel.start('index.html', size=(1000, 600))
