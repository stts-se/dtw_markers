import sys

marker_file1 = sys.argv[1]
marker_file2 = sys.argv[2]

debug = False


nr_frames_per_second = 50.0

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




markers1 = readMarkers(marker_file1)
markers2 = readMarkers(marker_file2)

if not len(markers1) == len(markers2):
    print("ERROR - different length: %s: %d, %s: %d" % (marker_file1, len(markers1), marker_file2, len(markers2)))
    sys.exit()

total_diff = 0
exact = 0
less_01 = 0
less_02 = 0
less_05 = 0
more_05 = 0

i = 0
while i < len(markers1):
    mark1 = markers1[i]
    mark2 = markers2[i]

    diff = mark1-mark2

    if diff < 0:
        total_diff = total_diff-diff
    else:
        total_diff = total_diff+diff
        

    if debug:
        print("%d\t%.2f" % (i,diff))

    i = i+1

    if diff == 0.0:
        exact += 1
    elif -0.1 < diff < 0.1:
        less_01 += 1
    elif -0.2 < diff < 0.2:
        less_02 += 1
    elif -0.5 < diff < 0.5:
        less_05 += 1
    else:
        more_05 += 1


total = float(len(markers1))
exact_pc = exact/total*100
less_01_pc = less_01/total*100
less_02_pc = less_02/total*100
less_05_pc = less_05/total*100
more_05_pc = more_05/total*100


print("Total:\t%d\t%.2f s" % (total, total_diff))
print("Exact:\t%d\t%.2f %%" % (exact, exact_pc))
print("<0.1s:\t%d\t%.2f %%" % (less_01, less_01_pc))
print("<0.2s:\t%d\t%.2f %%" % (less_02, less_02_pc))
print("<0.5s:\t%d\t%.2f %%" % (less_05, less_05_pc))
print(">0.5s:\t%d\t%.2f %%" % (more_05, more_05_pc))
