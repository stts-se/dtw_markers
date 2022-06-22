## TimeSync_2.1.py

```
USAGE:

Simple gui:
python3 TimeSync_2.1.py

Help message:
python3 TimeSync_2.1.py -h

Command line example:
python3 TimeSync_2.1.py test_data/sir_duke_fast.mp3 test_data/sir_duke_slow.mp3

```



















## dtw_markers.py

```
USAGE: python3 dtw_markers.py MASTER_MARKERS (MASTER_AUDIO SECONDARY_AUDIO_FILE ..)
EXAMPLE: python3 dtw_markers.py test_data/sir_duke_fast_markers.txt
EXAMPLE: python3 dtw_markers.py test_data/sir_duke_fast_markers.txt test_data/sir_duke_fast.mp3 test_data/sir_duke_slow.mp3

MASTER_MARKERS can be in "marker" or audacity format.
MASTER_MARKERS are converted to audacity and srt format.

If two or more soundfiles are given, they are aligned by dtw and marker files for secondary audio is written, in "marker", audacity, and srt formats"

```

```
-n: Don't overwrite dtw files (otherwise you will be asked, press y+enter for yes, any other key + enter for no)
-v: verbose output
```








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

`python3 print_dtw_points.py data/Dvorak_7_Master.mp3 data/Dvorak_7_K1.mp3 `

output in file with name generated from input files, samplerate, n_fft, hop_size


### 2) Load dtw points and markers, print new markers

find_markers_in_dtw.py

arguments:

1. input filename for dtw points (.npy)
2. input filename for markers (.txt)

output to stdout: new markers

example:

`python3 find_markers_in_dtw.py data/Dvorak_7_Master-Dvorak_7_K1-22050-2205-2205.npy data/Dvorak_7_Master.txt > data/Dvorak_7_K1_markers_dtw.txt`

### 3) convert to audacity label files

example:

`cat data/Dvorak_7_K1_markers_dtw.txt | python3 markers2aud_labels.py > data/Dvorak_7_K1_markers_dtw_audacity.txt`

### 4) compare marker files


### TODO:
The original marker files are not readable - there are two extra bytes first, and then \0 everywhere..
Fix (for now) by copying the text into a new file.


### QUICK TEST:
```
python3 print_dtw_points.py test_data/sir_duke_fast.mp3 test_data/sir_duke_slow.mp3
python3 find_markers_in_dtw.py test_data/sir_duke_fast-sir_duke_slow-22050-2205-2205.npy test_data/sir_duke_fast_markers.txt > test_data/sir_duke_slow_markers_dtw.txt
cat test_data/sir_duke_slow_markers_dtw.txt | python3 markers2aud_labels.py > test_data/sir_duke_slow_markers_dtw_audacity.txt
```



TODO:
läs audacity-labelfil
ta namn på marker från aud
skriv ut srt (från punkt till nästa punkt)
om ingen ljudfil i input, läs in label-fil och skriv ut ny aud-label och srt (= konvertera)


Ändrat anrop: först marker-fil, sedan masterljud, sedan mer ljud
