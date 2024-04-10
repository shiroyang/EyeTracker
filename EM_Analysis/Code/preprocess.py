"""
Step 3.

Please run this code after step 1 and step 2 in Data_Collection folder.
This code will process the eye tracking data and identify the eye state for each frame.

The result will be saved in the Data_Collection/Data/Processed folder.
"""

import os
import pandas as pd
from math import tan, pi, sqrt
import ast
    
def get_matched_files():
    files_input = os.listdir(EyeMovement.INPUT_DIR)
    files_target = os.listdir(EyeMovement.TARGET_DIR)
    # return the files that are in the input folder but not in the target folder
    return list(set(files_input) - set(files_target))
    
class EyeMovement:
    INPUT_DIR = './EM_Analysis/Data/Synced/'
    TARGET_DIR = './EM_Analysis/Data/Processed/'

    SCREEN_SIZE_W = 596.7  # mm
    PIXEL_PER_MM = SCREEN_SIZE_W / 1920
    SCREEN_SIZE_H = 335.7  # mm
    SCREEN_TO_EYE_DIST = 650  # mm
    SACCADE_THRESHOLD = pi / 9  # 20 degrees
    FIXATION_THRESHOLD = 6 # 6 frames = 100ms
    SAMPLING_RATE = 60  # Hz


    def __init__(self, filename):
        self.filename = filename
        self.filepath = os.path.join(EyeMovement.INPUT_DIR, filename)
        self.data = self._load_data()
        self.eye_to_use = None
        self.col = None
        self.validity_col = None
        self.states = []

    def _convert_to_tuple(self, value):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # Handle the exception or return a default value
            return (None, None)

    def _load_data(self) -> pd.DataFrame:
        converters = {
            'left_gaze_point_on_display_area': self._convert_to_tuple,
            'right_gaze_point_on_display_area': self._convert_to_tuple
        }
        return pd.read_csv(self.filepath, converters=converters)
    
    def decide_eye_to_use(self):
        left_valid = self.data['left_gaze_point_validity'].sum()
        right_valid = self.data['right_gaze_point_validity'].sum()
        self.eye_to_use = 'left' if left_valid > right_valid else 'right'
        self.col = f'{self.eye_to_use}_gaze_point_on_display_area'
        self.validity_col = f'{self.eye_to_use}_gaze_point_validity'
        self.data['eye_to_use'] = self.eye_to_use

    def interpolate_coordinates(self):
    
        idx = 0
        while idx < len(self.data):
            # If the current point is missing
            if self.data.at[idx, self.validity_col] == 0:
                start_idx = idx
                while idx < len(self.data) and self.data.at[idx, self.validity_col] == 0:
                    idx += 1
                end_idx = idx
                
                # Check if the count of missing points is 4 or fewer
                if 1 <= (end_idx - start_idx) <= 4:
                    # Ensure that both bounding points are valid for interpolation
                    if start_idx > 0 and end_idx < len(self.data):
                        x1, y1 = self.data.at[start_idx - 1, self.col]
                        x2, y2 = self.data.at[end_idx, self.col]
                        
                        # Linear interpolation for each missing point
                        for j in range(start_idx, end_idx):
                            alpha = (j - start_idx + 1) / (end_idx - start_idx + 1)
                            x = x1 + alpha * (x2 - x1)
                            y = y1 + alpha * (y2 - y1)
                            self.data.at[j, self.col] = (x, y)
                            # set validity to 2 to indicate that the point is interpolated
                            self.data.at[j, self.validity_col] = 2
            else:
                idx += 1


    def identify_blink(self):
        idx = 0
        total_rows = len(self.data)

        while idx < total_rows:
            # Check if both eyes' data is missing at the current index
            if self.data.at[idx, self.validity_col] == 0:
                blink_start_idx = idx
                while (idx < total_rows and self.data.at[idx, self.validity_col] == 0):
                    idx += 1
                blink_end_idx = idx

                # Check if the consecutive missing frames count as a blink or just error states
                if blink_end_idx - blink_start_idx >= 5:
                    self.states.extend(['Blink'] * (blink_end_idx - blink_start_idx))
                else:
                    self.states.extend(['Error'] * (blink_end_idx - blink_start_idx))
            else:
                self.states.append(None)
                idx += 1


    def identify_saccade(self):
        col = f'{self.eye_to_use}_gaze_point_on_display_area'
        for i in range(len(self.data) - 1):
            if self.states[i]:  # Skip already identified states
                continue
            
            x1, y1 = self.data.at[i, col]
            x2, y2 = self.data.at[i+1, col]
            if x1 is None or x2 is None or y1 is None or y2 is None: continue
            # Convert to actual coordinates on monitor
            x1, y1 = x1 * EyeMovement.SCREEN_SIZE_W, y1 * EyeMovement.SCREEN_SIZE_H
            x2, y2 = x2 * EyeMovement.SCREEN_SIZE_W, y2 * EyeMovement.SCREEN_SIZE_H
            
            # Calculate the velocity, pixel/sec
            v = sqrt((x2 - x1)**2 + (y2 - y1)**2) * EyeMovement.SAMPLING_RATE * EyeMovement.PIXEL_PER_MM # 60 Hz sampling rate
            if v >= EyeMovement.SCREEN_TO_EYE_DIST * tan(EyeMovement.SACCADE_THRESHOLD):  # 30 degree per second threshold
                self.states[i] = 'Saccade'

    def identify_fixation(self):
        for i, state in enumerate(self.states):
            if not state:
                self.states[i] = 'Fixation'

    def compute_center_point(self):
        col = f'{self.eye_to_use}_gaze_point_on_display_area'
        fixation_start = None
        self.data['fixation_center'] = [(None, None)] * len(self.data)

        # Append a non-fixation state to handle fixation at the end of data
        states = self.states + ['End']

        for i, state in enumerate(states):
            if state == 'Fixation':
                if fixation_start is None:
                    fixation_start = i  # Start of a new fixation
            elif fixation_start is not None:
                # Fixation has ended, check if it was longer than 6 frames
                if i - fixation_start > EyeMovement.FIXATION_THRESHOLD:
                    # Calculate fixation center for the points between fixation_start and i
                    fixation_points = self.data[col][fixation_start:i]
                    x_center = fixation_points.apply(lambda p: p[0]).mean()
                    y_center = fixation_points.apply(lambda p: p[1]).mean()
                    center_point = (x_center, y_center)
                    for j in range(fixation_start, i):
                        self.data.at[j, 'fixation_center'] = center_point
                fixation_start = None  # Reset for the next fixation
    
    def add_error_state(self):
        for i in range(len(self.data)):
            if self.states[i] == 'Fixation' and self.data.at[i, 'fixation_center'] == (None, None):
                self.states[i] = 'Error'

    def add_state_to_csv(self):
        self.data['eye_state'] = self.states
        self.data.to_csv(os.path.join(EyeMovement.TARGET_DIR, self.filename) , index=False)

    def run(self):
        self.decide_eye_to_use()
        self.interpolate_coordinates()
        self.identify_blink()
        self.identify_saccade()
        self.identify_fixation()
        self.compute_center_point()
        self.add_error_state()
        self.add_state_to_csv()


if __name__ == "__main__":
    matched_files = get_matched_files()
    for filename in matched_files:
        print(f"Now processing file: {filename}\n")
        em = EyeMovement(filename)
        em.run()