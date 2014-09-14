%% DETECT EVENTS
%
%Author: Dylan Thiemann (dylan-thiemann@uiowa.edu) June 13, 2013
%
%Group: University of Iowa Computational Epidemiology Research Group
%
%detects events within a .wav file by utilizing the moving standard
%deviation 
%
%Takes folders from a path on my local machine so be sure to indicate your
%specfic path when implementing this function
% 
%I've altered the k value for the movingstd function, I'm still working on
%a way to be more precise with the detection algorithm
%
%
%*STILL A WORK IN PROGRESS*
%

%% Clean up workspace and command window
clc
clear all

%create new file for the results of 
edit results.txt
fileID = fopen('results.txt','wt');

%Text file that contains the list of input (.wav) files
fp=fopen('/Matlab/Dylan_Folder/lists/input_list.txt','r');
j=1;
while(~feof(fp))
    line=fgetl(fp);
    %Adds the rest of the address to the beginning of the file location to
    %be recognized by the script
    input_list{j}=line;
    j=j+1;
end;
numAudioFiles=j-1;
fclose(fp);

%% Start event detection of all files in input_list
%

for x = 1:numAudioFiles
    data = [];
    Te = 0.05;
    [audio,Fs] = audioread(input_list{x});

    filterLength = Fs * Te;
    if mod(filterLength,2) == 0
        filterLength = filterLength + 1;
    end
    
%% Calculates the moving average by squaring the input audio
%to remove negative values
%
    
    average = movingAverageFilter(audio.^2,filterLength);
    
%Standardize the average values in order to have all values between 0 and 1
    average = average./max(average);
    siz = size(average);
    i = 1;
    
    
%% Event Detector
%
    
    while (i < siz(2))
        startTime = 0;
        endTime = 0;
%Using 0.06 as the threshold needed to pass inorder to classify
%something as an event
        if (average(i) > 0.06)
            startTime = i;
            while (average(i) > 0.06)
                i = i + 1;
            end
            endTime = i;
            data = [data; startTime endTime];
        end
        i = i + 1;
    end
    siz2 = size(data(:,1));
    fprintf(fileID,['file ' input_list{x} ' contains ' int2str(siz2(1)) ' events \n']);
end

fclose(fileID);
