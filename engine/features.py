import os
from playsound import playsound
import eel
from engine.command import speak
from engine.config import ASSISTANT_NAME

#playing assistant sound function

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)
    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.strip().lower()

    if query != "":
        speak("Opening " + query)

        # ✅ Fix: handle Windows built-in apps properly
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "command prompt": "cmd.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "explorer": "explorer.exe"
        }

        if query in apps:
            os.system(apps[query])
        else:
            os.system(f'start {query}')
    else:
        speak("not found")