import os
from sqlite3 import Cursor
import struct
import subprocess
import time
import webbrowser
import shlex
from urllib.parse import quote_plus
import eel
import pyaudio
import pyautogui
import pywhatkit as kit
import pvporcupine
from playsound import playsound
from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.db import get_sys_commands, get_web_commands, find_contact
from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

#playing assistant sound function

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

# Settings you already had (keep or adjust)
WHITELIST_ONLY = True
CONFIRM_BEFORE_OPEN = False
START_SOUND_PATH = os.path.join("www", "assets", "audio", "start_sound.mp3")

# Small website map for common voice commands
WEBSITE_MAP = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "email": "https://mail.google.com",
    "calendar": "https://calendar.google.com",
}

# Example manual mapping (keep as you had or extend)
MANUAL_APP_MAP = {
    # "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # add manual trusted paths here
}

# (Reuse or keep your auto discovery / APP_MAP code if you already built it)
# Assume APP_MAP contains user-installed apps (friendly name -> path)

APP_MAP = {
    # Basic Windows tools
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "wordpad": "wordpad.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    
    # Browsers (common install locations, fallback to command name)
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "microsoft edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",

    # Office-like
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",

}

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def hotword():
    while True:  # Outer loop to restart on error
        porcupine=None
        paud=None
        audio_stream=None
        try:
            # pre trained keywords
            porcupine=pvporcupine.create(keywords=["jarvis","alexa"])
            paud=pyaudio.PyAudio()
            audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)

            # loop for streaming
            while True:
                keyword=audio_stream.read(porcupine.frame_length)
                keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

                # processing keyword comes from mic
                keyword_index=porcupine.process(keyword)

                # checking first keyword detected for not
                if keyword_index>=0:
                    print("hotword detected")

                    # pressing shortcut key win+j
                    import pyautogui as autogui
                    autogui.keyDown("win")
                    autogui.press("j")
                    time.sleep(2)
                    autogui.keyUp("win")

        except Exception as e:
            print(f"Hotword detection error: {e}. Restarting...")
            time.sleep(1)  # Brief pause before restart
        finally:
            if porcupine is not None:
                porcupine.delete()
            if audio_stream is not None:
                audio_stream.close()
            if paud is not None:
                paud.terminate()
                
def _normalize(q: str) -> str:
    if not q:
        return ""
    return q.lower().strip()

def _confirm_with_voice(prompt_text: str) -> bool:
    """
    Use takecommand() to get a yes/no response if CONFIRM_BEFORE_OPEN is enabled.
    If CONFIRM_BEFORE_OPEN is False, return True (auto-confirm).
    """
    if not CONFIRM_BEFORE_OPEN:
        return True

    try:
        from engine.command import takecommand
    except Exception as e:
        print("Could not import takecommand for confirmation:", e)
        return False

    speak(prompt_text + ". Please say yes or no.")
    resp = takecommand()
    if not resp:
        speak("I didn't hear a confirmation.")
        return False
    resp = _normalize(resp)
    return resp.startswith("y") or "yes" in resp

def _open_with_path(path: str):
    """Start an executable or open a file/shortcut."""
    try:
        if os.path.exists(path):
            subprocess.Popen([path])
        else:
            # try to run by name (rely on PATH) or attempt to open .lnk
            subprocess.Popen([path])
        return True
    except Exception as e:
        print("Error launching:", path, e)
        return False

def searchGoogle(query: str):
    """
    Search on Google for the given query.
    """
    if not query:
        speak("What should I search for?")
        return

    q = _normalize(query)
    if ASSISTANT_NAME:
        q = q.replace(ASSISTANT_NAME.lower(), "")
    q = q.replace("search", "").replace("on google", "").strip()

    if not q:
        speak("What should I search for on Google?")
        return

    search_url = "https://www.google.com/search?q=" + quote_plus(q)
    speak(f"Searching for {q} on Google.")
    webbrowser.open(search_url)

def searchMedia(query: str):
    """
    Search for video or song on YouTube or Google based on the query.
    """
    if not query:
        speak("What should I search for?")
        return

    q = _normalize(query)
    if ASSISTANT_NAME:
        q = q.replace(ASSISTANT_NAME.lower(), "")
    q = q.replace("search", "").replace("play", "").replace("on youtube", "").replace("on google", "").strip()

    if not q:
        speak("What should I search for?")
        return

    if "on google" in query:
        search_url = "https://www.google.com/search?q=" + quote_plus(q)
        speak(f"Searching for {q} on Google.")
    else:
        search_url = "https://www.youtube.com/search?q=" + quote_plus(q)
        speak(f"Searching for {q} on YouTube.")

    webbrowser.open(search_url)

def openCommand(query: str):
    """
    Improved openCommand:
     - Opens websites (google, youtube, email, calendar)
     - Tries APP_MAP (manual or auto-discovered)
     - If not found, offers to search/download online
    Returns status string for UI: "opened", "not_found", "download_offered",
    "download_started", "cancelled", "error".
    """
    if not query:
        speak("No command received.")
        return "no_input"

    q = _normalize(query)
    if ASSISTANT_NAME:
        q = q.replace(ASSISTANT_NAME.lower(), "")
    q = q.replace("open", "").strip()

    if q == "":
        speak("What should I open?")
        return "no_target"

    # 1) Website quick map
    if q in WEBSITE_MAP:
        url = WEBSITE_MAP[q]
        if not _confirm_with_voice(f"Open {q} in your browser"):
            speak("Cancelled.")
            return "cancelled"
        speak(f"Opening {q}.")
        webbrowser.open(url)
        return "opened"

    # 2) Check database for web commands
    web_commands = get_web_commands()
    if q in web_commands:
        url = web_commands[q]
        if not _confirm_with_voice(f"Open {q} in your browser"):
            speak("Cancelled.")
            return "cancelled"
        speak(f"Opening {q}.")
        webbrowser.open(url)
        return "opened"

    # 3) Exact or fuzzy lookup in APP_MAP (manual or auto)
    # Try full match, then first token, then substring match
    found_path = None
    q_tokens = q.split()

    # exact match
    if q in APP_MAP:
        found_path = APP_MAP[q]
    else:
        # match first token
        if q_tokens[0] in APP_MAP:
            found_path = APP_MAP[q_tokens[0]]
        else:
            # substring / startswith
            for k, v in APP_MAP.items():
                if k.startswith(q) or q in k:
                    found_path = v
                    break

    if found_path:
        if not _confirm_with_voice(f"Open {q}"):
            speak("Cancelled.")
            return "cancelled"
        eel.DisplayMessage(f"Opening {q}.")
        speak(f"Opening {q}.")
        ok = _open_with_path(found_path)
        return "opened" if ok else "error"

    # 4) Check database for sys commands
    sys_commands = get_sys_commands()
    if q in sys_commands:
        found_path = sys_commands[q]
        if not _confirm_with_voice(f"Open {q}"):
            speak("Cancelled.")
            return "cancelled"
        eel.DisplayMessage(f"Opening {q}.")
        speak(f"Opening {q}.")
        ok = _open_with_path(found_path)
        return "opened" if ok else "error"
                    
    # 3) If whitelist-only is enabled, reject unknown
    if WHITELIST_ONLY:
        speak(f"I don't recognize {q} on this PC.")
        # Offer to search/download
        if _confirm_with_voice(f"Would you like me to search for {q} online to download it?"):
            # open a Google search for download <q>
            search_url = "https://www.google.com/search?q=" + quote_plus("download " + q)
            webbrowser.open(search_url)
            speak(f"I opened a search for downloading {q}.")
            return "download_started"
        else:
            speak("Okay, cancelled.")
            return "cancelled"

    # 4) If not whitelist-only, try to open as a file path or run as command
    potential_path = q.strip(' "\'')
    if ("\\" in potential_path) or ("/" in potential_path) or ("." in potential_path):
        if not _confirm_with_voice(f"Open file {potential_path}"):
            speak("Cancelled.")
            return "cancelled"
        try:
            speak("Opening file.")
            os.startfile(potential_path)
            return "opened"
        except Exception as e:
            print("Error opening file:", e)
            # proceed to trying to run as command

    # 5) Last resort: ask to search/download or try to run as command
    if _confirm_with_voice(f"I couldn't find {q}. Would you like me to search for it online?"):
        search_url = "https://www.google.com/search?q=" + quote_plus("download " + q)
        webbrowser.open(search_url)
        speak(f"I opened a search for downloading {q}.")
        return "download_started"

    # Optionally try to run as a command/program (only if user allowed)
    try:
        speak(f"Trying to run {q}.")
        parts = shlex.split(q)
        subprocess.Popen(parts)
        return "opened"
    except FileNotFoundError:
        speak(f"{q} does not appear to be installed on this system.")
        return "not_found"
    except Exception as e:
        print("Error running command:", e)
        speak("I failed to run that command.")
        return "error"

# find contact
def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    return find_contact(query)
    
    #
def whatsApp(mobile_no, message, flag, name):
    
    if flag == 'message':
        jarvis_message = "message send successfully to "+name
        try:
            # Use pywhatkit to send message instantly
            kit.sendwhatmsg_instantly(mobile_no, message, wait_time=10, tab_close=True)
            speak(jarvis_message)
        except Exception as e:
            speak("Failed to send message. Error: " + str(e))

    elif flag == 'call':
        jarvis_message = "calling to "+name
        try:
            # Open WhatsApp Desktop app with the phone number
            whatsapp_url = f"whatsapp://send?phone={mobile_no}"
            subprocess.run(['start', whatsapp_url], shell=True)
            time.sleep(15)
            # Navigate to call button
            pyautogui.hotkey('tab')  # Navigate to call button
            pyautogui.hotkey('enter')
            speak(jarvis_message)
        except Exception as e:
            speak("Failed to make call. Error: " + str(e))

    else:  # video call
        jarvis_message = "starting video call with "+name
        try:
            # Open WhatsApp Desktop app with the phone number
            whatsapp_url = f"whatsapp://send?phone={mobile_no}"
            subprocess.run(['start', whatsapp_url], shell=True)
            time.sleep(10)
            # Navigate to video call button
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')  # Navigate to video call button
            pyautogui.hotkey('enter')
            speak(jarvis_message)
        except Exception as e:
            speak("Failed to start video call. Error: " + str(e))
            
# chat bot
def chatBot(query):
    user_input = query.lower()
    try:
        chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response = chatbot.chat(user_input)
        print(response)
        speak(response)
        return response
    except Exception as e:
        print("ChatBot error:", e)
        speak("Sorry, I couldn't connect to the chatbot. Please check your cookies or internet connection.")
        return None
