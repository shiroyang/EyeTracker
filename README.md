# Eye Movement Data Analysis System Design

This document elaborates on the system design for analyzing raw eye movement data using Python, focusing on the `EyeMovement` class.

## Input Data Format

The system processes `.csv` files in the following format:

```
YYYYMMDDHHMM.csv
```

Containing JSON-formatted attributes:

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

## System Configuration

### Monitor Specifications
- Resolution: 1920x1080 pixels
- Size: 609.2mm x 349.4mm

### Distance to Monitor
- 65 cm from the participant

## Data Processing

### Preprocessing
- **Eye Selection:** Choose the eye with more valid data.
- **Data Interpolation:** Linear interpolation for missing data (validity 0), up to a gap of 4 points.
- **Blink Identification:** Detected when 5 or more consecutive frames are missing for both eyes.

### Analysis
- **Saccade Detection:** Calculating movement speed between frames, comparing to a threshold (20 degrees per second).
- **Fixation Identification:** Instances lasting at least 6 consecutive frames are tagged as fixations. The center point of fixations (over 100ms) is calculated.

### Error Handling
- Instances not meeting the criteria for fixation or saccade are classified as error states.

## Visualization Techniques
1. **Heatmap:** Uses a Gaussian matrix for gaze points, color-coded with the jet colormap.
2. **Scanpath:** Shows sequential gaze movement.
3. **Pie Chart:** Displays percentages of fixations, saccades, blinks, and errors.

## System Design Features

- **Threading:** Enables multitasking, such as simultaneous data collection, stimuli display, and user input handling.
- **Modular Classes:** Ensures compatibility with different eye trackers and integration into Psychopy Builder.

## Comparison with Tobii Pro Lab
- Different criteria for fixation identification and visualization techniques.

## Future Work
- Explore alternative methods for saccade and fixation identification (I-DT method).
- Automate extraction of eye movement features.

Visit our [GitHub repository](https://github.com/shiroyang/EyeTracker) for more information and updates.
