function [ data ] = individualEventDetector( audioFileName,Te,showPlot) 
%*INDIVIDUAL EVENT DETECTOR*
%
% Parameters
%   audioFileName = an audio file location URL
%   Te (optional) = enveloping time (default = 0.05)
%   showPlot (optional) = boolean variable to show plot (default = false)
%
%Author: Dylan Thiemann (dylan-thiemann@uiowa.edu) June 13, 2013
%
%Group: University of Iowa Computational Epidemiology Research Group
%
%detects events within a .wav file by utilizing the moving standard
%deviation 
%
%Function is the same as eventDetector.m but allows the user to analyze one
%file at a time without having to tamper with eventDetector.m
% 
%eventDetector.m is not up to date
%
%I've altered the k value for the movingstd function, I'm still working on
%a way to be more precise with the detection algorithm
%
%


%Has showplot as an optional variable
if nargin < 3
    showPlot = false;
end
if nargin < 2
    Te = 0.05;
    showPlot = false;
end

%% Initializes the audio file
%

data = [];
[audio,Fs] = audioread(audioFileName);
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
        
        %Uses a threshold to detect an event
        while (average(i) > 0.06)
            i = i + 1;
        end
        endTime = i;
        data = [data; startTime endTime];
    end
    i = i + 1;
end

%% Ploting and displaying detected events
%

if showPlot
    
    if data
        siz2 = size(data(:,1));
        disp(['The file: ' audioFileName ' contains ' int2str(siz2(1)) ' events'])
        
        plot(average,'r') %plots the smoothed audiofile in red
        set(gca,'Color','k') %Change background color to black for easy viewing
        hold all
        %plot(audio,'y')
        for x = 1: siz2
            line([data(x) data(x)],[0 1]) %Line to mark start of event (blue)
            line([data(x,2) data(x,2)],[0 1],'color','g') %Line to mark end of event (green)
        end
        siz2 = size(data(:,1));
        
    %If data is empty...
    else
        plot(average)
        disp(['The file: ' audioFileName ' contains 0 events'])
    end
end

end
        


    



