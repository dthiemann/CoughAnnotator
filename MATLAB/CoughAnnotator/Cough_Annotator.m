% This is where your code & data is located. 
% Subdirectories
posinpath='~/Documents/MATLAB/CompEpi/data/input/process/';


%% Make the Current directory your datapath
cd(posinpath);

%% Find all the .wav files and build the necessary output directory
% structure.
coughs      =listfiles( posinpath, '*.wav' );

%% Annotate each coughfile
cellfun(@annotate_audiofile,coughs);