import time
from threading import Lock

class SpamChecker:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self.data = {}  # Stores user_id -> list of timestamps
        self.interval = 10  # Interval in seconds to check for spam
        self.max_messages = 3  # Max messages allowed within the interval

    # returns True for span, false otherwise
    def add_message(self, user_id):
        current_time = time.time()

        # Ensure user_id has an entry in the data dictionary
        if user_id not in self.data:
            self.data[user_id] = []

        # Remove timestamps that are outside the interval
        self.data[user_id] = [ts for ts in self.data[user_id] if current_time - ts <= self.interval]

        # Check if adding a new timestamp would exceed the limit
        is_spam = len(self.data[user_id]) >= self.max_messages

        # Add the current timestamp
        self.data[user_id].append(current_time)

        return is_spam
