import os
import argparse
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image

class HeatmapGenerator:
    def __init__(self, dispsize, imagefile=None):
        self.dispsize = dispsize
        self.imagefile = imagefile

    def draw_display(self):
        # construct screen (black background)
        screen = np.zeros((self.dispsize[1], self.dispsize[0], 3), dtype='float32')
        # if an image location has been passed, draw the image
        if self.imagefile != None:
            # check if the path to the image exists
            if not os.path.isfile(self.imagefile):
                raise Exception("ERROR in draw_display: imagefile not found at '%s'" % self.imagefile)
            # load image
            img = image.imread(self.imagefile)

            # width and height of the image
            w, h = len(img[0]), len(img)
            # x and y position of the image on the display
            x = self.dispsize[0] / 2 - w / 2
            y = self.dispsize[1] / 2 - h / 2
            # draw the image on the screen
            screen[y:y + h, x:x + w, :] += img
        # dots per inch
        dpi = 100.0
        # determine the figure size in inches
        figsize = (self.dispsize[0] / dpi, self.dispsize[1] / dpi)
        # create a figure
        fig = plt.figure(figsize=figsize, dpi=dpi, frameon=False)
        ax = plt.Axes(fig, [0, 0, 1, 1])
        ax.set_axis_off()
        fig.add_axes(ax)
        # plot display
        ax.axis([0, self.dispsize[0], 0, self.dispsize[1]])
        ax.imshow(screen)  # , origin='upper')

        return fig, ax
    
    @staticmethod
    def gaussian(x, sx, y=None, sy=None):
        # square Gaussian if only x values are passed
        if y == None:
            y = x
        if sy == None:
            sy = sx
        # centers
        xo = x / 2
        yo = y / 2
        # matrix of zeros
        M = np.zeros([y, x], dtype=float)
        # gaussian matrix
        for i in range(x):
            for j in range(y):
                M[j, i] = np.exp(
                    -1.0 * (((float(i) - xo) ** 2 / (2 * sx * sx)) + ((float(j) - yo) ** 2 / (2 * sy * sy))))

        return M        
        
        

    def draw_heatmap(self, gazepoints, alpha=0.5, savefilename=None, gaussianwh=200, gaussiansd=None):

        # IMAGE
        fig, ax = self.draw_display(self.dispsize, imagefile=self.imagefile)

        # HEATMAP
        # Gaussian
        gwh = gaussianwh
        gsdwh = gwh / 6 if (gaussiansd is None) else gaussiansd
        gaus = self.gaussian(gwh, gsdwh)
        # matrix of zeroes
        strt = gwh / 2
        heatmapsize = self.dispsize[1] + 2 * strt, self.dispsize[0] + 2 * strt
        heatmap = np.zeros(heatmapsize, dtype=float)
        # create heatmap
        for i in range(0, len(gazepoints)):
            # get x and y coordinates
            x = strt + gazepoints[i][0] - int(gwh / 2)
            y = strt + gazepoints[i][1] - int(gwh / 2)
            # correct Gaussian size if either coordinate falls outside of
            # display boundaries
            if (not 0 < x < self.dispsize[0]) or (not 0 < y < self.dispsize[1]):
                hadj = [0, gwh]
                vadj = [0, gwh]
                if 0 > x:
                    hadj[0] = abs(x)
                    x = 0
                elif self.dispsize[0] < x:
                    hadj[1] = gwh - int(x - self.dispsize[0])
                if 0 > y:
                    vadj[0] = abs(y)
                    y = 0
                elif self.dispsize[1] < y:
                    vadj[1] = gwh - int(y - self.dispsize[1])
                # add adjusted Gaussian to the current heatmap
                try:
                    heatmap[y:y + vadj[1], x:x + hadj[1]] += gaus[vadj[0]:vadj[1], hadj[0]:hadj[1]] * gazepoints[i][2]
                except:
                    # fixation was probably outside of display
                    pass
            else:
                # add Gaussian to the current heatmap
                heatmap[y:y + gwh, x:x + gwh] += gaus * gazepoints[i][2]
        # resize heatmap
        heatmap = heatmap[strt:self.dispsize[1] + strt, strt:self.dispsize[0] + strt]
        # remove zeros
        lowbound = np.mean(heatmap[heatmap > 0])
        heatmap[heatmap < lowbound] = np.NaN
        # draw heatmap on top of image
        ax.imshow(heatmap, cmap='jet', alpha=alpha)

        # FINISH PLOT
        # invert the y axis, as (0,0) is top left on a display
        ax.invert_yaxis()
        # save the figure if a file name was provided
        if savefilename != None:
            fig.savefig(savefilename)

        return fig


# Parsing
parser = argparse.ArgumentParser(description='Parameters required for processing.')

# Required args
parser.add_argument('input_path', type=str, help='path to the csv input')
parser.add_argument('display_width', type=int, help='an integer representing the display width')
parser.add_argument('display_height', type=int, help='an integer representing the display height')

# Optional args
parser.add_argument('-a', '--alpha', type=float, default=0.5, help='alpha for the gaze overlay')
parser.add_argument('-o', '--output_name', type=str, default='output', help='name for the output file')
parser.add_argument('-b', '--background_image', type=str, default=None, help='path to the background image')

# Advanced optional args
parser.add_argument('-n', '--n_gaussian_matrix', type=int, default=200, help='width and height of gaussian matrix')
parser.add_argument('-sd', '--standard_deviation', type=float, default=None, help='standard deviation of gaussian distribution')

args = parser.parse_args()

# Initialize HeatmapGenerator
heatmap_generator = HeatmapGenerator((args.display_width, args.display_height), args.background_image)

# Load gaze data
with open(args.input_path) as f:
    reader = csv.reader(f)
    raw = list(reader)
    
    if len(raw[0]) == 2:
        gaze_data = [(int(q[0]), int(q[1]), 1) for q in raw]
    else:
        gaze_data = [(int(q[0]), int(q[1]), int(q[2])) for q in raw]
    
# Generate heatmap
heatmap_generator.draw_heatmap(gaze_data, alpha=args.alpha, savefilename=args.output_name, gaussianwh=args.n_gaussian_matrix, gaussiansd=args.standard_deviation)
