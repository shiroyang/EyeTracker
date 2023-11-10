#import tobii_research as tr
from datetime import datetime
from pynput import keyboard
import pandas as pd
import time
import threading
import cv2
import os
import random

# Global variables
data_lock = threading.Lock()
now = datetime.now()
file_em = now.strftime('./Data_Collection/Data/Raw/EM/%Y%m%d%H%M.csv')
file_stimuli = now.strftime('./Data_Collection/Data/Raw/Stimuli/%Y%m%d%H%M.csv')
is_recording = True  
image_display_info = []

STIMULUS_DURATION = 3
GREY_DURATION = 1

# def eye_tracker_input():
#     global file_name
#     found_eyetrackers = tr.find_all_eyetrackers()
#     my_eyetracker = found_eyetrackers[0]

#     def gaze_data_callback(gaze_data):
#         with data_lock:
#             gaze_dict = {
#                 "timestamp": time.time(),
#                 "left_gaze_point_on_display_area": gaze_data["left_gaze_point_on_display_area"],
#                 "left_gaze_point_validity": gaze_data["left_gaze_point_validity"],
#                 "right_gaze_point_on_display_area": gaze_data["right_gaze_point_on_display_area"],
#                 "right_gaze_point_validity": gaze_data["right_gaze_point_validity"],
#                 "left_pupil_diameter": gaze_data["left_pupil_diameter"],
#                 "left_pupil_validity": gaze_data["left_pupil_validity"],
#                 "right_pupil_diameter": gaze_data["right_pupil_diameter"],
#                 "right_pupil_validity": gaze_data["right_pupil_validity"]
#             }
#             df = pd.DataFrame([gaze_dict])
#             df.to_csv(file_em, mode='a', index=False)

#     my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

# Visual Stimuli Display and Recording Function
def display_stimuli_and_record():
    global image_display_info, is_recording
    fixation_img = cv2.imread('Data_Collection/Img/Instructions/fixation.png')
    grey_img = cv2.imread('Data_Collection/Img/Instructions/grey.png')
    image_folder = 'Data_Collection/Img/Animals/'
    image_files = os.listdir(image_folder)
    random.shuffle(image_files)  # Shuffle the list of images

    for selected_image in image_files:
        if not is_recording:
            break
    
        image_path = os.path.join(image_folder, selected_image)
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to load image from {image_path}")
            continue
        show_time = datetime.now()
        image_display_info.append((show_time, selected_image))

        img_dict = {
            "timestamp": time.time(),
            "image_name": selected_image
        }

        cv2.imshow('fixation', fixation_img)
        cv2.waitKey(GREY_DURATION * 1000)
        cv2.destroyAllWindows()

        cv2.imshow('Stimulus', img)
        cv2.waitKey(STIMULUS_DURATION * 1000)
        cv2.destroyAllWindows()
        
        cv2.imshow('grey', grey_img)
        cv2.waitKey(GREY_DURATION * 1000)
        cv2.destroyAllWindows()
        
        df = pd.DataFrame([img_dict])
        df.to_csv(file_stimuli, mode='a', index=False)

def on_press(key):
    try:
        print(f'Key {key.char} pressed')
    except AttributeError:
        print(f'Special key {key} pressed')
    if key == keyboard.Key.esc:
        global is_recording
        is_recording = False
        return False

def keyboard_input():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
        
# Main thread
if __name__ == "__main__":

    # thread_eye = threading.Thread(target=eye_tracker_input)
    thread_display = threading.Thread(target=display_stimuli_and_record)
    thread_keyboard = threading.Thread(target=keyboard_input)

    # thread_eye.start()
    thread_display.start()
    thread_keyboard.start()

    # thread_eye.join()
    thread_display.join()
    thread_keyboard.join()