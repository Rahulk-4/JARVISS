import eel
import sys

eel.init("www")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
eel.start('index.html', mode=edge_path, host='localhost', port=8000, block=True)
