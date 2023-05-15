import sys, os, re, glob
#import librosa, numpy

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



if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

verbose = False
allowOverwriteDTW = True
writeSrt = False

#TODO Gooey no longer works 230512
gui = False
import argparse
if len(sys.argv)>=2:
    gui = False
    #if not '--ignore-gooey' in sys.argv:
    #    sys.argv.append('--ignore-gooey')

if gui:
    from gooey import Gooey, GooeyParser
        

#@Gooey
def main():
    global verbose, overwriteDTW


    if gui:
        parser = GooeyParser()   
        #jun22 master_marker_file should always have tha same name
        #parser.add_argument('master_marker_file', widget="FileChooser")    
        parser.add_argument('master_audio_file', widget="FileChooser")    
        parser.add_argument('secondary_audio_file', nargs="*", widget="MultiFileChooser")    

    else:    
        parser = argparse.ArgumentParser()   
        #jun22 master_marker_file should always have tha same name
        #parser.add_argument('master_marker_file')    
        parser.add_argument('master_audio_file')    
        parser.add_argument('secondary_audio_file', nargs="*")    


    parser.add_argument('-o',action='store_true',dest='overwriteDTW', default=False, help="overwrite existing DTW file. Default: False")
    parser.add_argument('-v',action='store_true',dest='verbose', help="Verbose output. Default: False")    
    parser.add_argument('-m',action='store',dest='master_marker_file', default="label track.txt", help="Name of master marker file. Default: '<AUDIODIR>/label track.txt'")    

    args = parser.parse_args()

    #Imports here to speed up help message!
    import librosa, numpy
    global librosa, numpy


    master_audio_file = args.master_audio_file
    secondary_audio_files = args.secondary_audio_file
    verbose = args.verbose
    overwriteDTW = args.overwriteDTW


    
    audio_dir = os.path.dirname(master_audio_file)
    master_marker_file = f"{audio_dir}/{args.master_marker_file}"


    #old version, markers every 5s
    #createMasterMarkerFile(master_marker_file, master_audio_file)
    #new version 230512, markers according to beat_track
    createMasterMarkerFileByBeats(master_marker_file, master_audio_file)
    
    #sys.exit()
    
    debug("Reading markers from %s" % master_marker_file)
    master_markers = loadMarkers(master_marker_file)
    #jun22 name from master audio
    #master_audacity_file = re.sub("\.txt$", "_TimeSync.txt", master_marker_file)
    master_audacity_file = re.sub("\.mp3$", "_TimeSync.txt", master_audio_file)
    debug("Writing markers to %s" % master_audacity_file)
    writeAudacityLabels(master_markers, master_audacity_file)
    if writeSrt:
        master_srt_file = re.sub("\.txt$", ".srt", master_marker_file)
        debug("Writing markers to %s" % master_srt_file)
        writeSrtFile(master_markers, master_srt_file)
        print("Written output files: %s, %s" % (master_audacity_file, master_srt_file))
    else:
        print("Written output file: %s" % (master_audacity_file))


    debug("Done processing %d markers" % len(master_markers))

    #if len(sys.argv) == 2:
    #    sys.exit(1)
    #    
    #master_audio_file = sys.argv[2]
    #secondary_audio_files = sys.argv[3:]

    m = re.match("(.*?/?)([^/.]+).mp3", master_audio_file)
    #directory = m.group(1)
    master_audio_base = m.group(2)
    master_audio = None
    master_audio_loaded = False
    
    n_fft = 2205
    hop_size = 2205
    samplerate = 22050
    resample = True


    
    #Reverse list before getting secondary markers
    master_markers.reverse()
    debug("markers reversed: %s" % master_markers)
    
    for secondary_audio_file in secondary_audio_files:

        m = re.match("(.*?/?)([^/.]+).mp3", secondary_audio_file)
        directory = m.group(1)
        secondary_audio_base = m.group(2)

        dtw_file = "%s%s-%s-%s-%s-%s.npy" % (directory, master_audio_base, secondary_audio_base, samplerate, n_fft, hop_size)
        #print(f"overwriteDTW: {overwriteDTW} - checkWriteDTW({dtw_file}): {checkWriteDTW(dtw_file)}")
        if checkWriteDTW(dtw_file):
            if not master_audio_loaded:
                (master_audio, samplerate) = loadAudio(master_audio_file, resample)
                master_audio_loaded = True
            (secondary_audio, secondary_samplerate) = loadAudio(secondary_audio_file, resample)
            dtw = getDTW(master_audio, secondary_audio, samplerate, n_fft, hop_size)
            writeDTW(dtw, dtw_file)
        else:
            dtw = loadDTW(dtw_file)

        duration = librosa.get_duration(filename=secondary_audio_file)
        debug("duration %.2f" % duration)
        writeOutputFiles(dtw, master_markers, directory, secondary_audio_base, hop_size, samplerate, duration)


    #jun22
    #Finally run timesync2fcpxml.py
    #later import script instead of running in system
    audio_base = re.sub(" - master", "", master_audio_base)
    #cmd = f"python3 timesync2fcpxml/timesync2fcpxml.py '{audio_dir}/{audio_base} - syncmap.fcpxml' {audio_dir}/*master_TimeSync.txt {audio_dir}/*take\ *_TimeSync.txt > '{audio_dir}/{audio_base} - synced.fcpxml'"
    #print(cmd)
    #os.system(cmd)
    
    xmlfile = f"{audio_base} - syncmap.fcpxml"
    master_tp_file = f"{audio_base} - master_TimeSync.txt"
    take_tp_files = glob.glob(f"*take*_TimeSync.txt")
    #print(take_tp_files)
    #sys.exit()
    outfile = f"{audio_base} - synced.fcpxml"

    tp2fcp(xmlfile, master_tp_file, take_tp_files, outfile)




def createMasterMarkerFile(master_marker_file, master_audio_file):
    #jun22 create "label track.txt"
    master_duration = librosa.get_duration(filename=master_audio_file)
    print(f"Writing 5s intervals to {master_marker_file}")
    #print("master_duration %.2f" % master_duration)
    with open(master_marker_file, "w") as fh:
        i = 1
        tp = 5.0
        while tp < master_duration-5:
            fh.write(f"{tp}\t{tp}\t{i:02}\n")            
            i += 1
            tp += 5.0
        #HB 230301 Finally one timepoint at end of file
        print(f"last timepoint: {master_duration}")
        #print(f"last timepoint: {master_duration:.3}")
        #fh.write(f"{master_duration:.3}\t{master_duration:.3}\t{i:02}\n")
        fh.write(f"{master_duration}\t{master_duration}\t{i:02}\n")            
    
        
def createMasterMarkerFileByBeats(master_marker_file, master_audio_file, increment=10):
    master_duration = librosa.get_duration(filename=master_audio_file)
    print(f"Writing beat_times (increment={increment}) to {master_marker_file}")

    y, sr = librosa.load(master_audio_file)

    # Set the hop length; at 22050 Hz, 512 samples ~= 23ms
    hop_length = 512

    # Separate harmonics and percussives into two waveforms
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    # Beat track on the percussive signal
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)
    print(f"{tempo=}")
    #print(beat_frames)

    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    print(f"{beat_times=}")

    with open(master_marker_file, "w") as fh:
        #i = 0        
        i = increment        
        while i < len(beat_times):
            tp = beat_times[i]
            fh.write(f"{tp}\t{tp}\t{i:02}\n")            
            i += increment
        #HB 230301 Finally one timepoint at end of file
        print(f"last timepoint: {master_duration}")
        #print(f"last timepoint: {master_duration:.3}")
        #fh.write(f"{master_duration:.3}\t{master_duration:.3}\t{i:02}\n")
        fh.write(f"{master_duration}\t{master_duration}\t{i:02}\n")            
            
        


def checkWriteDTW(filename):
    
    ask = False
    if not os.path.exists(filename):
        return True
    elif overwriteDTW and os.path.exists(filename):
        return True
    elif ask:
        sys.stderr.write("DTW file %s already exists. Overwrite? y/N\n" % filename)
        reply = sys.stdin.read(1)
        if reply == "y":
            return True        
    else:
        return False


def loadAudio(filename, resample=True):
    print("Loading %s" % filename)
    if resample:
        audio, samplerate = librosa.load(filename)
    else:
        audio, samplerate = librosa.load(filename, sr=None)
    debug("samplerate %d" % samplerate)
    return (audio, samplerate)

def getDTW(x_1, x_2, samplerate, n_fft, hop_size):
    print("Getting chroma sequences")
    x_1_chroma = librosa.feature.chroma_stft(y=x_1, sr=samplerate, tuning=0, norm=2, hop_length=hop_size, n_fft=n_fft)
    x_2_chroma = librosa.feature.chroma_stft(y=x_2, sr=samplerate, tuning=0, norm=2, hop_length=hop_size, n_fft=n_fft)

    print("Aligning chroma sequences")
    #This was for an older version of librosa
    #D, wp = librosa.core.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')
    #D, wp = librosa.sequence.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')

    D, wp = librosa.sequence.dtw(X=x_1_chroma, Y=x_2_chroma, metric='euclidean')
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
def writeOutputFiles(dtw, master_markers, directory, secondary_audio_base, hop_size, samplerate, duration):
    secondary_marker_file = "%s%s_markers_dtw.txt" % (directory, secondary_audio_base)
    secondary_audacity_file = "%s%s_TimeSync.txt" % (directory, secondary_audio_base)
    secondary_srt_file = "%s%s_markers_dtw.srt" % (directory, secondary_audio_base)

    secondary_markers = getSecondaryMarkers(dtw, master_markers, hop_size, samplerate, duration)
    #debug("Second secondary marker: %s %s" % secondary_markers[1])

    writeAudacityLabels(secondary_markers, secondary_audacity_file)
    
    if writeSrt:
        writeMarkers(secondary_markers, secondary_marker_file)
        writeSrtFile(secondary_markers, secondary_srt_file)
        print("Written output files: %s, %s, %s" % (secondary_marker_file, secondary_audacity_file, secondary_srt_file))
    else:
        print("Written output file: %s" % (secondary_audacity_file))




import io    
    
def loadMarkers(filename):

    #cmd = "dos2unix '%s'" % filename
    #print(cmd)
    #os.system(cmd)
    
    markers = []
    lines = io.open(filename).readlines()
    i = 1
    for line in lines:
        line = line.strip()
        #print(f"{line}")
        line = re.sub("\0", "", line)
        #debug(line)

        rm = re.match("^.*([0-9]{2}):([0-9]{2}):([0-9]{2}):([0-9]{2})\s*(.*)\s*$", line)
        rm_aud = re.match("^([0-9.]+)\s+([0-9.]+)\s+(.+)$", line)
        if rm:
            #(h,m,s,ms) = line.split(":")
            h = rm.group(1)
            m = rm.group(2)
            s = rm.group(3)
            ms = rm.group(4)

            label = rm.group(5).strip()
            
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

            if label == "":                
                #HB why +1?
                #label = i+1
                label = i

        elif rm_aud:
            marker = float(rm_aud.group(1))
            label = rm_aud.group(3)
        else:
            continue
            
        markers.append( (label, marker) )
        i += 1
    return markers



def getSecondaryMarkers(wp, markers, hop_size, samplerate, duration):

    lines = []
    points_idx = numpy.int16(numpy.round(numpy.linspace(0, wp.shape[0] - 1, hop_size)))

    #markers.reverse()
    #debug("markers reversed: %s" % markers)

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
            (label, marker) = markers[mark_index]
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
            
            markers1_list.append( (label, marker) )
            markers2_list.append( (label, interp) )
        

            debug("%s: %s\t%f -> %f" % (marker_nr, label, marker,interp))
        
            mark_index +=1
            marker_nr -= 1
        
            latest_used_tp1 = prev_tp1
            latest_used_tp2 = prev_tp2

        prev_tp1 = tp1
        prev_tp2 = tp2
    
    #In case there was an error, just copy remaining markers
    while mark_index < len(markers):
        (label, marker) = markers[mark_index]
        debug("Copying marker: %s %s" % (label, marker))
        interp = marker
        markers1_list.append((label, marker))
        markers2_list.append((label, interp))
        debug("%s: %f -> %f" % (marker_nr, marker,interp))
        mark_index += 1
        marker_nr -= 1


    lastMarkerAlwaysAtEnd = True
    #HB 200427 Use duration instead of last marker = last timepoint is always at end of file
    if lastMarkerAlwaysAtEnd:
        (label, _) = markers2_list[0]
        markers2_list[0] = (label, duration)


        
    debug("markers2_list: %s" % markers2_list)
    markers2_list.reverse()
    debug("markers2_list reversed: %s" % markers2_list)
    return markers2_list

    
def writeMarkers(markers, marker_file):
    debug("Writing markers to %s" % marker_file)
    fh = open(marker_file, "w")
    i = 0
    while i < len(markers):
        (_, marker) = markers[i]
        fh.write("%s\n" % tp2str(marker))
        i += 1
    fh.close()

def writeAudacityLabels(markers, audacity_file):
    debug("Writing audacity labels to %s" % audacity_file)
    fh = open(audacity_file, "w")
    i = 0
    while i < len(markers):
        (label, tp) = markers[i]
        #print(f"{i} {tp}")
        fh.write("%.2f\t%.2f\t%s\n" % (tp, tp, label))
        i += 1
    fh.close()

def writeSrtFile(markers, srt_file):
    debug("Writing srt to %s" % srt_file)

    fh = open(srt_file, "w")
    i = 0
    while i < len(markers):

        (label, tp1) = markers[i]
        m1 = tp1/60
        s1 = tp1%60
        h1 = m1/60
        m1 = m1%60

        try:
            (_, tp2) = markers[i+1]
        except:
            tp2 = tp1+1

        m2 = tp2/60
        s2 = tp2%60
        h2 = m2/60
        m2 = m2%60

            
        fh.write("%d\n%02d:%02d:%.3f --> %02d:%02d:%.3f\n%s\n" % (i+1, h1, m1, s1, h2, m2, s2, label))
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
        

##########################
#
#  tp2fcpxml
#

from lxml import etree


def tp2fcp(xmlfile, master_tp_file, take_tp_files, outfile):
    with open(xmlfile) as fh:
        doc = etree.parse(fh)

    #clip, asset-clip, ref-clip are all ok
    clips = doc.xpath("library/event/project/sequence/spine/clip|library/event/project/sequence/spine/asset-clip|library/event/project/sequence/spine/ref-clip")


    
    log(f"Number of clips in xml : {len(clips)}")
    log(f"Number of Take sp files: {len(take_tp_files)}")
    assert len(clips) == len(take_tp_files)

    master_tp = readTimePointFile(master_tp_file)
    
    nr = 0    
    while len(clips) > nr:
        take_tp = readTimePointFile(take_tp_files[nr])
        assert len(master_tp) == len(take_tp)
        addTimepointsToClip(clips[nr], master_tp, take_tp)
        nr += 1


    #Change event and event/project name to basename
    basename = re.sub(" - syncmap.fcpxml", " - synced", os.path.basename(xmlfile))
    event = doc.xpath("library/event")[0]
    event.set("name",basename)
    project = doc.xpath("library/event/project")[0]
    project.set("name",basename)

    with open(outfile, "w") as fh:        
        etree.indent(doc, "    ")
        fh.write(str(etree.tostring(doc, xml_declaration=True), "utf-8"))

def log(msg):
    if verbose:
        sys.stderr.write(f"{msg}\n")

def readTimePointFile(filename):
    with open(filename) as fh:
        lines = fh.readlines()
    tps = []
    for line in lines:
        tps.append(float(line.split("\t")[0]))
    return tps
    
def addTimepointsToClip(clip, master_tp, take_tp):
    #log(clip)
    #log(take_tp)

    timeMaps = clip.xpath(".//timeMap")
    nrTimeMaps = len(timeMaps)
    for timeMap in timeMaps:
        #log(timeMap)
        addTimepointsToTimeMap(timeMap, master_tp, take_tp)
        #sys.exit()


def getDiff(tp1, tp2):
    val1 = int(tp1.get('time').replace("s", "").split("/")[0])
    rate1 = int(tp1.get('time').replace("s", "").split("/")[1])

    #log(f"VAL1:  {val1}")
    #log(f"RATE1: {rate1}")




    
    val2 = int(tp2.get('time').replace("s", "").split("/")[0])
    rate2 = int(tp2.get('time').replace("s", "").split("/")[1])

    #log(f"VAL2:  {val2}")
    #log(f"RATE2: {rate2}")

    q1 = 50 / rate1
    #if rate1 == 25:
    res1 = val1 * q1

    q2 = 50 / rate2
    #if rate2 == 25:   
    res2 = val2 * q2
    
    diff = int(res1-res2)

    log(f"RATE1: {rate1}")
    if rate1 != 25:    
        log(f"RES1: {res1}")
        log(f"RES2: {res2}")    
    log(f"DIFF: {diff}")
    
    return diff

        

def addTimepointsToTimeMap(timeMap, master_tp, take_tp):
    #first_timept = timeMap[0]
    second_timept = timeMap[1]
    zeropoint_string = second_timept.get("time")


    #remove second last timepoint in timeMap, it will be replaced by last in tp
    #print(dir(timeMap))
    second_last_timept = timeMap[-2]
    timeMap.remove(second_last_timept)
   

    
    #save last timepoint in timeMap, to append finally
    last_timept = timeMap[-1]
    timeMap.remove(last_timept)

    #log(f"SECOND LAST TIMEPT:   {second_last_timept.get('time')}")
    #log(f"LAST TIMEPT:          {last_timept.get('time')}")
    #log(f"LAST TIMEPT VALUE:          {last_timept.get('value')}")

    diffSecondLastToLast = getDiff(last_timept,second_last_timept)
    #log(f"DIFF:       {diffSecondLastToLast}")
    
    (zeropoint, fps) = zeropoint_string[:-1].split("/")
    #log(fps)
    factor = 50/int(fps)
    #log(factor)
    zeropoint_50f = int(int(zeropoint)*factor)
    #log(f"zeropoint_50f: {zeropoint_50f}")

    nr = 0
    while len(master_tp) > nr:
        master_timepoint = master_tp[nr]
        take_timepoint = take_tp[nr]

        master_timepoint_50f = f"{int(master_timepoint*50+zeropoint_50f)}/50s"
        take_timepoint_50f = f"{int(take_timepoint*50+zeropoint_50f)}/50s"

        new_timept = etree.Element("timept")
        new_timept.set("interp", "linear")
        #new_timept.set("value", master_timepoint_50f)
        #new_timept.set("time", take_timepoint_50f)
        new_timept.set("time", master_timepoint_50f)
        new_timept.set("value", take_timepoint_50f)

        #log(etree.tostring(new_timept))
        timeMap.append(new_timept)

        nr += 1


    new_last_timepoint_50f = f"{int(take_timepoint*50+zeropoint_50f+diffSecondLastToLast)}/50s"

    new_last_timept = etree.Element("timept")
    new_last_timept.set("interp", "linear")
    new_last_timept.set("time", new_last_timepoint_50f)
    new_last_timept.set("value", new_last_timepoint_50f)


    #log(f"NEW SECOND LAST TIMEPT VALUE:  {new_timept.get('value')}")
    #log(f"NEW LAST TIMEPT VALUE:         {new_last_timept.get('value')}")

    
    timeMap.append(new_last_timept) 




        
if __name__ == "__main__":
#    if len(sys.argv) > 1:
        main()
#    else:
#        sys.stderr.write("USAGE: python3 dtw_markers.py MASTER_MARKERS (MASTER_AUDIO SECONDARY_AUDIO ..)\n")
#        sys.stderr.write("EXAMPLE: python3 dtw_markers.py test_data/sir_duke_fast_markers.txt\n")
#        sys.stderr.write("EXAMPLE: python3 dtw_markers.py test_data/sir_duke_fast_markers.txt test_data/sir_duke_fast.mp3 test_data/sir_duke_slow.mp3\n")
#        sys.exit()
