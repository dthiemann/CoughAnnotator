function [ movingAverage ] = movingAverageFilter( audio,Fl )
%% MOVINGAVERAGEFILTER 
%
%Author: Dylan Thiemann (dylan-thiemann@uiowa.edu)  June 17, 2013
%
%Group: University of Iowa Computational Epidemiology Research Group
%

audioSize = size(audio);
audio = audio';

%Need to pad the audio file with zeros to ensure proper number of indices
%to account for the filter length
PadLength = floor((Fl-1)/2);
Pad = zeros(1,PadLength);

%Outputs a new 1 x M matrix which is used for finding the average
newAudio = [Pad audio Pad];
for i = 1: audioSize
    tempAve = 0;
    for j = 1: Fl
        tempAve = tempAve + newAudio(i+j-1);
    end
    movingAverage(i) = tempAve./Fl;
end

end

