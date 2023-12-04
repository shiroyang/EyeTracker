import tobii_research as tr
from datetime import datetime
import pandas as pd
import threading


# Global variables
data_lock = threading.Lock()
now = datetime.now()
file_em = now.strftime('./Data_Collection/Data/Raw/EM/%Y%m%d%H%M.csv')

def eye_tracker_input():
    global file_name
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
            df.to_csv(file_em, mode='a', index=False)

    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
        
# Main thread
if __name__ == "__main__":

    thread_eye = threading.Thread(target=eye_tracker_input)
    thread_eye.start()
    
    thread_eye.join()

