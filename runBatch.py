import sys, glob, re, os

python_exe = "python3"

#pythonscript = "D:/kkj/hkjh"
pythonscript = "dtw_markers.py"

datadir = sys.argv[1]

masterfiles = glob.glob(f"{datadir}/* master.txt")
#print(masterfiles)

for master_marker_file in masterfiles:
    base = re.sub(" master.txt", "", master_marker_file)
    #print(base)

    master_audio_file = f"{base} master.mp3"
    #print(master_audio_file)


    takes = glob.glob(f"{base} take [0-9]?*mp3")
    #print(takes)

    secondary_audio_files = "\" \"".join(takes)
    
    cmd = f"\"{python_exe}\" \"{pythonscript}\" \"{master_marker_file}\" \"{master_audio_file}\" \"{secondary_audio_files}\""
    print(cmd)
    os.system(cmd)
