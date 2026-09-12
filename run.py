import threading
import time
import webbrowser
import uvicorn

def open_browser():
    time.sleep(2)  # Server start hone ka wait
    webbrowser.open("http://127.0.0.1:8000/docs")

threading.Thread(target=open_browser).start()

uvicorn.run(
    "src.api.app:app",
    host="127.0.0.1",
    port=8000,
    reload=True
)