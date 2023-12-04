import tobii_research as tr
from datetime import datetime
import pandas as pd
import threading

class EyeTrackerDataCollector:
    def __init__(self):
        self.data_lock = threading.Lock()
        now = datetime.now()
        self.file_path = now.strftime('./Data_Collection/Data/Raw/EM/%Y%m%d%H%M.csv')
        self.my_eyetracker = self.initialize_eye_tracker()

    def initialize_eye_tracker(self):
        found_eyetrackers = tr.find_all_eyetrackers()
        if found_eyetrackers:
            return found_eyetrackers[0]
        else:
            raise Exception("No eye trackers found.")

    def start_collecting(self):
        self.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_callback, as_dictionary=True)

    def gaze_data_callback(self, gaze_data):
        with self.data_lock:
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
            self.append_data_to_file(gaze_dict)
            print(gaze_dict)

    def append_data_to_file(self, data):
        df = pd.DataFrame([data])
        with open(self.file_path, 'a') as file:
            df.to_csv(file, index=False)

        
# Main thread
if __name__ == "__main__":
    collector = EyeTrackerDataCollector()
    thread_eye = threading.Thread(target=collector.start_collecting)
    thread_eye.start()
    thread_eye.join()