function [ output_args ] = annotate_event( filename, outpath, Tstart, Tend, data, fs )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
% Define variables
Tw = 25;                % analysis frame duration (ms)
Ts = 10;                % analysis frame shift (ms)
alpha = 0.97;           % preemphasis coefficient
M = 20;                 % number of filterbank channels
C = 13;                 % number of cepstral coefficients
L = 22;                 % cepstral sine lifter parameter
LF = 100;               % lower frequency limit (Hz)
HF = 6000;              % upper frequency limit (Hz)
N=length(data);


if annotate( data, fs, Tstart, Tend);
    filename=strcat('data/iscough/',filename);
else
    filename=strcat('data/notcough/',filename);
end;

[ MFCCs, FBEs, frames ] = ...
    mfcc( data, fs, Tw, Ts, alpha, @hamming, [LF HF], M, C+1, L );

dataanalysis=[MFCCs, FBEs, frames];

save(filename, dataanalysis);
audiowrite(filename, data(Tstart:Tend), fs);
    
                
end

