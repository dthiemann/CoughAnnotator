function [ output ] = annotate( data, fs, T_start, T_end )
%Annotate[ output ] = annotate( data, fs, T_start, T_end )
%   This function takes an inputs the audio data, frames per second, and
%   event starts and ends, and starts a process where the program accepts 
%   user input 1 or 0 to decide whether a sample is a cough.  Any other 
%   input will result in the sound being played again.  

N=length(data);
output=zeros(N,1);

prompt='Press 1 if a cough, 2 to replay, anything else to contine';
% For each event, create a figure and plot the data, highlighting the event
% and then playing the associated audio and waiting for user input on
% whether the event is a cough or not.  
figure();
plot(data);
hold all;
event=zeros(N,1);
event(T_start:T_end)=1;
plot(event);
result=2;
% While the result isn't binary, play the sound and receive user
% input.
while result ~= 1 && result ~= 0
    soundsc(data(T_start:T_end), fs);
    result = input(prompt);
end;
output=result;
close();
end

