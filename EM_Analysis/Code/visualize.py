"""
Step4.

Visualize the fixation points and saccades on the screen.
The data will be read from the Data_Collection/Data/Processed folder.

Logic:
1. Let user select the file 
2. Let user select the stimuli
3. Let user select the way to visualize the data

Heatmap class is referenced from
https://github.com/TobiasRoeddiger/GazePointHeatMap/tree/master
"""

import os
import pandas as pd
from OOP_HeatMap import GazeHeatmap
import cv2

# def get_matched_files():
#     files_em = os.listdir(DataIntegration.EM_DATA_DIR)
#     files_stimuli = os.listdir(DataIntegration.STIMULI_DATA_DIR)
#     files_target = os.listdir(DataIntegration.TARGET_DIR)
#     # return the files that are in both em_data and stimuli_data but not in target, which means they are not processed yet
#     return list(set(files_em) & set(files_stimuli) - set(files_target))

class Visualize:
    def __init__(self) -> None:
        self.INPUT_DIR = './Data_Collection/Data/Processed/'
        self.RESULT_DIR = './EM_Analysis/Result/'
        self.file_name = self.select_file()
        self.data = pd.read_csv(os.path.join(self.INPUT_DIR, self.file_name))
        self.stimulus = self.select_stimulus()
        self.visualize_method = self.select_visualize_method()
    
    def select_file(self):
        try:
            input_dir = os.listdir(self.INPUT_DIR)
            if not input_dir:
                print("No files available for visualization.")
                return None

            print("\nHere is a list of files that can be visualized:")
            print("#################################")
            for idx, file in enumerate(input_dir, 1):
                print("{:<4} {}".format(idx, file))
            print("#################################")
            
            while True:
                try:
                    file_idx = int(input("\nPlease select the file to visualize (enter the number): ")) - 1
                    if 0 <= file_idx < len(input_dir):
                        file_name = input_dir[file_idx]
                        confirm = input(f"You have selected '{file_name}'. Do you want to proceed? (yes/no): ").lower()
                        if confirm == 'yes' or confirm == 'y' or confirm == '1':
                            print(f"\nYou have confirmed the selection: '{file_name}'")
                            return file_name
                        else:
                            print("\nPlease reselect the file.")
                    else:
                        print("\nInvalid selection. Please enter a number from the list.")
                except ValueError:
                    print("\nInvalid input. Please enter a valid number.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def select_stimulus(self):
        stimuli_list = [stimulus for stimulus in self.data['stimuli'].unique() if str(stimulus).endswith('.jpg')]
        print("\nHere is a list of stimuli that can be visualized:")
        print("#################################")
        for idx, file in enumerate(stimuli_list, 1):
            print("{:<4} {}".format(idx, file))
        print("#################################")
        
        while True:
            try:
                file_idx = int(input("\nPlease select the file to visualize (enter the number): ")) - 1
                if 0 <= file_idx < len(stimuli_list):
                    stimulus_name = stimuli_list[file_idx]
                    confirm = input(f"You have selected '{stimulus_name}'. Do you want to proceed? (yes/no): ").lower()
                    if confirm == 'yes' or confirm == 'y' or confirm == '1':
                        print(f"\nYou have confirmed the selection: '{stimulus_name}'")
                        return stimulus_name
                    else:
                        print("\nPlease reselect the file.")
                else:
                    print("\nInvalid selection. Please enter a number from the list.")
            except ValueError:
                print("\nInvalid input. Please enter a valid number.")
    
    def select_visualize_method(self):
        print("\nHere is a list of visualization methods:")
        print("#################################")
        print("1. Heatmap")
        print("2. Fixation points")
        print("3. Saccades")
        print("#################################")
        
        while True:
            try:
                method = int(input("\nPlease select the visualization method (enter the number): "))
                if method == 1:
                    return "heatmap"
                elif method == 2:
                    return "fixation"
                elif method == 3:
                    return "saccade"
                else:
                    print("\nInvalid selection. Please enter a number from the list.")
            except ValueError:
                print("\nInvalid input. Please enter a valid number.")
    
    def display_result(self):
        image = cv2.imread(os.path.join(self.RESULT_DIR, self.visualize_method, self.stimulus))
        cv2.imshow('Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def run(self):
        if self.visualize_method == "heatmap":
            heatmap = GazeHeatmap(os.path.join(self.INPUT_DIR, self.file_name), self.stimulus)
            heatmap.run()
        elif self.visualize_method == "fixation":
            pass
        elif self.visualize_method == "saccade":
            pass
        
        self.display_result()


if __name__ == '__main__':
    vis = Visualize()
    vis.run()