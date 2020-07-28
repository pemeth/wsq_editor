# The main window
The main window of the app is an image viewer with menu options. It contains a status bar at the bottom showing the loaded image dimensions and the it's filename.

## The menus
### File
- *Open...*, shortcut *Ctrl+O*
This option opens a native file dialog, through which the user can browse their filesystem. The file dialog gives the option to filter shown files based on their suffixes or to show all files. If the filter is enabled (default), the file dialog shows **png, bmp, jpg, jpeg, wsq, tiff** files. The loaded image is shown in the main window.

- *Export as...*, shortcut *Ctrl+O*
The option to export the currently shown image. The user may enter a valid absolute or relative path with a filename at the end. If the filename ends with a suffix, the application attempts to export the image in the format specified by the suffix. If no suffix is given, the image is exported as a **png**.

### Transformations
- *Zoom in 1.25x*, shortcut *+*
Zooms in with 1.25 magnification. The maximum zoom is twice the size of the input image.

- *Zoom out 0.8x*, shortcut *-*
Zooms in with 0.8 magnification. The minimum zoom is half the size of the input image.

- *Rotate by 90 degrees*, shortcut */*
Rotates the image by 90 degrees counter-clockwise.

- *Mirror the image along the x axis*, shortcut *\**
Mirrors the image along the x axis.

- *Translate the image...*
Opens a textbox, into which the *x* and *y* translation parameters can be input. The format of the input is *x,y*, two values separated by a comma. The values may be positive or negative integers.

### Image
- *Show normalized image*, shortcut *R*
- *Ridge orientation*
  - *Show ridge orientation image*
  - *Show ridge orientation plot*
- *Show region of interest*
- *Show frequency image*
- *Show Butterworth filtered image*
- *Show Gabor filtered image*
- *Show thinned image*

All of these show the output of their respective algorithms. The difference between *Show ridge orientation image* and *Show ridge orientation plot* is that the image version shows the interpreted image of the orientations and the plot version shows a plot of the orientation field in a new window.

### Analysis
- *Show singularities*
- *Minutiae*
  - *Show bifurcation minutiae*
  - *Show ridge ending minutiae*
- *Show class of the fingerprint*
- *Save minutiae info to minutiae.json*

Similarly as in the *Image* menus, these show the respective outputs of the analysis steps. Singularities and minutiae are shown as overlaid markers over the original image in positions where the singularities or minutiae were found. The class of the fingerprint is shown via a popup window. The last option extracts the minutiae and serializes them into JSON format. This is then saved as a file in the current folder as *minutiae.json*.

### Parameters
- *Open the parameter settings*, shortcut *P*

This option opens a new window where the user may modify some of the application parameters.


# Parameter settings window
This window contains sliders with readouts of their currently set values. These sliders may be moved, which sets the values of the parameters specified above the individual sliders. After any slider is moved, the user has to rerun the algorithm on which they would like to see the impact of the individual parameter values. The user may reset the sliders to their original position with the **Reset** button.
