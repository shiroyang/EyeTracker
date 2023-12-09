"""
Issue 1209:
Since the EM data collected on 1204 is not adequate, I will neglect the 1st visual stimuli.
Therefore, please remove the regarding unnecessary code afterwards.

Step 2.
This code will integrate the eye tracking data and the image stimuli data based on the timestamp.
"""
import os
import pandas as pd
from datetime import datetime

class DataIntegration:
    EM_DATA_DIR = './Data_Collection/Data/Raw/EM/'
    STIMULI_DATA_DIR = './Data_Collection/Data/Raw/Stimuli/'
    TARGET_DIR = './Data_Collection/Data/Sync/'
    FIXATION_CROSS_FRAME = 60
    IMAGE_FRAME = 180 
    GREY_FRAME = 60

    def __init__(self, file_name):
        # Create full file paths
        self.file_name = file_name
        self.em_data_path = os.path.join(DataIntegration.EM_DATA_DIR, file_name)
        self.stimuli_data_path = os.path.join(DataIntegration.STIMULI_DATA_DIR, file_name)
        self.em_data = pd.read_csv(self.em_data_path)
        self.stimuli_data = pd.read_csv(self.stimuli_data_path)
        self.stimuli = []

    def extract_image_timestamp(self):
        # Extract image timestamp from stimuli data
        self.img_timestamp = []
        for idx, row in self.stimuli_data.iterrows():
            if str(row['image_name']).endswith('.jpg'):
                self.img_timestamp.append((row['image_name'], row['timestamp']))
    
    # Find the timestamp that is closest to the stimulus onset, use liear search O(N+M)
    def find_closest_em_timestamp(self):
        # find the closest timestamp in em_data corresponding to the stimulus onset
        idx = 0
        
        # Remove this code afterwards: Start
        self.img_timestamp.pop(0)
        for image_name, timestamp in self.img_timestamp:
            print(image_name, timestamp)
        # Remove this code afterwards: End
        
        for image_name, timestamp in self.img_timestamp:
            target_datetime = datetime.fromisoformat(timestamp).timestamp()
            min_diff = 10**16
            while idx < self.em_data.shape[0] and min_diff > abs(datetime.fromisoformat(self.em_data['timestamp'][idx]).timestamp() - target_datetime):
                min_diff = abs(datetime.fromisoformat(self.em_data['timestamp'][idx]).timestamp() - target_datetime)
                idx += 1
                self.stimuli.append(None)
            
            # Roll back one step to get the closest timestamp
            idx -= 1
            if self.stimuli: self.stimuli.pop()
            # If the closest timestamp is found, append it to the stimuli list, 300 frames in total
            self.stimuli.extend(['Cross']*DataIntegration.FIXATION_CROSS_FRAME)
            self.stimuli.extend([image_name] * DataIntegration.IMAGE_FRAME)
            self.stimuli.extend(['Grey']*DataIntegration.GREY_FRAME)
            idx += DataIntegration.FIXATION_CROSS_FRAME + DataIntegration.IMAGE_FRAME + DataIntegration.GREY_FRAME
            
        # If the stimuli is less than the em_data, append None to the stimuli list
        if len(self.stimuli) < self.em_data.shape[0]:
            self.stimuli.extend([None]*(self.em_data.shape[0] - len(self.stimuli)))
        self.em_data['stimuli'] = self.stimuli
    
    def save_data(self):
        self.em_data.to_csv(os.path.join(DataIntegration.TARGET_DIR, self.file_name) , index=False)
    
    def run(self):
        self.extract_image_timestamp()
        self.find_closest_em_timestamp()
        self.save_data()
        
        
def get_matched_files():
    files_em = os.listdir(DataIntegration.EM_DATA_DIR)
    files_stimuli = os.listdir(DataIntegration.STIMULI_DATA_DIR)
    files_target = os.listdir(DataIntegration.TARGET_DIR)
    # return the files that are in both em_data and stimuli_data but not in target, which means they are not processed yet
    return list(set(files_em) & set(files_stimuli) - set(files_target))


if __name__ == "__main__":
    matched_files = get_matched_files()
    for file in matched_files:
        print(f"Now processing file: {file}\n")
        data_integration = DataIntegration(file)
        data_integration.run()
