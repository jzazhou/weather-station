import display
import ui

import threading
import time
from datetime import datetime

from config import SENSOR_INTERVAL, API_INTERVAL
from data_store import DataStore
from sensors import read_bme688
from weather_api import fetch_outdoor_weather

store = DataStore()

def sensor_worker():
    while True:
        store.update_indoor(read_bme688())
        time.sleep(SENSOR_INTERVAL)

def api_worker():
    while True:
        store.update_outdoor(fetch_outdoor_weather())
        time.sleep(API_INTERVAL)
        
def main():
    print("Starting weather station...\n")
    
    threading.Thread(target=sensor_worker, daemon=True).start()
    threading.Thread(target=api_worker, daemon=True).start()
    
    time.sleep(2)
    
    last_render = None
    
    try:
        while True:
            now = datetime.now()

            # Only redraw when the displayed minute changes or new data
            # arrives. The clock shows HH:MM, so re-rendering 10 times a
            # second would redraw an identical frame ~600 times per
            # minute. This cuts CPU use dramatically — which matters on
            # a 2GB Pi that also has to stay responsive.
            data = store.snapshot()
            fingerprint = (
                now.strftime("%H:%M"),
                data.get("indoor_time"),
                data.get("outdoor_time"),
            )

            if fingerprint != last_render:
                display.show(ui.render(data, now))
                last_render = fingerprint

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nShutting down.")

if __name__ == "__main__":
    main()