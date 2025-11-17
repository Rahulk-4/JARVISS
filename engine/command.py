
import time
import pyttsx3
import speech_recognition as sr
import eel
import traceback
import pvporcupine
import pyaudio
import struct
import os

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
def hotword():
    porcupine = None
    pa = None
    audio_stream = None
    try:
        # Initialize Porcupine with built-in keyword "jarvis"
        porcupine = pvporcupine.create(keywords=["jarvis"])

        pa = pyaudio.PyAudio()

        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)

            if keyword_index >= 0:
                print("Hotword detected")
                eel.DisplayMessage("Hotword detected")
                # Trigger the main command listening
                allCommands()
    except Exception as e:
        print("Error in hotword detection:", e)
        traceback.print_exc()
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()

@eel.expose
def allCommands(message=1):
    if message == 1:
        query = takecommand()
        print(query)
    else:
        query = message

    # Split query on " and " to handle multiple commands
    commands = query.split(" and ")
    for cmd in commands:
        cmd = cmd.strip()
        if not cmd:
            continue
        try:
            if "open" in cmd:
                from engine.features import openCommand
                openCommand(cmd)
                time.sleep(2)
            elif "on youtube" in cmd or "play" in cmd and ("song" in cmd or "video" in cmd):
                from engine.features import searchMedia
                searchMedia(cmd)
            elif "search" in cmd and "on google" in cmd:
                from engine.features import searchGoogle
                searchGoogle(cmd)

            elif "search" in cmd or "play" in cmd:
                from engine.features import searchMedia
                searchMedia(cmd)

            elif "send message" in cmd or "phone call" in cmd or "video call" in cmd or "whatsapp" in cmd:
                from engine.features import findContact, whatsApp
                msg_flag = ""
                contact_no, name = findContact(cmd)
                if(contact_no != 0):

                    if "send message" in cmd:
                        msg_flag = 'message'
                        speak("what message to send")
                        cmd = takecommand()

                    elif "phone call" in cmd:
                        msg_flag = 'call'
                    else:
                        msg_flag = 'video call'

                    whatsApp(contact_no, cmd, msg_flag, name)
            else:
                speak("I didn't understand that command.")
        except:
            print("error processing command:", cmd)
    eel.ShowHood()
