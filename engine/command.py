import pyttsx3
import speech_recognition as sr
import eel
import time
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    #eel.receiverText(text)
    engine.runAndWait()
    
@eel.expose
def takecommand():
    print("[DEBUG] takecommand() called")   # ✅ add this

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        speak("Listening, please say something.")
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")  # ✅ add this
        eel.DisplayMessage(query)
        time.sleep(2)
        eel.ShowHood()
    except Exception as e:
        print(f"[ERROR] {e}")  # ✅ show any recognition errors
        return ""
    
    return query.lower()
eel.expose
def allCommands():
    print("[DEBUG] allCommands() triggered")  # ✅ add this
    query = takecommand()
    print(f"[DEBUG] Query from takecommand(): {query}")

    if "open" in query:
        from engine.features import openCommand
        openCommand(query)
    else:
        print("[DEBUG] Not run")