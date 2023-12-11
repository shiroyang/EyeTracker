import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image
import pandas as pd
import cv2
import math
import plotly
from collections import Counter
import plotly.graph_objects as go

class GazePiechart:
    def __init__(self, input_path, image_name):
        self.input_path = input_path
        self.image_name = image_name
        self.image_path = os.path.join('./Data_Collection/Img/Animals/', self.image_name)
        self.output_name = os.path.join('./EM_Analysis/Result/piechart/', self.image_name)
    
    def run(self):
        df = pd.read_csv(self.input_path)
        # Create a condition to filter the DataFrame
        condition = df['stimuli'] == self.image_name
        selected_data = df[condition]
        CNT = Counter(selected_data['eye_state'])
        labels = list(CNT.keys())
        values = list(CNT.values())
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, textinfo='label+percent', insidetextorientation='radial')])
        fig.show()
        fig.write_image(self.output_name)
        
        
if __name__ == '__main__':
    # Usage example:
    heatmap = GazePiechart('./Data_Collection/Data/Processed/202312042245.csv', '807715.jpg')
    heatmap.run()