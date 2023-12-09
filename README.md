# Eye Movement Data Analysis System Design

This document outlines the system design for analyzing raw eye movement data. The system will be implemented using Python with the class name `EyeMovement`. Below are the specifications for the system, detailing the input data format, hardware configuration, and the analytic approach to categorize eye movement.

## Input Data

The input for the system is a `.csv` file named in the format `YYYYMMDDHHMM.csv`. The `.csv` file consists of the following attributes in JSON format:

```json
{
  "time": "timestamp",
  "left_gaze_point_on_display_area": "(x, y)",
  "left_gaze_point_validity": "0 or 1",
  "right_gaze_point_on_display_area": "(x, y)",
  "right_gaze_point_validity": "0 or 1",
  "left_pupil_diameter": "value",
  "left_pupil_validity": "0 or 1",
  "right_pupil_diameter": "value",
  "right_pupil_validity": "0 or 1"
}
```

These attributes represent the basic information collected from a Tobii eye tracker.

## System Configuration

- **Monitor Specifications:** 1920x1080 pixels (609.2mm x 349.4mm)
- **Distance to Monitor:** The participant is positioned 65 cm away from the monitor.

## Data Attributes

- **Time:** The eye tracker operates at a sampling frequency of 60 Hz, resulting in 60 rows of data per second.
- **Left Gaze Point on Display Area:** Provides the (x, y) coordinates of the gaze position where 0 <= x <= 1 and 0 <= y <= 1.
- **Left Gaze Point Validity:** Indicates the validity of the data point with 0 (missing data) or 1 (valid data).

## Analysis Goal

The analysis focuses on using the most complete dataset (with the least missing data) between the left and right eyes.

## Task

Our objective is to augment the `.csv` file with an additional attribute representing the state of the eye, categorized into the following four states:

1. **Error State:**
   - Identified when continuous missing frames are fewer than 6.
   - Missing data is indicated by validity being 0 and missing coordinates.
   - Interpolate the gaze coordinates linearly in this scenario.

2. **Blink:**
   - Determined by 6 or more continuous missing frames for both eyes.

3. **Saccade:**
   - Given points \( p_i:(x_i, y_i) \) and \( p_{i+1}:(x_{i+1}, y_{i+1}) \).
   - Compute the velocity \( v \) by subtracting these points.
   - A velocity \( v \) greater than or equal to 30 degrees per second indicates a saccade.

4. **Fixation:**
   - Applies to gaze data that does not fit the criteria above.
   - Fixation typically lasts longer than 100 ms.
   - Calculate the center point of fixation by averaging the X coordinates \( \Sigma X_i/n \).

---

## Next Steps

1. **11.08 Prof. Nakashima**
   - Fixation Centerが一部の状況で表示されないエラー処理 (fixed)
   - Data_Collectionをmulti-threadに変更、3 threads. OOP_image_stumili.py records the stimulus number and the timestamp of the fixation cross. File2 records the EM data.
      - thread 1: input from eye tracker
      - thread 2: input from keyboard
      - thread 3: show stimuli (1 sec fixaiton + 3 sec stimulus + 1 sec grey background)
   - `preprocess.py`
      - Find the timestamp that is closest to the stimulus onset, use linear search O(N+M)
      - extract 5 secs of data (1 sec fixation + 3 sec stimulus + 1 sec grey background), which is 300 rows of data from the timestamp
      - do the basic process as `main.py`
      - remove the first 60 rows and the last 60 rows
         - fix the timestamp to start from 0
         - add column stimulus number
         - add correct/incorrect column
   - `vizualize.py`
      - given the stimulus number, extract the corresponding EM data from preprocessed data.
      - plot the data with different colors for each state
      - plot the fixation points in two methods
         - plot the fixation points as a heatmap
         - plot the convex hull of the fixation points