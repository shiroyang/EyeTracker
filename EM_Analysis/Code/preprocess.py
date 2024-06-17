"""
Step 3.

Please run this code after step 1 and step 2 in Data_Collection folder.
This code will process the eye tracking data and identify the eye state for each frame.

The result will be saved in the Data_Collection/Data/Processed folder.
"""

import os
import pandas as pd
import numpy as np
from math import tan, pi, sqrt
from functools import cache
import ast

def get_matched_files():
    files_input = os.listdir(EyeMovement.INPUT_DIR)
    files_target = os.listdir(EyeMovement.TARGET_DIR)
    # return the files that are in the input folder but not in the target folder
    return list(set(files_input) - set(files_target))
    
class EyeMovement:
    INPUT_DIR = './Data_Collection/Data/Synced/'
    TARGET_DIR = './Data_Collection/Data/Processed/'

    SCREEN_SIZE_W = 596.7  # mm
    PIXEL_PER_MM = SCREEN_SIZE_W / 1920
    SCREEN_SIZE_H = 335.7  # mm
    SCREEN_TO_EYE_DIST = 650  # mm
    BLINK_THRESHOLD = 5  # 5 consecutive missing frames
    SAMPLING_RATE = 60  # Hz

    # IVT parameters
    IVT_SACCADE_THRESHOLD = 30  # 30 degree per second
    IVT_FIXATION_THRESHOLD = 6  # Fixation is at least 100ms

    def __init__(self, filename):
        self.filename = filename
        self.filepath = os.path.join(EyeMovement.INPUT_DIR, filename)
        self.data = self._load_data()
        self.eye_to_use = None
        self.col = None
        self.validity_col = None
        self.states = []
        self.blink = []

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
            # Check if the eye data is missing at the current index
            if self.data.at[idx, self.validity_col] == 0:
                blink_start_idx = idx
                while (idx < total_rows and self.data.at[idx, self.validity_col] == 0):
                    idx += 1
                blink_end_idx = idx

                # Check if the consecutive missing frames count as a blink or just error states
                if blink_end_idx - blink_start_idx >= EyeMovement.BLINK_THRESHOLD:
                    self.blink.extend(['Blink'] * (blink_end_idx - blink_start_idx))
                else:
                    self.blink.extend(['Error'] * (blink_end_idx - blink_start_idx))
            else:
                self.blink.append(None)
                idx += 1
                
    def visual_angle_calculation(self, p1, p2):
        # Convert to actual coordinates on monitor
        x1, y1 = p1[0] * EyeMovement.SCREEN_SIZE_W, p1[1] * EyeMovement.SCREEN_SIZE_H
        x2, y2 = p2[0] * EyeMovement.SCREEN_SIZE_W, p2[1] * EyeMovement.SCREEN_SIZE_H
        d = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        theta = np.arctan(d / EyeMovement.SCREEN_TO_EYE_DIST)
        theta = np.rad2deg(theta)
        return theta
                
    def IVT(self):
        """
        Calculate the distance between each consecutive point, 
        if the distance is greater than the threshold, then it is a saccade
        The rest of the points are fixations, however, if the fixation is less than 6 frames, it should be considered as an error
        identify saccade -> identify fixation -> compute center point -> add error state
        """
        self.IVT_states = self.blink[:]
        
        # identify saccade
        col = f'{self.eye_to_use}_gaze_point_on_display_area'
        for i in range(len(self.data) - 1):
            if self.IVT_states[i]:  # Skip already identified states
                continue
            
            p1 = self.data.at[i, col]
            p2 = self.data.at[i+1, col]
            # Ignore the point where value is missing
            if p1[0] is None or p2[0] is None or p1[1] is None or p2[1] is None: continue
        
            # Calculate the velocity, 
            v = self.visual_angle_calculation(p1, p2) * EyeMovement.SAMPLING_RATE # 60 Hz sampling rate
            if v >= EyeMovement.IVT_SACCADE_THRESHOLD:
                self.IVT_states[i] = 'Saccade'
        
        # identify fixation
        for i, state in enumerate(self.IVT_states):
            if not state:
                self.IVT_states[i] = 'Fixation'

        # add state to the dataframe
        self.data['IVT_state'] = self.IVT_states
        
        # compute fixation centroid
        fixation_start = None
        self.data['IVT_fixation_centroid'] = [(None, None)] * len(self.data)
        IVT_states = self.IVT_states + ['End']
        
        for i, state in enumerate(IVT_states):
            if state == 'Fixation':
                if fixation_start is None:
                    fixation_start = i
            # Fixation has ended, check if it was longer or equal to 6 frames
            elif fixation_start is not None:
                if i - fixation_start >= EyeMovement.IVT_FIXATION_THRESHOLD:
                    fixation_points = self.data[col][fixation_start:i]
                    x_center = fixation_points.apply(lambda p: p[0]).mean()
                    y_center = fixation_points.apply(lambda p: p[1]).mean()
                    center_point = (x_center, y_center)
                    for j in range(fixation_start, i):
                        self.data.at[j, 'IVT_fixation_centroid'] = center_point
                fixation_start = None
        
        # add error state
        for i in range(len(self.data)):
            if self.data.at[i, 'IVT_state'] == 'Fixation' and self.data.at[i, 'IVT_fixation_centroid'] == (None, None):
                self.data.at[i, 'IVT_state'] = 'Error'
                
        # For 3 cosecutive eye states, change [Saccade, Error, Saccade] to [Saccade, Saccade, Saccade]
        for i in range(len(self.data)-2):
            first_state = self.data.at[i, 'IVT_state']
            second_state = self.data.at[i+1, 'IVT_state']
            third_state = self.data.at[i+2, 'IVT_state']
            if first_state == 'Saccade' and second_state == 'Error' and third_state == 'Saccade':
                self.data.at[i+1, 'IVT_state'] = 'Saccade'

    def add_state_to_csv(self):
        self.data.to_csv(os.path.join(EyeMovement.TARGET_DIR, self.filename), index=False)

    def run(self):
        self.decide_eye_to_use()
        self.interpolate_coordinates()
        self.identify_blink()
        self.IVT()
        self.add_state_to_csv()

if __name__ == "__main__":
    matched_files = get_matched_files()
    for filename in matched_files:
        print(f"Now processing file: {filename}\n")
        em = EyeMovement(filename)
        em.run()