import sys,re


editsfile = sys.argv[1]
if editsfile.endswith(".txt"):
    outfile = re.sub(".txt$",".srt", editsfile)
else:
    outfile = editsfile+".srt"

print("%s --> %s" % (editsfile, outfile))

lines = open(editsfile).readlines()
out = open(outfile, "w")

i = 1
for line in lines:
    #00:00:00:00	00:00:36:00	K02
    m = re.search("^\s*([0-9]{2}):([0-9]{2}):([0-9]{2}):([0-9]{2})\s+([0-9]{2}):([0-9]{2}):([0-9]{2}):([0-9]{2})\s+(.+)$", line)

    if not m:
        print("Something wrong with line:\n%s" % line)
        sys.exit()


    #print(line)
        
    h1 = m.group(1)
    m1 = m.group(2)
    s1 = m.group(3)
    f1 = m.group(4)
                  
    h2 = m.group(5)
    m2 = m.group(6)
    s2 = m.group(7)
    f2 = m.group(8)

    text = m.group(9)

    #convert frames to ms
    framesPerSecond = 25
    ms1 = int(f1)*(100/framesPerSecond)
    ms2 = int(f2)*(100/framesPerSecond)

    out.write("""%d
%s:%s:%s.%02d --> %s:%s:%s.%02d
%s\n\n""" % (i,h1,m1,s1,ms1,h2,m2,s2,ms2,text))
    i += 1
    
