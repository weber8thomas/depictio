import time
import os

while True:
    for file in os.listdir("."):
        if file.endswith(".txt"):
            print("New file created:", file)
    time.sleep(5)
