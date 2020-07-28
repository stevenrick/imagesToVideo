'''
Reads a folder of images, prepares temp directory, then outputs to video via ffmpeg
author: steven rick
'''

from datetime import datetime
import shutil
import os
from decimal import Decimal
from subprocess import Popen, PIPE
import sys
import csv

ffmpeg_path = "ffmpeg"

chunkLoops = 10
write_format = 'w'

#check version
# if sys.version_info <= (3,0):
#     #py2
#     import Tkinter as tk
#     root = tk.Tk()
#     root.withdraw()
#     import tkFileDialog
#     import tkMessageBox
#     tkMessageBox.showinfo("","Select directory containing images")
#     raw_dir = tkFileDialog.askdirectory()
#     tkMessageBox.showinfo("", "Select directory where you want to save (make sure Free Space > 1/10 of total size of images)")
#     work_dir = tkFileDialog.askdirectory()
#     root.update()
# else:
#     #py3
#     import tkinter as tk
#     root = tk.Tk()
#     root.withdraw()
#     from tkinter import filedialog
#     from tkinter import messagebox
#     messagebox.showinfo("","Select directory containing images")
#     raw_dir = filedialog.askdirectory()
#     raw_dir = raw_dir.replace('/', os.sep)
#     messagebox.showinfo("","Select directory where you want to save (make sure Free Space > 1/10 of total size of images)")
#     work_dir = filedialog.askdirectory()
#     work_dir = work_dir.replace('/', os.sep)
#     root.update()


output_len = 10
frame_rate = 60.0


def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


def batch(parent_dir, temp_dir, batch_vid_dir):
    imgs = list(os.listdir(parent_dir))
    total_size = len(imgs)
    batch_size = int(total_size / chunkLoops)
    groups = chunks(imgs, batch_size)
    for sub in groups:
        # eliminate small groups
        if groups.index(sub) > 0:
            if len(groups[groups.index(sub)]) < batch_size:
                groups[groups.index(sub)-1].extend(groups[groups.index(sub)])
                groups.remove(groups[groups.index(sub)])
    for sub2 in groups:
        if groups.index(sub2) > 0:
            groups[groups.index(sub2)].insert(0, groups[groups.index(sub2) - 1][-1])
    num = 1
    for sub3 in groups:
        batchProgStr = "Batch: " + str(num) + " out of " + str(len(groups))
        print(batchProgStr)
        ext = prep(sub3, parent_dir, temp_dir)
        convert(ext, temp_dir, num, batch_vid_dir)
        clear(temp_dir)
        num += 1
    return
    
def getTimeFromCsv(subBatchPath, session):
    lookupCsv = "{}_colorImages.csv".format(session)
    csvPath = os.path.join(raw_dir,lookupCsv)
    csv_file = csv.reader(open(csvPath, "r"), delimiter=",")
    time_val = ""
    for row in csv_file:
        if subBatchPath == row[1]:
            time_val = row[0]
            # print("time:", time_val)
            break
    return time_val.strip(' \t\r\n')

def prep(sub_batch, par_dir, tem_dir):
    if not os.path.exists(tem_dir):
        os.makedirs(tem_dir)
    
    if ".DS_Store" in sub_batch:
        sub_batch.remove(".DS_Store")
    if "temp" in sub_batch:
        sub_batch.remove("temp")
    if any(".csv" in f for f in sub_batch):
        csv_files = [s for s in sub_batch if ".csv" in s]
        for el in csv_files:
            sub_batch.remove(el)

    space = str(int(Decimal(1.0/frame_rate)*1000000)).zfill(6)
    offset_str = '0-00-00-'+space

    n = 1
    timeArray = getTimeFromCsv(sub_batch[0], session).split(".")
    timeString = timeArray[0]+"."+timeArray[1][:3]
    # print("time:", datetime.strptime(timeString, '%H:%M:%S.%f'))
    zero = datetime.strptime(timeString, '%H:%M:%S.%f')
    previousTime = zero
    offset = datetime.strptime(offset_str, '%H-%M-%S-%f')-datetime.strptime('0-00-00-00', '%H-%M-%S-%f')
    for img in sub_batch[1:]:
        ext = os.path.splitext(img)[1]
        img_path = os.path.join(par_dir, img)
        timeArray = getTimeFromCsv(img, session).split(".")
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


def clear(tem_dir):
    shutil.rmtree(tem_dir)
    return


def combine(batch_dir, out):
    data = []
    temp_file = "temp.txt"
    temp_path = os.path.join(batch_dir, temp_file)
    out_file = os.path.join(out, "video.mp4")
    if not os.path.exists(out):
        os.makedirs(out)
    with open(temp_path, write_format) as temp_txt:
        for el in os.listdir(batch_dir):
            if "temp" not in el:
                data.append("file '"+el+"'"+os.linesep)
        temp_txt.writelines(data)
    video_concat(batch_dir, temp_file, out_file)
    shutil.rmtree(batch_dir)
    return

def findKinectDirectories(search_path):
    directoryList = []

    #return nothing if path is a file
    if os.path.isfile(search_path):
        return []

    #add dir to directorylist if it contains .bmp or .png files
    for f in os.listdir(search_path):
        if (f == "rgb"):
            directoryList.append(os.path.join(search_path, f))

    for d in os.listdir(search_path):
        new_path = os.path.join(search_path, d)
        if os.path.isdir(new_path):
            directoryList += findKinectDirectories(new_path)

    for d in directoryList:
        if "output" in os.listdir(os.path.dirname(d)):
            print("Found output in:", d, "Skipping...")
            directoryList.remove(d)

    return directoryList


if __name__ == '__main__':
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    from tkinter import filedialog
    from tkinter import messagebox
    messagebox.showinfo("","Select where to start search")
    search_start = filedialog.askdirectory()
    search_start = search_start.replace('/', os.sep)    

    rgb_dir_list = findKinectDirectories(search_start)

    print("Found", len(rgb_dir_list), "directories")
    input("Hit any key to process...")

    for d in rgb_dir_list:
        raw_dir = d
        work_dir = os.path.dirname(raw_dir)
        session = work_dir.split(os.sep)[-1]
        print("Processing:", session)
        temp_dir = os.path.join(work_dir,'temp')
        batch_vid_dir = os.path.join(work_dir,'batch_videos')
        out_dir = os.path.join(work_dir,'output')

        print("Splitting")
        batch(raw_dir, temp_dir, batch_vid_dir)
        print("Combining")
        combine(batch_vid_dir, out_dir)
