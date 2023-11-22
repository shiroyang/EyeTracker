"""
This code will create the image stimuli for the experiment.
It will also handle the keyboard input.
"""
import cv2
import os
import random
import threading
from datetime import datetime
from pynput import keyboard
import pandas as pd
import numpy as np
from screeninfo import get_monitors

# Global variables
data_lock = threading.Lock()
now = datetime.now()
file_path = now.strftime('./Data_Collection/Data/Raw/Stimuli/%Y%m%d%H%M.csv')

is_recording = True
image_display_info = []
key_presses = []

FIXATION_CROSS_DURATION = 1
STIMULUS_DURATION = 3
GREY_DURATION = 1
TARGET_SIZE = (1920, 1080)

screen_width = get_monitors()[0].width
screen_height = get_monitors()[0].height

def place_image_center(screen, image):
    x_offset = screen_width // 2 - TARGET_SIZE[0] // 2
    y_offset = screen_height // 2 - TARGET_SIZE[1] // 2
    screen[y_offset:y_offset + image.shape[0], x_offset:x_offset + image.shape[1]] = image
    return screen


def wait_or_break(duration):
    global is_recording
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < duration:
        if not is_recording:
            return False
        cv2.waitKey(1)  # Check every 1 millisecond
    return True

# Function to display stimuli and record display times
def display_stimuli_and_record():
    global image_display_info, is_recording
    fixation_img = cv2.imread('Data_Collection/Img/Instructions/fixation.png')
    fixation_img = cv2.resize(fixation_img, TARGET_SIZE)
    grey_img = cv2.imread('Data_Collection/Img/Instructions/grey.png')
    grey_img = cv2.resize(grey_img, TARGET_SIZE)
    image_folder = 'Data_Collection/Img/Animals/'
    image_files = os.listdir(image_folder)
    random.shuffle(image_files)

    # Create a full-screen black canvas
    screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    for selected_image in image_files:
        with data_lock:
            if not is_recording:
                break

        image_path = os.path.join(image_folder, selected_image)
        img = cv2.imread(image_path)

        if img is None:
            print(f"Failed to load image from {image_path}")
            continue

        img = cv2.resize(img, TARGET_SIZE)

        show_time = datetime.now()
        image_display_info.append({"timestamp": show_time, "image_name": selected_image})

        # Display the images centered on the screen
        cv2.imshow('Stimulus', place_image_center(screen.copy(), fixation_img))
        wait_or_break(FIXATION_CROSS_DURATION)

        cv2.imshow('Stimulus', place_image_center(screen.copy(), img))
        wait_or_break(STIMULUS_DURATION)

        cv2.imshow('Stimulus', place_image_center(screen.copy(), grey_img))
        wait_or_break(GREY_DURATION)

    cv2.destroyAllWindows()

    combined_data = pd.DataFrame(image_display_info)
    combined_data['key'] = None  # Add a column for key presses
    combined_data.set_index('timestamp', inplace=True)
    return combined_data

# Function to handle keyboard input
def on_press(key):
    try:
        key_char = key.char
    except AttributeError:
        key_char = str(key)
    
    with data_lock:
        key_presses.append({"timestamp": datetime.now(), "key": key_char})
    
    if key == keyboard.Key.esc:
        global is_recording
        is_recording = False
        return False

# Main function
if __name__ == "__main__":
    thread_keyboard = threading.Thread(target=keyboard.Listener(on_press=on_press).start)
    thread_keyboard.start()

    combined_data = display_stimuli_and_record()

    # In the main function, after display_stimuli_and_record call:
    key_df = pd.DataFrame(key_presses)
    key_df.set_index('timestamp', inplace=True)

    # Merge the dataframes
    result_df = pd.concat([combined_data, key_df], axis=0).sort_index().reset_index()
    result_df.to_csv(file_path, index=False) 

    thread_keyboard.join()