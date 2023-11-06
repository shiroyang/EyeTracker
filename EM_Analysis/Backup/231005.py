import pandas as pd
import numpy as np
import math

class EyeMovement:
    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)
        self.add_eye_state()

    def calculate_distance(self, p1, p2):
        """Calculate the euclidean distance between two points."""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def convert_to_deg_per_sec(self, p1, p2):
        """Convert distance to degrees per second."""
        # Given the user is 65cm away from a 609.2mm x 349.4mm screen.
        # Using basic trigonometry.
        distance_mm = self.calculate_distance(p1, p2) * 609.2
        radian = math.atan(distance_mm / 650)
        return math.degrees(radian) * 60

    def interpolate(self, start_index, end_index):
        """Linearly interpolate missing values."""
        # This can be further improved by considering screen bounds
        x0, y0 = self.data.iloc[start_index]['left_gaze_point_on_display_area']
        x1, y1 = self.data.iloc[end_index]['left_gaze_point_on_display_area']
        
        for i in range(start_index + 1, end_index):
            ratio = (i - start_index) / (end_index - start_index)
            self.data.at[i, 'left_gaze_point_on_display_area'] = (
                x0 + ratio * (x1 - x0),
                y0 + ratio * (y1 - y0)
            )

    def add_eye_state(self):
        """Add the eye state to the dataframe."""
        states = []
        i = 0
        while i < len(self.data):
            row = self.data.iloc[i]
            if row['left_gaze_point_validity'] == 0 and row['right_gaze_point_validity'] == 0:
                start_missing = i
                while i < len(self.data) and self.data.iloc[i]['left_gaze_point_validity'] == 0 and self.data.iloc[i]['right_gaze_point_validity'] == 0:
                    i += 1
                end_missing = i - 1

                missing_frames = end_missing - start_missing + 1
                if missing_frames < 6:
                    states.extend(['Error State'] * missing_frames)
                    self.interpolate(start_missing, end_missing)
                else:
                    states.extend(['Blink'] * missing_frames)
            else:
                if i + 1 < len(self.data):
                    next_row = self.data.iloc[i + 1]
                    v = self.convert_to_deg_per_sec(
                        row['left_gaze_point_on_display_area'],
                        next_row['left_gaze_point_on_display_area']
                    )
                    if v >= 30:
                        states.append('Saccade')
                    else:
                        states.append('Fixation')
                else:
                    states.append('Fixation')
                i += 1

        self.data['eye_state'] = states

# Usage
eye_movement = EyeMovement('YYYYMMDDHHMM.csv')
eye_movement.data.to_csv('updated_YYYYMMDDHHMM.csv', index=False)