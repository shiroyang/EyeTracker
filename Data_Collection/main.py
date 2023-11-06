import tobii_research as tr
from datetime import datetime
from collections import defaultdict
import pandas as pd
import time

found_eyetrackers = tr.find_all_eyetrackers()
my_eyetracker = found_eyetrackers[0]

now = datetime.now()
file_name = now.strftime('%Y%m%d%H%M.csv')
data = defaultdict(list)

def gaze_data_callback(gaze_data):
    # Print gaze points of left and right eye
    # print("Left eye: ({gaze_left_eye}) \t Right eye: ({gaze_right_eye})".format(
    #     gaze_left_eye=gaze_data['left_gaze_point_on_display_area'],
    #     gaze_right_eye=gaze_data['right_gaze_point_on_display_area']))
    gaze_data["time"] = time.time() - st_time  
    data["time"].append(gaze_data["time"])
    data["left_gaze_point_on_display_area"].append(gaze_data["left_gaze_point_on_display_area"])
    data["left_gaze_point_validity"].append(gaze_data["left_gaze_point_validity"])
    data["right_gaze_point_on_display_area"].append(gaze_data["right_gaze_point_on_display_area"])
    data["right_gaze_point_validity"].append(gaze_data["right_gaze_point_validity"])
    data["left_pupil_diameter"].append(gaze_data["left_pupil_diameter"])
    data["left_pupil_validity"].append(gaze_data["left_pupil_validity"])
    data["right_pupil_diameter"].append(gaze_data["right_pupil_diameter"])
    data["right_pupil_validity"].append(gaze_data["right_pupil_validity"])

    print(gaze_data)


if __name__ == "__main__":
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    time.sleep(1)
    st_time = time.time()
    time.sleep(5)    
    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)