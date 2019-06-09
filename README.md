# tilt-shift

Fast Python program to simulate the tilt-shift effect for faking miniatures. [Miniature faking](https://en.wikipedia.org/wiki/Miniature_faking) is the process of blurring parts of an image to simulate a shallow depth of field normally encountered in close-up photography, making the scene seem much smaller than it actually is.

The program handles both images and videos. In video mode, the program prompts the user to choose a focus line for each video in the directory and concatenates all the videos together.

Supported on Python 3 and OpenCV 3+. Tested on macOS.

## Requirements
* OpenCV
* matplotlib
* numpy

Note: proper versions of ffmpeg may need to be installed to support OpenCV video capture code.

## Example Results

See a video demo [here](https://youtu.be/GBbQ9KsgMFk). It was created using timelapse clips from [RIO - 8K](https://vimeo.com/73053894) and [EuroLapse](https://vimeo.com/44941805).

<img src="https://github.com/andrewdcampbell/tilt-shift/blob/master/images/norway.jpg" width="49%"> <img src="https://github.com/andrewdcampbell/tilt-shift/blob/master/out/norway_60.jpg" width="49%">

<img src="https://github.com/andrewdcampbell/tilt-shift/blob/master/images/town.jpg" width="49%"> <img src="https://github.com/andrewdcampbell/tilt-shift/blob/master/out/town_100.jpg" width="49%">

<img src="https://github.com/andrewdcampbell/tilt-shift/blob/master/images/prador.jpg" width="49%"> <img src="https://github.com/andrewdcampbell/tilt-shift/blob/master/out/prador_70.jpg" width="49%">

## Usage
```
python tilt-shift.py (-im IM | -vid VID) [-dof DOF] [-no_enhance]
```

The program works by having the user choose a point in the image to represent the height of a horizontal focus line. `DOF` pixels above and below this line will be in focus (i.e. not blurred), and regions farther away from the focus line will be increasingly blurred. The heuristic is that objects on the same straight line are at the same depth.

* `-im`: The path to the image to be processed.
* `-vid`: The path to the directory of video files.
* `-dof`: The width of the focus region in pixels. Default is 60.
* `-no_enhance`: By default, the brightness and saturation of the input is boosted to increase the illusion of a miniature; if this flag is present, no enhancements are applied.


#### Additional Notes
There are some constants defined in the code that may be modified.
* Input images are resized to have width 1600. To change this, change the value of `RESIZE_WIDTH`, or set `SHOULD_RESIZE` to `False` to disable resizing completely.
* If you click too close to the top or bottom of the image, the code will raise an assertion error that the focus line height is incompatible with the DOF. Either click closer to the center of the image or lower the DOF.
* If concatenating multiple videos, they may have different sizes but must have the same aspect ratio. 
* The video output is set to `1280 x 720` (720p). To change this, just change the size argument to `cv2.VideoWriter`. 
* Only `.mp4` video files are supported. Others may work, but I haven't tested anything.
