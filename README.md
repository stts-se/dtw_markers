1)
Extract chroma features, compute dtw points and write to file

script:
print_dtw_points.py

settings:
n_fft
hop_size
more?

arguments:
1: input audio file
2: input audio file

example:
python print_dtw_points.py data/Dvorak_7_Master.mp3 data/Dvorak_7_K1.mp3 

output in name generated from input files, samplerate, n_fft, hop_size


2)
Load dtw points and markers, print new markers

script:
find_markers_in_dtw.py

settings:
n_fft
hop_size
more?

input:
1: input filename for dtw points (.npy)
2: input filename for markers (.txt)

output:
stderr new markers

example:
python find_markers_in_dtw.py data/Dvorak_7_Master-K1.npy data/Dvorak_7_Master.txt > data/Dvorak_7_K1_dtw.txt

3)
convert to audacity label files


4)
compare marker files



FILENAMES

audio, marker, audacity label files should be named <work>_<Master|K1>(_dtw_).<txt|mp3|wav|lab> (with _dtw_ for interpolated markers, without for manually labelled)
npy filename should reflect which two audio files are compared: for example "Dvorak 7_Master-K1.npy" (<work>_<version>-<version>.npy)

data/Dvorak_7_Master.mp3
data/Dvorak_7_K1.mp3
data/Dvorak_7_Master-K1.npy
data/Dvorak_7_Master.txt
data/Dvorak_7_K1_dtw.txt


TODO:
The exported marker files are not readable - there are two extra bytes first, and then \0 everywhere..
Fix (for now) by copying the text into a new file.





QUICK TEST:

n_fft = 4800
hop_size = 1200
resample = True

python3 print_dtw_points.py data/sir_duke_fast.mp3 data/sir_duke_slow.mp3
python3 find_markers_in_dtw.py data/sir_duke_fast-sir_duke_slow_22050_4800_1200.npy data/sir_duke_fast_markers.txt > data/sir_duke_slow_dtw.txt
