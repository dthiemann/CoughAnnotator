import os

directory = "/Users/dylanthiemann/Desktop/2_4_14-annotated/"
directoryContents =  os.listdir(directory)

textFiles = [x for x in directoryContents if x[-3:] == "txt"]

completeFile = open("2_4_14_annotated_from_Dylan.txt","a")

for fileName in textFiles:
    tempFile = open(fileName,"r")
    completeFile.write(tempFile.readline() + "\n")
    tempFile.close()
    
completeFile.close()