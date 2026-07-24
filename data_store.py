import threading
from datetime import datetime

class DataStore: 
    def __init__(self):
        self._lock = threading.Lock()
        
        self._data = {
            "indoor": None,
            "outdoor": None,
            "indoor_time": None,
            "outdoor_time": None,
        }
        
    def update_indoor(self, reading):
        with self._lock:
            if reading is not None:
                self._data["indoor"] = reading
                self._data["indoor_time"] = datetime.now()
    
    def update_outdoor(self, reading):
        with self._lock:
            if reading is not None:
                self._data["outdoor"] = reading
                self._data["outdoor_time"] = datetime.now()
                
    def snapshot(self):
        with self._lock:
            return dict(self._data)