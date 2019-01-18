# coding: utf-8

from __future__ import print_function
import sys
import numpy as np

import librosa

audiofile1 = sys.argv[1]
audiofile2 = sys.argv[2]


out = open(sys.argv[3], "w")

print("Loading %s" % audiofile1)
#x_1, samplerate = librosa.load(audiofile1, sr=None)
x_1, samplerate = librosa.load(audiofile1)
print("samplerate %d" % samplerate)


print("Loading %s" % audiofile2)
#x_2, samplerate = librosa.load(audiofile2, sr=None)
x_2, samplerate = librosa.load(audiofile2)
print("samplerate %d" % samplerate)



#########################
# -----------------------
# Extract Chroma Features
# -----------------------
#n_fft = 4410
#hop_size = 2205
#n_fft = 4800
#hop_size = 300
n_fft = 4800
#hop_size = 2400
hop_size = 1200

x_1_chroma = librosa.feature.chroma_stft(y=x_1, sr=samplerate, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)
x_2_chroma = librosa.feature.chroma_stft(y=x_2, sr=samplerate, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)



########################
# ----------------------
# Align Chroma Sequences
# ----------------------

D, wp = librosa.core.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')

np.save(out, wp)
