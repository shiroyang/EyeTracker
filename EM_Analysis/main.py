import pandas as pd
import math

class EyeMovement:

    def __init__(self, filepath):
        self.data = pd.read_csv(filepath)
        self.states = []

    def decide_eye_to_use(self):
        left_valid = self.data['left_gaze_point_validity'].sum()
        right_valid = self.data['right_gaze_point_validity'].sum()
        self.eye_to_use = 'left' if left_valid > right_valid else 'right'

    def interpolate_coordinates(self):
        # Assumes self.decide_eye_to_use() has been called
        col = f'{self.eye_to_use}_gaze_point_on_display_area'
        validity_col = f'{self.eye_to_use}_gaze_point_validity'
        
        idx = 0
        while idx < len(self.data):
            # If the current point is missing
            if self.data.at[idx, validity_col] == 0:
                start_idx = idx
                while idx < len(self.data) and self.data.at[idx, validity_col] == 0:
                    idx += 1
                end_idx = idx
                
                # Check if the count of missing points is 5 or fewer
                if 1 <= (end_idx - start_idx) <= 5:
                    # Ensure that both bounding points are valid for interpolation
                    if start_idx > 0 and end_idx < len(self.data):
                        x1, y1 = self.data.at[start_idx - 1, col]
                        x2, y2 = self.data.at[end_idx, col]
                        
                        # Linear interpolation for each missing point
                        for j in range(start_idx, end_idx):
                            alpha = (j - start_idx + 1) / (end_idx - start_idx + 1)
                            x = x1 + alpha * (x2 - x1)
                            y = y1 + alpha * (y2 - y1)
                            self.data.at[j, col] = (x, y)
            else:
                idx += 1


    def identify_blink(self):
        idx = 0
        total_rows = len(self.data)

        while idx < total_rows:
            # Check if both eyes' data is missing at the current index
            if (self.data.at[idx, 'left_gaze_point_validity'] == 0 and 
                self.data.at[idx, 'right_gaze_point_validity'] == 0):
                blink_start_idx = idx
                while (idx < total_rows and 
                    self.data.at[idx, 'left_gaze_point_validity'] == 0 and 
                    self.data.at[idx, 'right_gaze_point_validity'] == 0):
                    idx += 1
                blink_end_idx = idx

                # Check if the consecutive missing frames count as a blink or just error states
                if blink_end_idx - blink_start_idx >= 6:
                    self.states.extend(['Blink'] * (blink_end_idx - blink_start_idx))
                else:
                    self.states.extend(['Error State'] * (blink_end_idx - blink_start_idx))
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
            
            # Convert to actual coordinates on monitor
            x1, y1 = x1 * 609.2, y1 * 349.4
            x2, y2 = x2 * 609.2, y2 * 349.4
            
            # Calculate the velocity
            v = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 60  # 60 Hz sampling rate
            if v >= 30:  # 30 degree per second threshold
                self.states[i] = 'Saccade'

    def identify_fixation(self):
        for i, state in enumerate(self.states):
            if not state:
                self.states[i] = 'Fixation'

    def compute_center_point(self):
        # Calculate for fixations lasting longer than 100ms
        col = f'{self.eye_to_use}_gaze_point_on_display_area'
        fixation_start = None
        
        for i, state in enumerate(self.states):
            if state == 'Fixation':
                if fixation_start is None:
                    fixation_start = i
            else:
                if fixation_start is not None:
                    duration = (i - fixation_start) * (1/60)  # 60 Hz sampling rate
                    if duration > 0.1:  # Lasting longer than 100ms
                        fixations = self.data[col][fixation_start:i]
                        x_center = fixations.apply(lambda p: p[0]).mean()
                        y_center = fixations.apply(lambda p: p[1]).mean()
                        print(f"Center of fixation from {fixation_start} to {i}: ({x_center}, {y_center})")
                    fixation_start = None

    def add_state_to_csv(self, filepath):
        self.data['eye_state'] = self.states
        self.data.to_csv(filepath, index=False)

    def analyze(self, filepath):
        self.decide_eye_to_use()
        self.interpolate_coordinates()
        self.identify_blink()
        self.identify_saccade()
        self.identify_fixation()
        self.compute_center_point()
        self.add_state_to_csv(filepath)


# Example usage
if __name__ == "__main__":
    # Assuming the file path for the input CSV is "YYYYMMDDHHMM.csv"
    filepath = "YYYYMMDDHHMM.csv"
    
    eye_movement = EyeMovement(filepath)
    eye_movement.analyze("output.csv")

    print("Analysis completed and results saved to output.csv.")