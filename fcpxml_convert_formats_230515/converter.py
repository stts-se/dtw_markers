import sys, json, xmljson

from lxml.etree import parse, fromstring, tostring, indent


def inspect(jsdoc):
    print(len(jsdoc))
    print(type(jsdoc))
    print(jsdoc.keys())
    for item in jsdoc["fcpxml"]:
        print(item)

    spine = jsdoc["fcpxml"]["library"]["event"]["project"]["sequence"]["spine"]        
    for item in spine:
        print(item)        
        #print(spine[item])


    assetclip = jsdoc["fcpxml"]["library"]["event"]["project"]["sequence"]["spine"]["asset-clip"]
    for item in assetclip:
        print(f"{type(item)=}")        
        print(f"{item=}")        
        #print(assetclip[item])
    



with open(sys.argv[1]) as fh:
    xmldoc = parse(fh).getroot()

jsdoc = xmljson.badgerfish.data(xmldoc)

inspect(jsdoc)


xml2 = xmljson.badgerfish.etree(jsdoc)[0]
#indent(xml2, space="\t", level=0)
#print(tostring(xml2, encoding="unicode"))

