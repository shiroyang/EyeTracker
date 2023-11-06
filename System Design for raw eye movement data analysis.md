## System Design for raw eye movement data analysis

I want to construct a complete system for analyzing eye movement data using python classes, where calss name = EyeMovement and achieve the following goals.

The input is a csv file with the format of YYYYMMDDHHMM.csv.

There are 

```json
{time, left_gaze_point_on_display_area, left_gaze_point_validity, right_gaze_point_on_display_area, right_gaze_point_validity, left_pupil_diameter, left_pupil_validity, right_pupil_diameter, right_pupil_validity}
```

attributes in this csv file, which are the basic information that can be retrieved from tobii eye tracker.

- Basic Information
  - The monitor I used is 1920*1080 pixels (609.2mm\*349.4mm) 
  - The participant's distance to the monitor is 65 cm

- Time:
  - This eye tracker has 60 Hz sampling frequency, so it has 60 rows of data per second.
- left_gaze_point_on_display_area
  - show the coordinate of the gaze position (x, y), where 0<=x<=1, 0<=y<=1.
- left_gaze_point_validity
  - The value is whether 0 or 1, and if the value is 0, it means the data is missing and if the value is 1, it means the data is valid

**For analysis, we will use the most complete data (less missing data) of left eye or right eye**



Now, our task is to add a new attribute to this csv file that shows the state of the eye.

Here are 4 states that I want to represent.

1. Error State
   - Continuous missing frames < 6,
   - In this case, the validity might be 0 and the coordinate might be missing. So please interpolate the gaze coordinate linearly. 
2. Blink
   - Continuous missing frams of both eyes >= 6
3. Saccade
   - Assume we have $p_i:(x_i, y_i)$ and $p_{i+1}:(x_{i+1}, y_{i+1})$
   - If we do the subtraction, we can calculate v, and if v is greater or equal to 30 degree per second, this gaze point will be regarded as saccade
4. Fixation
   - The gaze data that fits nothing above will be regarded as fixation.
   - Usually fixation lasts longer than 100 ms.
   - We will calculate the center point of the fixation by $\Sigma {X_i/n}$

