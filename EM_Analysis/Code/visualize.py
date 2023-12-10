import os
import pandas as pd
import cv2
from threading import Thread
from pynput import keyboard
import sys

from OOP_Heatmap import GazeHeatmap
from OOP_Scanpath import GazeScanpath
from OOP_Piechart import GazePiechart

class Visualize:
    def __init__(self) -> None:
        self.INPUT_DIR = './Data_Collection/Data/Processed/'
        self.RESULT_DIR = './EM_Analysis/Result/'
        self.stop_thread = False  # Flag to stop the thread
        self.listener_thread = Thread(target=self.listen_for_esc)
        self.listener_thread.start()

    def listen_for_esc(self):
        def on_press(key):
            if key == keyboard.Key.esc:
                os._exit(0)

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def select_file(self):
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
                file_idx = int(input("\nSelect the file to visualize (enter the number): "))
                if 1 <= file_idx <= len(input_dir):
                    return input_dir[file_idx - 1]
                else:
                    print("\nInvalid selection. Please enter a number from the list.")
            except ValueError:
                print("\nInvalid input. Please enter a valid number.")

    def select_stimulus(self, data):
        stimuli_list = [stimulus for stimulus in data['stimuli'].unique() if str(stimulus).endswith('.jpg')]
        print("\nHere is a list of stimuli that can be visualized:")
        print("#################################")
        for idx, stimulus in enumerate(stimuli_list, 1):
            print("{:<4} {}".format(idx, stimulus))
        print("#################################")
        
        while True:
            try:
                file_idx = int(input("\nSelect the stimulus to visualize (enter the number): "))
                if 1 <= file_idx <= len(stimuli_list):
                    return stimuli_list[file_idx - 1]
                else:
                    print("\nInvalid selection. Please enter a number from the list.")
            except ValueError:
                print("\nInvalid input. Please enter a valid number.")
    
    def select_visualize_method(self):
        print("\nHere is a list of visualization methods:")
        print("#################################")
        print("1. Heatmap")
        print("2. Scanpath")
        print("3. Piechart")
        print("#################################")
        
        while True:
            try:
                method = int(input("\nSelect the visualization method (enter the number): "))
                if method in [1, 2, 3]:
                    return ["heatmap", "scanpath", "piechart"][method - 1]
                else:
                    print("\nInvalid selection. Please enter a number from the list.")
            except ValueError:
                print("\nInvalid input. Please enter a valid number.")
    
    def display_result(self):
        image = cv2.imread(os.path.join(self.RESULT_DIR, self.visualize_method, self.stimulus))
        cv2.imshow('Image', image)
        cv2.waitKey(0)  # Display until any key is pressed
        cv2.destroyAllWindows()
    
    def run_visualization(self):
        self.file_name = self.select_file()
        if self.file_name is None:
            return False
        self.data = pd.read_csv(os.path.join(self.INPUT_DIR, self.file_name))
        self.stimulus = self.select_stimulus(self.data)
        if self.stimulus is None:
            return False
        self.visualize_method = self.select_visualize_method()

        if self.visualize_method == "heatmap":
            heatmap = GazeHeatmap(os.path.join(self.INPUT_DIR, self.file_name), self.stimulus)
            heatmap.run()
        elif self.visualize_method == "scanpath":
            scanpath = GazeScanpath(os.path.join(self.INPUT_DIR, self.file_name), self.stimulus)
            scanpath.run()
        elif self.visualize_method == "piechart":
            piechart = GazePiechart(os.path.join(self.INPUT_DIR, self.file_name), self.stimulus)
            piechart.run()
            # Rendered the image on web browser, so no need to display the image
            return True
        
        self.display_result()
        return True

    def run(self):
        while self.run_visualization():
            pass


if __name__ == '__main__':
    vis = Visualize()
    vis.run()