import time

class SimpleAgent:
    def __init__(self, name):
        self.name = name
        self.goal = "Scan file system for suspicious files"

    def act(self):
        print(f"[{self.name}] Starting task: {self.goal}")
        time.sleep(1)
        print(f"[{self.name}] Task completed (placeholder).")
