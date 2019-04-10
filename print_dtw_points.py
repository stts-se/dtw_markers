# coding: utf-8

from __future__ import print_function
import sys, re
import numpy as np

import librosa

audiofile1 = sys.argv[1]
audiofile2 = sys.argv[2]

#Change: create output file name based on input+samplerate+n_fft+hop_size
#outfile = sys.argv[3]

#n_fft = 4410
#hop_size = 2205
#n_fft = 4800
#hop_size = 300
#n_fft = 4800
#hop_size = 2400
#hop_size = 1200

#With resampled audio: trying to avoid memory error
#This worked for Dvorak_7 10/4 2019
#Lower = Less memory ?
#n_fft = 2205
#Higher = Longer = Fewer = Less memory?
#hop_size = 2205
#resample = True

#Quick test:
#n_fft = 4410
#hop_size = 2205

#Schmidt:
n_fft = 2205
hop_size = 2205
resample = True



m1 = re.match("(.*?/?)([^/.]+).mp3", audiofile1)
dir1 = m1.group(1)
base1 = m1.group(2)

m2 = re.match("(.*?/?)([^/.]+).mp3", audiofile2)
dir2 = m2.group(1)
base2 = m2.group(2)


print("Loading %s" % audiofile1)
#librosa resamples to 22050 by default
if resample:
    x_1, samplerate = librosa.load(audiofile1)
else:
    x_1, samplerate = librosa.load(audiofile1, sr=None)

print("samplerate %d" % samplerate)


print("Loading %s" % audiofile2)
if resample:
    x_2, samplerate = librosa.load(audiofile2)
else:
    x_2, samplerate = librosa.load(audiofile2, sr=None)

print("samplerate %d" % samplerate)



outfile = "%s%s-%s_%s_%s_%s.npy" % (dir1,base1,base2,samplerate,n_fft,hop_size)
print("outfile: %s" % outfile)
out = open(outfile, "wb")




#########################
# -----------------------
# Extract Chroma Features
# -----------------------




print("Extracting chroma features from %s, n_fft: %s, hop_size: %s" % (audiofile1, n_fft, hop_size))
x_1_chroma = librosa.feature.chroma_stft(y=x_1, sr=samplerate, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)

print("Extracting chroma features from %s, n_fft: %s, hop_size: %s" % (audiofile2, n_fft, hop_size))
x_2_chroma = librosa.feature.chroma_stft(y=x_2, sr=samplerate, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)



########################
# ----------------------
# Align Chroma Sequences
# ----------------------

print("Aligning chroma sequences")

D, wp = librosa.core.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')

print("Saving to %s" % outfile)
np.save(out, wp)

print("Done!")
