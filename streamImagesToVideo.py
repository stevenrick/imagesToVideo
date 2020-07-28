'''
Streams a series of images to video via ffmpeg
author: steven rick
'''

from datetime import datetime
import shutil
import os
from decimal import Decimal
from subprocess import Popen, PIPE
import sys
import csv
import tkinter as tk


root = tk.Tk()
root.withdraw()
from tkinter import filedialog
from tkinter import messagebox


messagebox.showinfo("","Select directory to start search")
search_dir = filedialog.askdirectory()
search_dir = search_dir.replace('/', os.sep)
messagebox.showinfo("","Select directory where you want to stream output")
work_dir = filedialog.askdirectory()
work_dir = work_dir.replace('/', os.sep)
messagebox.showinfo("","Select ffmpeg directory")
ffmpeg_dir = filedialog.askdirectory()
ffmpeg_dir = ffmpeg_dir.replace('/', os.sep)
root.update()

ffmpeg_path = "ffmpeg.exe"
write_format = 'w'
frame_rate = 60.0


def createTimeFileDict(f_path):
    with open(f_path, "r") as f:
        csv_file = csv.reader(f, delimiter=",")
    timeFileDict = dict()
    skipOne = True
    for row in csv_file:
        if(skipOne):
            next(row)
            skipOne = False
        else:
            timeFileDict[row[0].strip(' \t\r\n')] = row[1].strip(' \t\r\n')
    return timeFileDict


def stream(csv_file):
    space = str(int(Decimal(1.0/frame_rate)*1000000)).zfill(6)
    offset_str = '0-00-00-'+space

    n = 1
    timeFileDict = createTimeFileDict(csv_file)
    timeArray = sorted(map(int, timeFileDict.keys()))
    for el in timeArray:
        print(timeFileDict[el])
    timeBatchStartString = timeBatchStart[0]+"."+timeBatchStart[1][:3]
    # print("time:", datetime.strptime(timeString, '%H:%M:%S.%f'))
    zero = datetime.strptime(timeBatchStartString, '%H:%M:%S.%f')
    previousTime = zero
    offset = datetime.strptime(offset_str, '%H-%M-%S-%f')-datetime.strptime('0-00-00-00', '%H-%M-%S-%f')
    for img in sub_batch[1:]:
        ext = os.path.splitext(img)[1]
        img_path = os.path.join(par_dir, img)
        # timeArray = getTimeFromCsv(img, session).split(".")
        timeString = timeArray[0]+"."+timeArray[1][:3]
        time = datetime.strptime(timeString, '%H:%M:%S.%f')
        while (previousTime-zero) < (time-zero):
            out_name = str(n).zfill(output_len)+ext
            out_path = os.path.join(tem_dir, out_name)
            shutil.copy(img_path, out_path)
            n += 1
            previousTime += offset
    return ext


def convert(ext, temp, num, out):
    if not os.path.exists(out):
        os.makedirs(out)
    vid_num = str(num).zfill(output_len) + ".mp4"
    ffmpeg_cmd = '{5} -framerate {0} -i {1}/%10d{4} -c:v libx264 -pix_fmt yuv420p {2}/{3}'
    temp = '"' + temp + '"'
    out = '"' + out + '"'
    input_rate = '"' + str(int(frame_rate)) + '"'
    p = Popen(ffmpeg_cmd.format(input_rate, temp, out, vid_num, ext, ffmpeg_path), stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate(input=None)
    return stdout, stderr


def video_concat(batch_dir, txt_file, out_video):
    ffmpeg_cmd = '{2} -f concat -i {0} -c copy {1}'
    txt_file = '"' + txt_file + '"'
    out_video = '"' + out_video + '"'
    p = Popen(ffmpeg_cmd.format(txt_file, out_video, ffmpeg_path), cwd=batch_dir, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate(input=None)
    #print(stdout)
    #print(stderr)
    return stdout, stderr


def populateKinectDirectories(search_path):
    directoryList = []
    print("Searching:", search_path)
    for dirpath, dirnames, filenames in os.walk(search_path):
        for dirname in dirnames:
            if dirname.lower() == "rgb":
                directoryList.append(os.path.join(dirpath,dirname))
    return directoryList


if __name__ == '__main__':
    rgb_dir_list = populateKinectDirectories(search_dir)

    print("Found", len(rgb_dir_list), "directories")
    input("Hit any key to process...")

    for d in rgb_dir_list:
        raw_dir = d
        session = "Q"+raw_dir.split("Q")[1].split(os.sep)[0]
        print("Processing:", session)
        temp_dir = os.path.join(work_dir,'temp')
        batch_vid_dir = os.path.join(work_dir,'batch_videos')
        out_dir = os.path.join(work_dir,'output')

        print("Splitting")
        batch(raw_dir, temp_dir, batch_vid_dir)
        print("Combining")
        combine(batch_vid_dir, out_dir)
