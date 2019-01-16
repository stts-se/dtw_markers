# coding: utf-8

from __future__ import print_function
import sys
import numpy as np

import librosa

audiofile1 = sys.argv[1]
audiofile2 = sys.argv[2]


out = open(sys.argv[3], "w")


#HB x_1, fs = librosa.load('audio/sir_duke_slow.mp3')
#audiofile1 = 'audio/Master audio.wav'
#audiofile1 = 'audio/Master 1. Figaros Brollop.mp3'
#audiofile1 = 'audio/Dvorak 7 Master.mp3'
#audiofile1 = 'audio/Dvorak 7 Master part1.mp3'
x_1, fs = librosa.load(audiofile1)

#x_2, fs = librosa.load('audio/sir_duke_fast.mp3')
#audiofile2 = 'audio/Audio - Take 1.wav'
#audiofile2 = 'audio/GP 1. Figaros Brollop DELETED MARKERS.mp3'
#audiofile2 = 'audio/Dvorak 7 K1 no markers.mp3'
#audiofile2 = 'audio/Dvorak 7 K1 no markers part1.mp3'
x_2, fs = librosa.load(audiofile2)

#########################
# -----------------------
# Extract Chroma Features
# -----------------------
#n_fft = 4410
#hop_size = 2205
#n_fft = 4800
#hop_size = 300
n_fft = 4800
hop_size = 2400
#hop_size = 1200

x_1_chroma = librosa.feature.chroma_stft(y=x_1, sr=fs, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)
x_2_chroma = librosa.feature.chroma_stft(y=x_2, sr=fs, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)



########################
# ----------------------
# Align Chroma Sequences
# ----------------------

D, wp = librosa.core.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')

#Doesn't work..
#from fastdtw import fastdtw
#D, wp = fastdtw(x_1_chroma, x_2_chroma, dist='cosine')




#wp.tofile(out, sep=" ")
np.save(out, wp)
