function [ filelist ] = listfiles( pathname, filetype )
%LIST FILES 
%   [ output ] = listfiles( inpath )
%==========================================================================
%   Takes as input a path, and finds all the .wav files within that path within
%   that paths subdirs, and returns an array of their paths.
%   Author: David Campbell david-campbell@uiowa.edu
%   University of Iowa CompEpi Group 2013
%==========================================================================

% Search the current directory for .wav files
files=dir(strcat(pathname, filetype));
[r, c]=size(files);
if r;
    % If there are files, make a list of them
    temp=struct2cell(files);
    [r, c]=size(temp);
    filelist=temp(1,1:c)';
    filelist=strcat(pathname, filelist);
else
    % If there aren't files, file list is empty
    filelist=[];
end;

% Search all the directories within the directory
listing=dir(pathname);

% Ignore hidden directories
listing=listing(arrayfun(@(x) ~strcmp(x.name(1),'.'),listing));

for i=1:length(listing),...
    if listing(i).isdir;
        % In directories, run listfiles on each dir.  
        newpath=strcat(strcat( pathname, listing(i).name ),'/');
        newfiles=listfiles(newpath, filetype);
        % Append contents to wavlist.
        filelist=[filelist; newfiles]; 
        % If this dir doesn't exist in output dir, make it.
        odir=strrep(strcat(strcat(strcat(pwd,'/'),pathname),listing(i).name),'input','output');
        if ~exist(odir, 'dir');
            mkdir(odir);
        end;
    end;
end;

end

