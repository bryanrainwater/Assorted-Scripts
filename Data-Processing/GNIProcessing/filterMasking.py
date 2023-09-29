#Had to add pillow package using pip for .tiff support
#import skimage #For morphology work
#from skimage import filters, io#, data
#from skimage.color import rgb2gray
#from skimage.filters import threshold_adaptive
#import matplotlib.patches as mpatches
#from skimage import filters
#from scipy import ndimage
#import scipy
#import trackpy as tp
import numpy as np
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
from skimage.feature import canny
from skimage.measure import regionprops
from skimage.morphology import label
from scipy import ndimage as ndi
import csv

img = (mpimg.imread('C:/Users/rainw/Desktop/Australia/GNITest/sli_180116a4.tiff'))

newimg = np.array(img[:,:])
#newimg = rgb2gray(newimg)
dim = newimg.shape

#for i in range(dim[0]):
#	for j in range(dim[1]):
#		if newimg[i,j] > 165: newimg[i,j] = 0
#		else: newimg[i,j] = 255

#edges = filters.sobel(newimg)
#edges = threshold_adaptive(img, 161, offset = 50)
edges = canny(newimg, sigma=1)#, low_threshold = 50, high_threshold=60)
filled_edges = ndi.binary_fill_holes(edges)
for i in range(3): filled_edges = ndi.morphology.binary_erosion(filled_edges).astype(filled_edges.dtype)
for i in range(3): filled_edges = ndi.morphology.binary_dilation(filled_edges).astype(filled_edges.dtype)

label_img = label(filled_edges)
imlog = []
for region in regionprops(label_img):
	minr, minc, maxr, maxc = region.bbox
	imlog.append([minr+(maxr-minr)/2, minc + (maxc-minc)/2,(maxr-minr)/2])
imlog = np.array(imlog)

n, bins, patches = plt.hist(imlog[:,2], 70, normed = 0, facecolor='green',alpha=0.75)
y = mlab.normpdf( bins, 100, 15 )
l = plt.loglog(bins, y, 'r--', linewidth=1)
plt.title('Binned Size Distribution')
plt.xlabel('Pixel Radius')
plt.ylabel('Number of Instances')
#plt.axis([0,50,0.9,150])
#plt.show()

#imlog = tp.locate(newimg, 11, invert=True)

#overlap is between 0 and 1 (0 means any overlap has smaller particle discarded)
#imlog = blob_doh(newimg, min_sigma = 1*np.sqrt(2), max_sigma = 40*np.sqrt(2),  overlap = 0, threshold = 0)#, max_sigma = 30, num_sigma = 10, threshold = 0.1)
#imlog[:,2] = imlog[:,2]*np.sqrt(2)

blobs_list = [imlog]#, imdog, imdoh]
colors = ['blue']#, 'lime', 'red']
titles = ['Laplacian of Gaussian']#, 'Difference of Gaussian', 'Determinant of Hessian']
sequence = zip(blobs_list, colors, titles)

#fig, axes = plt.subplots(1, 1, figsize = (9,3), sharex = True, sharey = True, subplot_kw = {'adjustable': 'box-forced'})
#ax = axes.ravel()
#for idx, (blobs, color, title) in enumerate(sequence):
#	#ax[idx].set_title(title)
#	#ax[idx].imshow(img, interpolation='nearest')
#	for blob in blobs:
#		y, x, r = blob
#		c = plt.Circle((x,y), r, color = color, linewidth = 2, fill = False)
		#ax[idx].add_patch(c)
	#ax[idx].set_axis_off()

fig, ax1 = plt.subplots(1, 1, figsize = (6,6), sharex = True, sharey = True, subplot_kw = {'adjustable': 'box-forced'})
ax1.set_title('Filter Overlay')
ax1.imshow(img, interpolation='nearest')
for blob in imlog:
	y, x, r = blob
	c = plt.Circle((x,y), r, color = 'red', linewidth = 2, fill = False)
	ax1.add_patch(c)
ax1.set_axis_off()
plt.tight_layout()
#plt.show()

with open('C:/Users/rainw/Desktop/Australia/GNITest/output.csv', 'w', newline = '') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter = ',')
	spamwriter.writerow(['Y Pixel', 'X Pixel', 'Radius'])
	spamwriter.writerows(imlog)
