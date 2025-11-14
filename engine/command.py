import time
import pyttsx3
import speech_recognition as sr
import eel
import traceback

# Expose speak() so JS can call it if needed
@eel.expose
def speak(text):
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        index = 1 if len(voices) > 1 else 0
        engine.setProperty('voice', voices[index].id)
        engine.setProperty('rate', 174)
        eel.DisplayMessage(text)
        engine.say(str(text))
        engine.runAndWait()
        return True
    except Exception as e:
        print("Error in speak():", e)
        traceback.print_exc()
        return False

@eel.expose
def takecommand():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Listening...")
            try:
                eel.DisplayMessage("Listening...")
            except:
                pass

            r.adjust_for_ambient_noise(source, duration=0.8)
            audio = r.listen(source, timeout=10, phrase_time_limit=8)

        try:
            print("Recognizing...")
            try:
                eel.DisplayMessage("Recognizing...")
            except:
                pass

            query = r.recognize_google(audio, language="en-in")
            print("User said:", query)

            try:
                eel.DisplayMessage(query)
            except:
                pass

            return query.lower()

        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print("Speech recognition error:", e)
            return ""

    except Exception as e:
        print("Error in takecommand:", e)
        traceback.print_exc()
        return ""

@eel.expose
def allCommands(message=1):
    query = takecommand()
    print(query)

    if "open" in query:
        from engine.features import openCommand
        openCommand(query)
        time.sleep(2)
        eel.ShowHood()
    else:
        print("not run")
        eel.ShowHood()
