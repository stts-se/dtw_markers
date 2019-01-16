import sys



nr_frames_per_second = 50.0

def readMarkers(lines):
    markers = []
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



lines = sys.stdin.readlines()
markers = readMarkers(lines)


i = 0
while i < len(markers):
    print("%.2f\t%.2f\t%d" % (markers[i], markers[i], i+1))
    i += 1
