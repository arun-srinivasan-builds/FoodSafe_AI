import cv2
import numpy as np
import pyautogui
import subprocess
import threading
import time
import os
from datetime import datetime


# --------------------------------------------------
# Configuration
# --------------------------------------------------

FPS = 15

OUTPUT_DIR = os.path.join("assets", "demo")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    f"foodsafe_ai_demo_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
)

screen_width, screen_height = pyautogui.size()

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

video = cv2.VideoWriter(
    OUTPUT_FILE,
    fourcc,
    FPS,
    (screen_width, screen_height)
)

recording = True


# --------------------------------------------------
# Screen recording function
# --------------------------------------------------

def record_screen():
    global recording

    frame_interval = 1 / FPS

    while recording:
        start_time = time.time()

        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)

        # Convert RGB image to BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        video.write(frame)

        elapsed = time.time() - start_time
        sleep_time = frame_interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)


# --------------------------------------------------
# Start recorder
# --------------------------------------------------

print()
print("======================================")
print("       FoodSafe AI Demo Recorder")
print("======================================")
print()
print(f"Screen Resolution : {screen_width} x {screen_height}")
print(f"Recording FPS     : {FPS}")
print(f"Output File       : {OUTPUT_FILE}")
print()

record_thread = threading.Thread(target=record_screen)
record_thread.start()

print("Screen recording started.")
print()

# Give the recorder a moment before launching Streamlit
time.sleep(2)


# --------------------------------------------------
# Launch FoodSafe AI
# --------------------------------------------------

print("Launching FoodSafe AI...")
print()

streamlit_process = subprocess.Popen(
    [
        "streamlit",
        "run",
        "foodsafe_ai_app.py"
    ]
)

print("FoodSafe AI launched.")
print()

print("======================================")
print(" Suggested Demo Flow")
print("======================================")
print()
print("1. Show the FoodSafe AI home page")
print()
print("2. Click one pre-built sample question")
print()
print("3. Show the generated answer")
print("   and official FSSAI/FoSCoS source")
print()
print("4. Type this conversational question:")
print()
print(
    '   "I found a foreign object inside a sealed juice package. '
    'How do I complain to FSSAI?"'
)
print()
print("5. After the answer, type the follow-up:")
print()
print('   "What evidence should I keep for this issue?"')
print()
print("6. Show how the answer retains the previous context")
print()
print("7. Return to this terminal")
print()
print("======================================")
print()

input("Press ENTER when you are ready to stop recording...")


# --------------------------------------------------
# Stop recording
# --------------------------------------------------

print()
print("Stopping recording...")

recording = False
record_thread.join()

video.release()

print()
print("======================================")
print("       Recording Completed")
print("======================================")
print()
print(f"Video saved to:")
print(OUTPUT_FILE)
print()
print("Streamlit is still running.")
print("Press CTRL+C in the Streamlit terminal")
print("if you want to stop the application.")
print()