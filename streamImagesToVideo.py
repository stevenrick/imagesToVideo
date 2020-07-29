'''
Streams a series of images to video via ffmpeg
author: steven rick
'''

from datetime import datetime
import shutil
import os
from decimal import Decimal
import subprocess
import sys
import csv
import tkinter as tk
import re
from PIL import Image


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

ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
frame_rate = 60.0
regex = r"Q\d\d\d-\d\d"


def hms2sec(hms):
    h, m, s = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + Decimal(s)


def createTimeFileDict(f_path):
    timeFileDict = dict()
    with open(f_path, "r") as f:
        csv_file = csv.reader(f, delimiter=",")
        skipOne = True
        for row in csv_file:
            if(skipOne):
                skipOne = False
            else:
                timeFileDict[hms2sec(row[0].strip(' \t\r\n'))] = row[1].strip(' \t\r\n')
    return timeFileDict


def readImgToFfmpeg(img_path, subproc):
    poll = subproc.poll()
    if poll == None:
        img = Image.open(img_path)
        img.save(subproc.stdin, 'JPEG', quality=100, subsampling=0)
        del(img)
    return


def streamToVideo(img_dir, out_dir, session):
    timeFileDict = createTimeFileDict(os.path.join(img_dir, session)+"_colorImages.csv")
    timeArray = sorted(timeFileDict.keys())
    offset = Decimal(1/frame_rate)
    outVideoPath = os.path.join(out_dir,session+"_colorVideo.mp4")
    ffmpeg = '"' + str(ffmpeg_path) + '"'
    input_rate = '"' + str(int(frame_rate)) + '"'
    out = '"' + outVideoPath + '"'
    ffmpeg_cmd = '{0} -f mjpeg -r {1} -i - -c:v libx264 -pix_fmt yuvj444p -r {1} {2}'
    subProc = subprocess.Popen(ffmpeg_cmd.format(ffmpeg, input_rate, out), shell=True, bufsize=0, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    previousTime = timeArray[0]
    previousImgPath = os.path.join(img_dir, timeFileDict[previousTime])
    for currentTime in timeArray[1:]:
        readImgToFfmpeg(previousImgPath, subProc)
        while (currentTime - previousTime) > offset:
            readImgToFfmpeg(previousImgPath, subProc)
            previousTime += offset
        previousTime = currentTime
        previousImgPath = os.path.join(img_dir, timeFileDict[previousTime])
    subProc.stdin.close()
    subProc.wait()
    return


def populateKinectDirectories(search_path):
    directoryList = []
    print("Searching:", search_path)
    for dirpath, dirnames, filenames in os.walk(search_path):
        for dirname in dirnames:
            if dirname.lower() == "rgb":
                directoryList.append(os.path.join(dirpath,dirname))
                continue
    return directoryList


if __name__ == '__main__':
    rgb_dir_list = populateKinectDirectories(search_dir)

    print("Found", len(rgb_dir_list), "directories")
    input("Hit any key to proceed...")

    for d in rgb_dir_list:
        raw_dir = d
        session = re.search(regex, raw_dir).group(0)
        print("Processing:", session)
        out_dir = os.path.join(work_dir,'out')
        if (not os.path.isdir(out_dir)):
            os.mkdir(out_dir)
        streamToVideo(raw_dir, out_dir, session)
