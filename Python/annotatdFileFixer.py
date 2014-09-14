#takes an annotated file and rewrites the file and to show beginning and end of event
import os
directory = "/Users/dylanthiemann/Desktop/Cough Data/2_6_14/annotated_by_dylan/"
listOfFilesTemp = os.listdir(directory)
listOfFiles = [x for x in listOfFilesTemp if x[-4:] == "anno"]

for annotated in listOfFiles:
    fileLocal = directory + annotated
    newFile = open(fileLocal,'r')
    listOfCoughs = []
    for line in newFile:
        lineList = line.split(",")
        listOfCoughs.append(lineList)
    newFile.close()
    if not (lineList[0] == "No coughs"):
        newFile = open(fileLocal, 'w')
        for event in listOfCoughs:
            newFile.write(event[0] + "," + str(int(event[1])-int(event[0])) + "\n")
        newFile.close()
