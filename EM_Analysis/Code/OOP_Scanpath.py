import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image
import pandas as pd
import cv2

class GazeScanpath:
    def __init__(self, input_path, image_name=None, display_width=1920, display_height=1080, alpha=0.6, n_gaussian_matrix=500, standard_deviation=33):
        self.input_path = input_path
        self.image_name = image_name
        self.image_path = os.path.join('./Data_Collection/Img/Animals/', self.image_name)
        self.display_width = display_width
        self.display_height = display_height
        self.alpha = alpha
        self.output_name = os.path.join('./EM_Analysis/Result/heatmap/', self.image_name)
        self.n_gaussian_matrix = n_gaussian_matrix
        self.standard_deviation = standard_deviation
        self.resize_image(self.image_path, self.display_width, self.display_height)
        self.gaze_data = None
        self.max_duration = None

    def resize_image(self, image_path, width, height):
        image = cv2.imread(image_path)
        if image is None:
            print("Failed to load image. Please check the image path.")
            return
        # Check if image is already 1920x1080
        if image.shape[1] == self.display_width and image.shape[0] == self.display_height:
            pass
        else:
            # Resize the image
            resized_image = cv2.resize(image, (self.display_width, self.display_height))
            cv2.imwrite(image_path, resized_image)
            print("Image resized to 1920x1080 and saved with correct color.")
            
    def draw_display(self):
        screen = np.zeros((self.display_height, self.display_width, 3), dtype='float32')
        if self.image_path is not None:
            if not os.path.isfile(self.image_path):
                raise Exception(f"ERROR in draw_display: imagefile not found at '{self.image_path}'")
            # Load image with matplotlib's image module
            img = image.imread(self.image_path)
            # Ensure the image is in the correct format
            if img.dtype == np.float32:
                # Normalize if the image is in float format (common for .png)
                img = np.clip(img, 0, 1)
            elif img.dtype == np.uint8:
                # Convert to float and normalize if the image is in byte format (common for .jpg)
                img = img.astype('float32') / 255

            # width and height of the image
            w, h = img.shape[1], img.shape[0]
            # x and y position of the image on the display
            x = self.display_width // 2 - w // 2
            y = self.display_height // 2 - h // 2
            # draw the image on the screen
            screen[y:y + h, x:x + w, :] += img[:,:,:3]  # Use only RGB channels
        dpi = 100.0
        figsize = (self.display_width / dpi, self.display_height / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
        ax = plt.Axes(fig, [0, 0, 1, 1])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.axis([0, self.display_width, 0, self.display_height])
        ax.imshow(screen)
        return fig, ax            
            
    def draw_scanpath(self):
        fig, ax = self.draw_display()
        
        # Iterate over gaze data to plot scanpath
        for i in range(len(self.gaze_data)):
            # Extract current and next fixation point
            x, y, duration = self.gaze_data[i]
            color_intensity = min(duration / self.max_duration, 1)  # Normalizing duration
            circle = plt.Circle((x, y), 10, color=(1, 0, 0, color_intensity))
            ax.add_patch(circle)
            ax.text(x, y, str(i+1), color='white', ha='center', va='center')

            if i < len(self.gaze_data) - 1:
                next_x, next_y, _ = self.gaze_data[i+1]
                ax.arrow(x, y, next_x - x, next_y - y, head_width=20, head_length=30, fc='black', ec='black')
        
        plt.show()
        

    
    def to_pixel(self, coord):
        coord = eval(coord)
        if len(coord)!= 2 or coord[0] == None or coord[1] == None: return (None, None)
        return (coord[0] * self.display_width, coord[1] * self.display_height)
    
    def run(self):
        df = pd.read_csv(self.input_path)
        condition = df['stimuli'] == self.image_name
        selected_data = df[condition]
        fixation_center_list = selected_data['fixation_center'].apply(self.to_pixel).tolist()
        filtered_fixation_center_list = [coord for coord in fixation_center_list if coord != (None, None)]
        clean_fixation_center_list = []
        idx = 0
        while idx < len(filtered_fixation_center_list)-1:
            if filtered_fixation_center_list[idx] == filtered_fixation_center_list[idx+1]:
                start_idx = idx
                while idx < len(filtered_fixation_center_list)-1 and filtered_fixation_center_list[idx] == filtered_fixation_center_list[idx+1]:
                    idx += 1
                end_idx = idx
                clean_fixation_center_list.append((*filtered_fixation_center_list[start_idx], end_idx - start_idx + 1))
            else:
                clean_fixation_center_list.append((*filtered_fixation_center_list[idx], 1))
            idx += 1
        self.gaze_data = clean_fixation_center_list
        self.max_duration = max(self.gaze_data, key=lambda x:x[-1])[-1]
        print(clean_fixation_center_list)
        self.draw_scanpath()


if __name__ == '__main__':
    # Usage example:
    heatmap = GazeScanpath('./Data_Collection/Data/Processed/202312042245.csv', '807715.jpg')
    heatmap.run()