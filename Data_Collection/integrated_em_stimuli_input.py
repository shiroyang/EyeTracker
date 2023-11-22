
import cv2
import os
import random
import threading
from datetime import datetime
from pynput import keyboard
import pandas as pd
import numpy as np
from screeninfo import get_monitors
import tobii_research as tr

# Global variables for both functionalities
data_lock = threading.Lock()
now = datetime.now()
file_path_stimuli = now.strftime('./Data_Collection/Data/Raw/Stimuli/%Y%m%d%H%M.csv')
file_path_em = now.strftime('./Data_Collection/Data/Raw/EM/%Y%m%d%H%M.csv')

is_recording = True
image_display_info = []
key_presses = []

FIXATION_CROSS_DURATION = 1
STIMULUS_DURATION = 3
GREY_DURATION = 1
TARGET_SIZE = (1920, 1080)

screen_width = get_monitors()[0].width
screen_height = get_monitors()[0].height

# Function to place image at the center of the screen
def place_image_center(screen, image):
    x_offset = screen_width // 2 - TARGET_SIZE[0] // 2
    y_offset = screen_height // 2 - TARGET_SIZE[1] // 2
    screen[y_offset:y_offset + image.shape[0], x_offset:x_offset + image.shape[1]] = image
    return screen

# Function for the time control
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

            # Display fixation cross
            place_image_center(screen, fixation_img)
            cv2.imshow('Stimuli', screen)
            cv2.setWindowProperty('Stimuli', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            if not wait_or_break(FIXATION_CROSS_DURATION):
                break

            # Display the stimulus
            img_path = os.path.join(image_folder, selected_image)
            image = cv2.imread(img_path)
            image = cv2.resize(image, TARGET_SIZE)
            place_image_center(screen, image)
            cv2.imshow('Stimuli', screen)
            start_time = datetime.now()
            if not wait_or_break(STIMULUS_DURATION):
                break
            end_time = datetime.now()
            image_display_info.append({"image": selected_image, "start_time": start_time, "end_time": end_time})

            # Display grey screen
            place_image_center(screen, grey_img)
            cv2.imshow('Stimuli', screen)
            if not wait_or_break(GREY_DURATION):
                break

    cv2.destroyAllWindows()

# Function to collect eye tracker data
def eye_tracker_input():
    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]

    def gaze_data_callback(gaze_data):
        with data_lock:
            gaze_dict = {
                "timestamp": datetime.now(),
                "left_gaze_point_on_display_area": gaze_data["left_gaze_point_on_display_area"],
                "left_gaze_point_validity": gaze_data["left_gaze_point_validity"],
                "right_gaze_point_on_display_area": gaze_data["right_gaze_point_on_display_area"],
                "right_gaze_point_validity": gaze_data["right_gaze_point_validity"],
                "left_pupil_diameter": gaze_data["left_pupil_diameter"],
                "left_pupil_validity": gaze_data["left_pupil_validity"],
                "right_pupil_diameter": gaze_data["right_pupil_diameter"],
                "right_pupil_validity": gaze_data["right_pupil_validity"]
            }
            df = pd.DataFrame([gaze_dict])
            df.to_csv(file_path_em, mode='a', index=False)

    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

# Function to record keyboard inputs
def on_press(key):
    try:
        key_data = {'timestamp': datetime.now(), 'key': key.char}
    except AttributeError:
        key_data = {'timestamp': datetime.now(), 'key': str(key)}
    with data_lock:
        key_presses.append(key_data)

# Main function
def main():
    global is_recording

    # Setting up threads for each task
    thread_display = threading.Thread(target=display_stimuli_and_record)
    thread_eye_tracker = threading.Thread(target=eye_tracker_input)
    thread_keyboard = threading.Thread(target=keyboard.Listener(on_press=on_press).start)

    # Start threads
    thread_display.start()
    thread_eye_tracker.start()
    thread_keyboard.start()

    # Wait for display thread to finish
    thread_display.join()
    is_recording = False

    # Wait for other threads to finish
    thread_eye_tracker.join()
    thread_keyboard.join()

    # Processing and saving data
    stimuli_df = pd.DataFrame(image_display_info)
    key_df = pd.DataFrame(key_presses)
    combined_data = pd.concat([stimuli_df, key_df], axis=0).sort_index().reset_index()
    combined_data.to_csv(file_path_stimuli, index=False)

if __name__ == "__main__":
    main()
