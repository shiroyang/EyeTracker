"""
Issue 1209: 
This code will display stimuli immidiately. 
However, launching eye tracker will take some time.
Therefore, I need to add an instruction to show "press enter to start the experiment".

Please import StimuliExperiment class from this script.
This class will create the image stimuli for the experiment and handle the keyboard input simultaneously.
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
import time

class StimuliExperiment:
    FIXATION_CROSS_DURATION = 1
    STIMULUS_DURATION = 3
    GREY_DURATION = 1
    TARGET_SIZE = (1920, 1080)

    def __init__(self):
        self.screen_width = get_monitors()[0].width
        self.screen_height = get_monitors()[0].height
        self.full_screen = (self.screen_width, self.screen_height)
        print(self.screen_width, self.screen_height)

        self.is_recording = True
        self.image_display_info = []
        self.key_presses = []

        self.data_lock = threading.Lock()
        now = datetime.now()
        self.file_path = now.strftime('./Data_Collection/Data/Raw/Stimuli/%Y%m%d%H%M.csv')
        
    def show_start_instruction(self):
        # Create an image with the text "Press Enter to start the experiment"
        instruction_img = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

        # Set the window to full-screen
        cv2.namedWindow('Stimulus', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Stimulus', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Initialize countdown time (3 seconds)
        countdown_time = 3
        start_time = time.time()

        while True:
            # Calculate remaining time
            elapsed_time = time.time() - start_time
            remaining_time = max(0, countdown_time - int(elapsed_time))

            # Update and show the instruction image with remaining time
            instruction_img_updated = instruction_img.copy()
            cv2.putText(instruction_img_updated, f"Press Enter to start the experiment in {remaining_time}s", 
                        (100, self.screen_height // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1, 
                        (255, 255, 255), 
                        2, 
                        cv2.LINE_AA)
            cv2.imshow('Stimulus', instruction_img_updated)

            # Check for Enter key press after countdown
            if cv2.waitKey(1) & 0xFF == 13 and elapsed_time > countdown_time:  # 13 is the Enter Key
                break

        cv2.destroyAllWindows()

    def wait_or_break(self, duration):
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < duration:
            if not self.is_recording:
                return False
            cv2.waitKey(1)
        return True

    def display_stimuli_and_record(self):
        fixation_img = cv2.imread('Data_Collection/Img/Instructions/fixation.png')
        fixation_img = cv2.resize(fixation_img, self.full_screen)
        grey_img = cv2.imread('Data_Collection/Img/Instructions/grey.png')
        grey_img = cv2.resize(grey_img, self.full_screen)
        image_folder = 'Data_Collection/Img/Animals/'
        image_files = os.listdir(image_folder)
        random.shuffle(image_files)

        screen = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

        cv2.namedWindow('Stimulus', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Stimulus', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


        for selected_image in image_files:
            with self.data_lock:
                if not self.is_recording:
                    break

            image_path = os.path.join(image_folder, selected_image)
            img = cv2.imread(image_path)

            if img is None:
                print(f"Failed to load image from {image_path}")
                continue

            img = cv2.resize(img, self.full_screen)

            show_time = datetime.now()
            self.image_display_info.append({"timestamp": show_time, "image_name": selected_image})

            cv2.imshow('Stimulus', fixation_img)
            self.wait_or_break(self.FIXATION_CROSS_DURATION)

            cv2.imshow('Stimulus', img)
            self.wait_or_break(self.STIMULUS_DURATION)

            cv2.imshow('Stimulus', grey_img)
            self.wait_or_break(self.GREY_DURATION)

        cv2.destroyAllWindows()

        combined_data = pd.DataFrame(self.image_display_info)
        combined_data['key'] = None
        combined_data.set_index('timestamp', inplace=True)
        return combined_data

    def on_press(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)

        with self.data_lock:
            self.key_presses.append({"timestamp": datetime.now(), "key": key_char})

        if key == keyboard.Key.esc:
            self.is_recording = False
            return False

    def run(self):
        
        listener = keyboard.Listener(on_press=self.on_press)
        thread_keyboard = threading.Thread(target=listener.start)
        thread_keyboard.start()

        self.show_start_instruction()
        combined_data = self.display_stimuli_and_record()

        key_df = pd.DataFrame(self.key_presses)
        key_df.set_index('timestamp', inplace=True)

        result_df = pd.concat([combined_data, key_df], axis=0).sort_index().reset_index()
        result_df.to_csv(self.file_path, index=False)

        thread_keyboard.join()

if __name__ == "__main__":
    experiment = StimuliExperiment()
    experiment.run()