# Images to Video
## A python script that uses FFMPEG to convert a sequence of dynamically timestamped images into a video
Using a batching approach, it divides up the source images into ~10 equal sized groups and then runs each group through two steps: 1) duplication of image frames to upsample input frame rate 2) converting those image frames into a sub-video. Finally these sub-videos are concatenated together to produce one final video.

Tested on OSX and Windows

### Dependencies
- Python
  
  Written to work with core 2.7 and 3.5

- FFMPEG
  
  Recommend installing FFMPEG using Homebrew - http://brew.sh/ - After setting up Homebrew paste the following into Terminal to get all the codec's you'll ever need (this uses grep to include every --with- flag available):
  ```
  brew install ffmpeg $(brew options ffmpeg | grep -vE '\s' | grep -- '--with-' | tr '\n' ' ')
  ```

### Running
Specify frame_rate prior to running. Here are some tips for selecting a value:
  - A higher frame_rate value produce video output that is more accurate to the source frames. This is important for dynamically timestamped images that have higher chance of temporal drift between files. For most cases I recommend a value that is double that of the average expected input framerate.
  - The frame_rate value determines how much storage usage will be required. If the source images take up 100 GB at 10 fps, specifying 20 fps in a naive implementation would temporarily demand 200 GB of space due to doubling of the framerate. By incorporating batching, processing only requires 1/10th of this overhead. In the prior example, processing would temporarily require 20 GB of free space.

Script assumes names of images are their timestamps (time of generation) in HH-MM-SS-ms format, and can be modified according to http://strftime.org/
