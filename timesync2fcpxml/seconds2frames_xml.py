

#take1 är första "clip" i sequence->spine
#varje clip innehåller i sin tur flera clip som ska få samma tidkoder

#value och time i den andra timept i timeMap
zeropoint_string = "946374/25s"
(zeropoint, fps) = zeropoint_string[:-1].split("/")

print(fps)

factor = 50/int(fps)

print(factor)

zeropoint_50f = int(int(zeropoint)*factor)

print(zeropoint_50f)


take1_timepoint = 3.58
take1_timepoint_50f = int(take1_timepoint*50+zeropoint_50f)



master_timepoint = 3.42
master_timepoint_50f = int(master_timepoint*50+zeropoint_50f)



xml_timept = f"<timept interp=\"linear\" value=\"{master_timepoint_50f}/50s\" time=\"{take1_timepoint_50f}/50s\"/>"

print(xml_timept)

#första och andra timept ska vara kvar
#lägg till efter andra timept
#sista timept ska vara kvar




#1) läs in xml och master
#2) för varje "spine"->"clip": läs in take, konvertera format, lägg till timept-element
#3) skriv ut xml
