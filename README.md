# Images to Video
## A python script that uses FFMPEG to convert a sequence of dynamically timestamped images into a video
Using a batching approach, it divides up the source images into ~10 equal sized groups and then runs each group through two steps: 1) duplication of image frames to upsample input frame rate 2) converting those image frames into a video. Finally these sub-videos are concatenated together to produce one final video.

### Dependencies
- Python
  
  Written to work with core 2.7 and 3.5

- FFMPEG
  
  On Mac: Recommend installing using Homebrew - http://brew.sh/ - After setting up Homebrew paste the following into Terminal to get all the codec's you'll ever need:
  ```
  brew install ffmpeg --with-vpx --with-vorbis --with-libvorbis --with-vpx --with-vorbis --with-theora --with-libogg --with-libvorbis --with-gpl --with-version3 --with-nonfree --with-postproc --with-libaacplus --with-libass --with-libcelt --with-libfaac --with-libfdk-aac --with-libfreetype --with-libmp3lame --with-libopencore-amrnb --with-libopencore-amrwb --with-libopenjpeg --with-openssl --with-libopus --with-libschroedinger --with-libspeex --with-libtheora --with-libvo-aacenc --with-libvorbis --with-libvpx --with-libx264 --with-libxvid
  ```

  On Windows: Download the appropriate static version of FFMPEG - https://ffmpeg.zeranoe.com/builds/

### Running
Specify frame_rate prior to running. Here are some tips for selecting a value:
  - higher framerate values produce video output that is more accurate to the source frames. This is important for dynamically timestamped images that have higher chance of temporal drift between files' (for most cases I recommend a value that is double that of the average input framerate)
  - framerate determines storage usage (so if the source images take up 100 GB at 10 fps, specifying 20 fps in a naive implementation would temporarily demand 200 GB of space. Because of designing in batching, this script only needs 1/10th of that, so in this example it would temporarily demand an extra 20 GB of space.

Script assumes names of images are their timestamps (time of generation) in HH-MM-SS-ms format. 
