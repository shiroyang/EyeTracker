import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image

class GazeHeatmap:
    def __init__(self, input_path, background_image=None, display_width=1920, display_height=1080, alpha=0.5, output_name='output', n_gaussian_matrix=200, standard_deviation=33):
        self.input_path = input_path
        self.background_image = background_image
        self.display_width = display_width
        self.display_height = display_height
        self.alpha = alpha
        self.output_name = output_name
        self.n_gaussian_matrix = n_gaussian_matrix
        self.standard_deviation = standard_deviation

    def draw_display(self):
        screen = np.zeros((self.display_height, self.display_width, 3), dtype='float32')
        if self.background_image is not None:
            if not os.path.isfile(self.background_image):
                raise Exception(f"ERROR in draw_display: imagefile not found at '{self.background_image}'")
            # Load image with matplotlib's image module
            img = image.imread(self.background_image)
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


    def gaussian(self, x, sx, y=None, sy=None):
        if y is None:
            y = x
        if sy is None:
            sy = sx
        xo = x // 2
        yo = y // 2
        M = np.zeros([y, x], dtype=float)
        for i in range(x):
            for j in range(y):
                M[j, i] = np.exp(-1.0 * (((float(i) - xo) ** 2 / (2 * sx ** 2)) + ((float(j) - yo) ** 2 / (2 * sy ** 2))))
        return M

    def draw_heatmap(self):
        fig, ax = self.draw_display()
        gwh = self.n_gaussian_matrix
        gsdwh = gwh // 6 if (self.standard_deviation is None) else self.standard_deviation
        gaus = self.gaussian(gwh, gsdwh)
        strt = gwh // 2
        heatmapsize = self.display_height + 2 * strt, self.display_width + 2 * strt
        heatmap = np.zeros(heatmapsize, dtype=float)
        for i in range(len(self.gaze_data)):
            x = strt + self.gaze_data[i][0] - gwh // 2
            y = strt + self.gaze_data[i][1] - gwh // 2
            if 0 > x or x > self.display_width or 0 > y or y > self.display_height:
                continue
            heatmap[y:y + gwh, x:x + gwh] += gaus * self.gaze_data[i][2]
        heatmap = heatmap[strt:self.display_height + strt, strt:self.display_width + strt]
        lowbound = np.mean(heatmap[heatmap > 0])
        heatmap[heatmap < lowbound] = np.NaN
        ax.imshow(heatmap, cmap='jet', alpha=self.alpha)
        ax.invert_yaxis()
        if self.output_name is not None:
            fig.savefig(self.output_name)
        return fig

    def process_data(self):
        with open(self.input_path) as f:
            reader = csv.reader(f)
            raw = list(reader)
            if len(raw[0]) == 2:
                self.gaze_data = [(int(q[0]), int(q[1]), 1) for q in raw]
            else:
                self.gaze_data = [(int(q[0]), int(q[1]), int(q[2])) for q in raw]
            self.draw_heatmap()

# Usage example:
heatmap = GazeHeatmap('data.csv', 'test.jpg')
heatmap.process_data()