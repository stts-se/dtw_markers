# coding: utf-8
from __future__ import print_function

import sys, re

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import librosa
import librosa.display

#For extra prints
debug = False
if "-d" in sys.argv:
    debug = True
    sys.argv.remove("-d")


#For display. Slow and takes a lot of memory! audiofile1 and 2 are only read if display is True
display = False
if "-s" in sys.argv:
    display = True
    sys.argv.remove("-s")


#Input files
dtw_file = sys.argv[1]



marker_file = sys.argv[2]
if len(sys.argv) > 3:
    samplerate = int(sys.argv[3])
else:
    samplerate = 22050.0


m = re.search("(.*?/?)([^/-]+)-([^-]+)-([0-9]+)-([0-9]+)-([0-9]+).npy$", dtw_file)
if m:
    audiodir = m.group(1) 
    audiofile1 = "%s%s.mp3" % (audiodir, m.group(2))
    audiofile2 = "%s%s.mp3" % (audiodir, m.group(3))
    sys.stderr.write("Audiodir: %s, audiofile1: %s, audiofile2: %s\n" % (audiodir, audiofile1, audiofile2))
    samplerate = float(m.group(4))
    n_fft = float(m.group(5))
    hop_size = float(m.group(6))
else:
    n_fft = 4410.0
    hop_size = 2205.0

#HB NOTE    
nr_frames_per_second = 50.0


sys.stderr.write("SETTINGS: samplerate: %s, n_fft: %s, hop_size: %s\n" % (samplerate, n_fft, hop_size))

def readMarkers(filename):
    markers = []
    lines = open(filename).readlines()
    for line in lines:
        line = line.strip()
        (h,m,s,ms) = line.split(":")
        #print(ms)
        
        #last field in marker isn't ms but frame. If fifty frames/s use 0.02
        #marker = int(ms)*100/nr_frames_per_second
        marker = int(ms)/nr_frames_per_second
        #print(marker)
        
        if int(s) > 0:
            marker = marker+int(s)
        if int(m) > 0:
            marker = marker+int(m)*60
        if int(h) > 0:
            marker = marker+int(h)*60*60
        markers.append(marker)

        #print("Line: %s\nMarker: %s" % (line, marker))

            
    return markers


sys.stderr.write("Reading markers from %s\n" % marker_file)
markers = readMarkers(marker_file)
sys.stderr.write("Read %d markers\n" % len(markers))

if debug:
    sys.stderr.write("MARKERS: %s\n" % markers)


marker_nr = len(markers)

########################
# Load dtw-aligned chroma points

sys.stderr.write("Loading dtw points\n")
wp = np.load(open(dtw_file, "rb"))

sys.stderr.write("len(wp): %s\n" % len(wp))


# Settings

# arrows.. explain?

arrows = 30
#Used with display
#arrows = 30
#arrows = hop_size    


#librosa documentation:
#Audio will be automatically resampled to the given rate (default sr=22050).
#To preserve the native sampling rate of the file, use sr=None.


if display:
    sys.stderr.write("Loading audiofiles for display\n")
    #x_1, samplerate = librosa.load(audiofile1, sr=None)
    #x_2, samplerate = librosa.load(audiofile2, sr=None)
    x_1, samplerate = librosa.load(audiofile1)
    x_2, samplerate = librosa.load(audiofile2)

    fig = plt.figure(figsize=(16, 8))

    # Plot x_1
    plt.subplot(2, 1, 1)
    librosa.display.waveplot(x_1, sr=samplerate)
    plt.title(audiofile1)
    ax1 = plt.gca()

    # Plot x_2
    plt.subplot(2, 1, 2)
    librosa.display.waveplot(x_2, sr=samplerate)
    plt.title(audiofile2)
    ax2 = plt.gca()
    
    plt.tight_layout()

    trans_figure = fig.transFigure.inverted()

    
lines = []
#points_idx = np.int16(np.round(np.linspace(0, wp.shape[0] - 1, arrows)))
points_idx = np.int16(np.round(np.linspace(0, wp.shape[0] - 1, hop_size)))



def tp2str(s):
    #tp is seconds
    h = 0
    m = 0
    if s > 60:
        m = s/60
        s = s%60
    if m > 60:
        h = m/60
        m = m%60
    #ms = int(s%1*100)
    ms = round(s%1*nr_frames_per_second)

    #print("s: %.2f\tms: %d" % (s,ms)) 

    s = int(s)
    return "%02d:%02d:%02d:%02d" % (h,m,s,ms)

def interpolateTimepoint(marker, prev_tp1, prev_tp2, tp1, tp2):
    #distance prev_tp1-tp1  = d1
    #distance prev_tp2-tp2 = d2
    #distance marker-prev_tp1 as percent of d1 = t
    #prev_tp2 - d2*t = interp
    d1 = prev_tp1-tp1
    d2 = prev_tp2-tp2
    d3 = prev_tp1-marker
    t = d3/d1
    interp = prev_tp2 - d2*t
    return interp
    
markers.reverse()
mark_index = 0
prev_tp1 = None
prev_tp2 = None
latest_used_tp1 = None
latest_used_tp2 = None
markers1_list = []
markers2_list = []

sys.stderr.write("Finding markers\n")

# for tp1, tp2 in zip((wp[points_idx, 0]) * hop_size, (wp[points_idx, 1]) * hop_size):


timepoints = wp[points_idx] * hop_size / samplerate
timepoints = wp[points_idx] * 0.1



for tp1, tp2 in wp[points_idx] * hop_size / samplerate:
    #for tp1, tp2 in wp[points_idx] * float(hop_size) / samplerate:


    if prev_tp1 and tp1 > prev_tp1:
        sys.stderr.write("ERROR: prev_tp1 = %s, tp1 = %s\n" % (prev_tp1, tp1))
        sys.stderr.write("Probably because the first audio is longer than the second?\n")
        #sys.exit()

    
    if display:
        # get position on axis for a given index-pair
        coord1 = trans_figure.transform(ax1.transData.transform([tp1, 0]))
        coord2 = trans_figure.transform(ax2.transData.transform([tp2, 0]))

        # draw a line
        redline = matplotlib.lines.Line2D((coord1[0], coord2[0]),
                                   (coord1[1], coord2[1]),
                                   transform=fig.transFigure,
                                   color='r')
        if debug:
            sys.stderr.write("REDLINE: tp1: %f, tp2: %f\n" % (tp1,tp2))
        #add all lines
        #lines.append(redline)


    try:
        marker = markers[mark_index]
    except:
        #marker = None
        break

    if debug:
        sys.stderr.write("Looking for marker %s: prev_tp1: %s, tp1: %s\n" % (marker, prev_tp1, tp1))

    
    if prev_tp1 and latest_used_tp1 and marker > prev_tp1:
        prev_tp1 = latest_used_tp1
        prev_tp2 = latest_used_tp2


    if (marker and prev_tp1 and marker < prev_tp1 and marker >= tp1) or (prev_tp1 == None and marker >= tp1):
        #hb special case.. can't interpolate if at end of file
        if prev_tp1 == None:
            interp = marker
        else:
            interp = interpolateTimepoint(marker, prev_tp1, prev_tp2, tp1, tp2)

        if debug:
            sys.stderr.write("prev_tp1: %s, tp1: %.2f, marker: %.2f, interp: %s\n" % (prev_tp1,tp1,marker,interp))
            

        markers1_list.append(marker)
        markers2_list.append(interp)
        

        sys.stderr.write("%s: %f -> %f\n" % (marker_nr, marker,interp))
        
        mark_index +=1
        marker_nr -= 1
        
        if display:
            #Only add red lines for markers!
            lines.append(redline)

            # get position on axis for a given index-pair
            coord1 = trans_figure.transform(ax1.transData.transform([marker, 0]))
            coord2 = trans_figure.transform(ax2.transData.transform([interp, 0]))

            # draw a line
            greenline = matplotlib.lines.Line2D((coord1[0], coord2[0]),
                                   (coord1[1], coord2[1]),
                                   transform=fig.transFigure,
                                   color='g')
            lines.append(greenline)
        latest_used_tp1 = prev_tp1
        latest_used_tp2 = prev_tp2

    prev_tp1 = tp1
    prev_tp2 = tp2
    
#In case there was an error, just copy remaining markers
while mark_index < len(markers):
    marker = markers[mark_index]
    sys.stderr.write("Copying marker: %s\n" % marker)
    interp = marker
    markers1_list.append(marker)
    markers2_list.append(interp)        
    sys.stderr.write("%s: %f -> %f\n" % (marker_nr, marker,interp))
    mark_index += 1
    marker_nr -= 1

    
if display:
    sys.stderr.write("displaying..\n")
    
    fig.lines = lines
    plt.tight_layout()

    plt.show()





markers.reverse()
markers1_list.reverse()
markers2_list.reverse()


i = 0
while i < len(markers1_list):
    #marker = markers1_list[i]
    marker = markers[i]
    interp = markers2_list[i]    
    #Print numbered list with both file markers
    #print("%d\t%s\t%s" % (i+1, tp2str(marker) ,tp2str(interp)))

    #Only print new markers
    print(tp2str(interp))

    i += 1
    


