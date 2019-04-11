### 1) Extract chroma features, compute dtw points and write to file

print_dtw_points.py

```
settings:
n_fft
hop_size
```

arguments:

1. input audio file
2. input audio file


example:

`python print_dtw_points.py data/Dvorak_7_Master.mp3 data/Dvorak_7_K1.mp3 `

output in file with name generated from input files, samplerate, n_fft, hop_size


### 2) Load dtw points and markers, print new markers

find_markers_in_dtw.py

arguments:

1. input filename for dtw points (.npy)
2. input filename for markers (.txt)

output to stdout: new markers

example:

`python find_markers_in_dtw.py data/Dvorak_7_Master-Dvorak_7_K1-22050-2205-2205.npy data/Dvorak_7_Master.txt > data/Dvorak_7_K1_markers_dtw.txt`

### 3) convert to audacity label files

example:

`cat data/Dvorak_7_K1_markers_dtw.txt | python3 markers2aud_labels.py > data/Dvorak_7_K1_markers_dtw_audacity.txt`

### 4) compare marker files


### TODO:
The original marker files are not readable - there are two extra bytes first, and then \0 everywhere..
Fix (for now) by copying the text into a new file.





QUICK TEST:

python3 print_dtw_points.py test_data/sir_duke_fast.mp3 test_data/sir_duke_slow.mp3
python3 find_markers_in_dtw.py test_data/sir_duke_fast-sir_duke_slow-22050-2205-2205.npy test_data/sir_duke_fast_markers.txt > test_data/sir_duke_slow_markers_dtw.txt
cat test_data/sir_duke_slow_markers_dtw.txt | python3 markers2aud_labels.py > test_data/sir_duke_slow_markers_dtw_audacity.txt
