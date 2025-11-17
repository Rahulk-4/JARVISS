import eel
import sys
import threading


from engine.features import *
from engine.command import *

eel.init("www")

playAssistantSound()

# Start hotword detection in a separate thread
hotword_thread = threading.Thread(target=hotword)
hotword_thread.daemon = True
hotword_thread.start()

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
eel.start('index.html', mode=edge_path, host='localhost', port=8000, block=True)
