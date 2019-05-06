import sys, os, re
import librosa, numpy

#Main script for dtw_markers
#Input:
#Master audio file
#Master marker file
#Secondary audio files

#For each secondary audio file:
#Get dtw points Master-Secondary, write to file
#(if file exists - ask to overwrite)

#If dtw file exists - load dtw file and Master marker file
#Print Secondary marker file and audacity label file

verbose = False
allowOverwriteDTW = True

def main():
    global verbose, allowOverwriteDTW

    if "-n" in sys.argv:
        allowOverwriteDTW = False
        sys.argv.remove("-n")

    if "-v" in sys.argv:
        verbose = True
        sys.argv.remove("-v")
    
    master_audio_file = sys.argv[1]
    master_marker_file = sys.argv[2]
    secondary_audio_files = sys.argv[3:]

    m = re.match("(.*?/?)([^/.]+).mp3", master_audio_file)
    #directory = m.group(1)
    master_audio_base = m.group(2)
    master_audio = None
    master_audio_loaded = False
    
    n_fft = 2205
    hop_size = 2205
    samplerate = 22050
    resample = True

    debug("Reading markers from %s" % master_marker_file)
    master_markers = loadMarkers(master_marker_file)
    master_audacity_file = re.sub("\.txt$", "_audacity.txt", master_marker_file)
    writeAudacityLabels(master_markers, master_audacity_file)
    debug("Read %d markers" % len(master_markers))

    
    for secondary_audio_file in secondary_audio_files:

        m = re.match("(.*?/?)([^/.]+).mp3", secondary_audio_file)
        directory = m.group(1)
        secondary_audio_base = m.group(2)

        dtw_file = "%s%s-%s-%s-%s-%s.npy" % (directory, master_audio_base, secondary_audio_base, samplerate, n_fft, hop_size)
        if allowOverwriteDTW and checkWriteDTW(dtw_file):
            if not master_audio_loaded:
                master_audio = loadAudio(master_audio_file, resample)
                master_audio_loaded = True
            secondary_audio = loadAudio(secondary_audio_file, resample)
            dtw = getDTW(master_audio, secondary_audio, samplerate, n_fft, hop_size)
            writeDTW(dtw, dtw_file)
        else:
            dtw = loadDTW(dtw_file)

        secondary_marker_file = "%s%s_markers_dtw.txt" % (directory, secondary_audio_base)
        secondary_audacity_file = "%s%s_markers_dtw_audacity.txt" % (directory, secondary_audio_base)
        writeMarkersAndAudacityLabels(dtw, master_markers, secondary_marker_file, secondary_audacity_file, hop_size, samplerate)

        
def checkWriteDTW(filename):
    if not os.path.exists(filename):
        return True
    else:
        sys.stderr.write("DTW file %s already exists. Overwrite? y/N\n" % filename)
        reply = sys.stdin.read(1)
        if reply == "y":
            return True        
        
    return False


def loadAudio(filename, resample=True):
    print("Loading %s" % filename)
    if resample:
        audio, samplerate = librosa.load(filename)
    else:
        audio, samplerate = librosa.load(filename, sr=None)
    debug("samplerate %d" % samplerate)
    return audio

def getDTW(x_1, x_2, samplerate, n_fft, hop_size):
    print("Getting chroma sequences")
    x_1_chroma = librosa.feature.chroma_stft(y=x_1, sr=samplerate, tuning=0, norm=2, hop_length=hop_size, n_fft=n_fft)
    x_2_chroma = librosa.feature.chroma_stft(y=x_2, sr=samplerate, tuning=0, norm=2, hop_length=hop_size, n_fft=n_fft)

    print("Aligning chroma sequences")
    D, wp = librosa.core.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')
    print("Finished aligning chroma sequences")
    return wp
    


def writeDTW(dtw, filename):
    print("Saving to %s" % filename)
    out = open(filename, "wb")
    numpy.save(out, dtw)
    out.close()


def loadDTW(filename):
    debug("Loading dtw from %s" % filename)
    wp = numpy.load(open(filename, "rb"))
    debug("len(wp): %s" % len(wp))
    return wp


nr_frames_per_second = 50.0
def writeMarkersAndAudacityLabels(dtw, master_markers, secondary_marker_file, secondary_audacity_file, hop_size, samplerate):
    secondary_markers = getSecondaryMarkers(dtw, master_markers, hop_size, samplerate)
    writeMarkers(secondary_markers, secondary_marker_file)
    writeAudacityLabels(secondary_markers, secondary_audacity_file)





import io    
    
def loadMarkers(filename):

    cmd = "dos2unix '%s'" % filename
    print(cmd)
    os.system(cmd)
    
    markers = []
    lines = io.open(filename).readlines()
    for line in lines:
        line = line.strip()

        rm = re.match("^.*\s([0-9]{2}):([0-9]{2}):([0-9]{2}):([0-9]{2}).*$", line)
        if rm:
            #(h,m,s,ms) = line.split(":")
            h = rm.group(1)
            m = rm.group(2)
            s = rm.group(3)
            ms = rm.group(4)
        else:
            continue
            
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
    return markers

def loadMarkersOLD(filename):
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
    return markers



def getSecondaryMarkers(wp, markers, hop_size, samplerate):

    lines = []
    points_idx = numpy.int16(numpy.round(numpy.linspace(0, wp.shape[0] - 1, hop_size)))

    markers.reverse()

    mark_index = 0
    marker_nr = len(markers)

    prev_tp1 = None
    prev_tp2 = None
    latest_used_tp1 = None
    latest_used_tp2 = None
    markers1_list = []
    markers2_list = []

    debug("Finding markers")
    for tp1, tp2 in wp[points_idx] * hop_size / samplerate:
        if prev_tp1 and tp1 > prev_tp1:
            sys.stderr.write("ERROR: prev_tp1 = %s, tp1 = %s\n" % (prev_tp1, tp1))
            sys.stderr.write("Probably because the first audio is longer than the second?\n")
            #sys.exit()
        try:
            marker = markers[mark_index]
        except:
            #marker = None
            break

        #debug("Looking for marker %s: prev_tp1: %s, tp1: %s" % (marker, prev_tp1, tp1))

    
        if prev_tp1 and latest_used_tp1 and marker > prev_tp1:
            prev_tp1 = latest_used_tp1
            prev_tp2 = latest_used_tp2


        if (marker and prev_tp1 and marker < prev_tp1 and marker >= tp1) or (prev_tp1 == None and marker >= tp1):
            #hb special case.. can't interpolate if at end of file
            if prev_tp1 == None:
                interp = marker
            else:
                interp = interpolateTimepoint(marker, prev_tp1, prev_tp2, tp1, tp2)

            debug("prev_tp1: %s, tp1: %.2f, marker: %.2f, interp: %s" % (prev_tp1,tp1,marker,interp))
            
            markers1_list.append(marker)
            markers2_list.append(interp)
        

            debug("%s: %f -> %f" % (marker_nr, marker,interp))
        
            mark_index +=1
            marker_nr -= 1
        
            latest_used_tp1 = prev_tp1
            latest_used_tp2 = prev_tp2

        prev_tp1 = tp1
        prev_tp2 = tp2
    
    #In case there was an error, just copy remaining markers
    while mark_index < len(markers):
        marker = markers[mark_index]
        debug("Copying marker: %s" % marker)
        interp = marker
        markers1_list.append(marker)
        markers2_list.append(interp)        
        debug("%s: %f -> %f" % (marker_nr, marker,interp))
        mark_index += 1
        marker_nr -= 1

    markers2_list.reverse()
    return markers2_list

    
def writeMarkers(markers, marker_file):
    fh = open(marker_file, "w")
    i = 0
    while i < len(markers):
        marker = markers[i]
        fh.write("%s\n" % tp2str(marker))
        i += 1
    fh.close()

def writeAudacityLabels(markers, audacity_file):
    fh = open(audacity_file, "w")
    i = 0
    while i < len(markers):
        fh.write("%.2f\t%.2f\t%d\n" % (markers[i], markers[i], i+1))
        i += 1
    fh.close()




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

def debug(msg):
    if verbose:
        sys.stderr.write("%s\n" % msg)
        

if __name__ == "__main__":
    if len(sys.argv) > 3:
        main()
    else:
        sys.stderr.write("USAGE: python3 dtw_markers.py MASTER_AUDIO MASTER_MARKERS SECONDARY_AUDIO ..\n")
        sys.stderr.write("EXAMPLE: python3 dtw_markers.py test_data/sir_duke_fast.mp3 test_data/sir_duke_fast_markers.txt test_data/sir_duke_slow.mp3\n")
        sys.exit()
