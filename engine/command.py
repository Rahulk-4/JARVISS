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
    if message == 1:
        query = takecommand()
        print(query)
    else:
        query = message

    try:
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
            time.sleep(2)
            eel.ShowHood()
        elif "on youtube" in query or "play" in query and ("song" in query or "video" in query):
            from engine.features import searchMedia
            searchMedia(query)
            eel.ShowHood()
        elif "search" in query and "on google" in query:
            from engine.features import searchGoogle
            searchGoogle(query)
            eel.ShowHood()
        elif "search" in query or "play" in query:
            from engine.features import searchMedia
            searchMedia(query)
            eel.ShowHood()
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query:
                        speak("what message to send")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()

                    elif "phone call" in query:
                        message = 'call'
                    else:
                        message = 'video call'

                    whatsApp(contact_no, query, message, name)
            eel.ShowHood()
        else:
            from engine.features import geminai
            geminai(query)
            eel.ShowHood()
    except:
        print("error")
        eel.ShowHood()
