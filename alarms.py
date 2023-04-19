# import datetime
import json
import time
import threading
import pystray
from PIL import Image
from notifypy import Notify
from os.path import dirname, realpath, getmtime, isfile
from datetime import datetime, date
from subprocess import run, Popen

# Flag variable to stop the counter thread
stop_flag = False
alarms = {
    'filename': None,
    'filemtime': None,
    'date': None,
    'data': None,
}

__dir__ = dirname(realpath(__file__))
APP_ICON =  __dir__ + "/alarms.png"
ICON_ERROR =  __dir__ + "/error.png"
ICON_INFO =  __dir__ + "/info.png"
AUDIO_DING = __dir__ + "/ding.wav"
AUDIO_BEEP = __dir__ + "/beep.wav"

def notify(title, message, icon = None):
  notification = Notify()
  notification.title = title
  notification.message = message
  notification.icon = APP_ICON if not icon else icon
  notification.audio = AUDIO_BEEP if notification.icon==APP_ICON else AUDIO_DING
  notification.urgency = "critical" if notification.icon==APP_ICON else "normal"
  notification.send(block=False)

def load_alarms_file(today):
    global alarms, __dir__
    
    alarms["date"] = today
    try:
        alarms["filename"] = __dir__ + today.strftime("/%Y/%m") + ".json"
        with open(alarms["filename"]) as f:
            data = json.load(f)
            day = str(today.day)
            alarms["data"] = data[day] if day in data else None
            alarms["filemtime"] = getmtime(alarms["filename"])
        notify("Success", "File " + alarms["filename"] + " loaded", ICON_INFO)
    except FileNotFoundError:
        notify("Error", "Error: File " + alarms["filename"] + " not found.", ICON_ERROR)
        alarms["data"] = None
        alarms["filemtime"] = None
    print(alarms)

# Function to update the counter every second
def update_counter():
    global today, alarms, tray_icon
    while not stop_flag:
        if not alarms["filename"] \
            or alarms["date"]!=date.today() \
            or (isfile(alarms["filename"]) and alarms["filemtime"] != getmtime(alarms["filename"])):
                load_alarms_file(date.today())

        if datetime.now().second==0:
            hm = datetime.now().strftime("%H:%M")
            if alarms["data"] and hm in alarms["data"]:
                    notify(hm + " - " + alarms["data"][hm]["title"], alarms["data"][hm]["msg"])
        
        time.sleep(1)

# Function to display the system tray icon
def show_tray_icon():
    global tray_icon

    # Create an image to use as the icon
    icon_image = Image.open(APP_ICON)

    # Define the menu items for the tray icon
    menu_items = [
        pystray.MenuItem("edit", lambda: run(["code", alarms["filename"]])),
        pystray.MenuItem("Exit", lambda: stop_threads())
    ]

    # Create the tray icon object
    tray_icon = pystray.Icon("example", icon_image, "Alarms", menu_items)

    # Start the tray icon
    tray_icon.run()

# Function to stop the thread and exit the program
def stop_threads():
    global stop_flag, tray_icon
    stop_flag = True
    tray_icon.stop()

# Create a new thread for the counter update function
counter_thread = threading.Thread(target=update_counter)

# Start the counter thread
counter_thread.start()

# Start the system tray icon in a separate thread
tray_thread = threading.Thread(target=show_tray_icon)
tray_thread.start()

# Wait for the counter thread to finish (this will never happen in this example code)
counter_thread.join()
