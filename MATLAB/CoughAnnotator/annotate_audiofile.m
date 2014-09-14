function annotate_audiofile( filename )
%Annotate[ output ] = annotate( data, fs, T_start, T_end )
%   This function takes an inputs the audio data, frames per second, and
%   event starts and ends, and starts a process where the program accepts 
%   user input 1 or 0 to decide whether a sample is a cough.  Any other 
%   input will result in the sound being played again.  
filename
[T_start, T_end, data, fs ]=detect_events( filename, 0 ); 
num_events=size(T_start,1);
N=size(data,1);
notaccepted=1;
result=0;
prompt='Press 1 if a cough, 2 for secondary, 3 to replay previous,\n any other for replay, 8 to skip file, 0 for not a cough\n';
prompt_accept='Accept the file? (1 for yes, 0 for no)\n\n';

%% Control Flags
YES         = 1;
NO          = 0;
SECONDARY   = 2;
REPLAYPREV  = 3;
SKIP        = 8;

%% For each event, create a figure and plot the data, highlighting the event
% and then playing the associated audio and waiting for user input on
% whether the event is a cough or not.  
gdata=data.^2;
while notaccepted && result ~= SKIP
    %% Data Structures for the loop
    output=zeros(N,1);
    output_times=zeros(num_events,2);
    coughs=0;
    for i=1:num_events,...
        event=T_start(i):T_end(i);
        plot_event(event,i,N,gdata);
        result=5;
        
        %% While User hasn't identified the event as a cough, not a cough,
        % or a secondary event
        while result ~= YES && result ~= NO && result ~= SECONDARY
            if result == SKIP;
                break;
            end;
            if result == REPLAYPREV && i-1 ~= 0
                close(i)
                plot_event2(event,T_start(i-1):T_end(i),i,N,gdata);
                soundsc(data(T_start(i-1):T_end(i)),fs);
            else
                soundsc(data(T_start(i):T_end(i)), fs);
            end
            result = input(prompt);
        end;
        
        %% Stop if user elected to skip the file
        if result == SKIP
            break;
        end;
        
        %% If the result is secondary
        if result == SECONDARY && coughs
            output(T_start(i-1):T_end(i))=1;
            output_times(coughs,2)=T_end(i);
        elseif result == YES    % For Primary Events
            coughs=coughs+1
            output(T_start(i):T_end(i))=result;
            output_times(coughs,:)=[T_start(i) T_end(i)];
        else
            continue;
        end
        % Close the figure displaying the cough
        close(i);
    end;
    %% Shorten output to number of coughs
    output_times=output_times(1:coughs,:);
    %% Plot results
    figure(1);
    plot(output);
    hold all
    plot(gdata);
    user_accepts=2;
    
    if result == SKIP || num_events == 0
        break;
    end;
    %% User may accept or not accept the file.  
    while user_accepts ~= YES && user_accepts ~= NO
        user_accepts=input(prompt_accept);
    end;
    notaccepted=~user_accepts;
    
end
%% Write the results if the user accepted them.
if result ~= SKIP || ~notaccepted
    for i=1:size(output_times,1);
        newfile=strrep(filename, '.wav', strcat(strcat('_',num2str(i,'%03i')),'.wav')); 
        audiowrite(newfile,data(output_times(i,1):output_times(i,2)), fs);
    end;
end;
end

function plot_event(event,i,N,gdata)
%% This function plots primary events
    plotsize=2000;                      % Limits number of samples
    interval=floor(N/plotsize);   % Calculate interval
    if interval < 1;
        interval=1;
    end;
    clf;
    figure(i);
    gevent=zeros(N,1);
    gevent(event)=1;
    area(gevent(1:interval:end),'FaceColor','Green');
    hold all;
    plot(gdata(1:interval:end),'Color','Black');
end

function plot_event2(event,event2,i,N,gdata)
%% This function plots secondary events along with primary events
        plotsize=2000;                      % Limits number of samples
        interval=floor(N/plotsize);   % Calculate interval
        if interval < 1;
            interval=1;
        end;clf;
        figure(i);
        gevent=zeros(N,1);
        gevent(event2)=1;
        area(gevent(1:interval:end),'FaceColor','Green');
        hold all;
        gevent=zeros(N,1);
        gevent(event)=1;
        area(gevent(1:interval:end),'FaceColor','Red');

        plot(gdata(1:interval:end),'Color','Black');
end