import sys
from lxml import etree


xmlfile = sys.argv[1]
master_tp_file = sys.argv[2]
take_tp_files = sys.argv[3:]


def main():
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

    etree.indent(doc, "    ")
    print(str(etree.tostring(doc, xml_declaration=True), "utf-8"))

def log(msg):
    sys.stderr.write(f"{msg}\n")

def readTimePointFile(filename):
    with open(filename) as fh:
        lines = fh.readlines()
    tps = []
    for line in lines:
        tps.append(float(line.split("\t")[0]))
    return tps
    
def addTimepointsToClip(clip, master_tp, take_tp):
    log(clip)
    #log(take_tp)

    timeMaps = clip.xpath(".//timeMap")
    for timeMap in timeMaps:
        log(timeMap)
        addTimepointsToTimeMap(timeMap, master_tp, take_tp)


def addTimepointsToTimeMap(timeMap, master_tp, take_tp):
    #first_timept = timeMap[0]
    second_timept = timeMap[1]
    zeropoint_string = second_timept.get("time")

    #save last timepoint in timeMap, to append finally
    last_timept = timeMap[-1]
    timeMap.remove(last_timept)
    
    #remove second last timepoint in timeMap, it will be replaced by last in tp
    #print(dir(timeMap))
    second_last_timept = timeMap[-2]
    timeMap.remove(second_last_timept)
    
    (zeropoint, fps) = zeropoint_string[:-1].split("/")
    #log(fps)
    factor = 50/int(fps)
    #log(factor)
    zeropoint_50f = int(int(zeropoint)*factor)
    log(f"zeropoint_50f: {zeropoint_50f}")

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

    timeMap.append(last_timept) 

    

main()    
