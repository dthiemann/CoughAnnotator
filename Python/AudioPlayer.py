'''

Author: Dylan Thiemann
Group: University of Iowa Computational Epidemiology Group
Most Recent Update: 2/11/14

This program is an audio player that allows the user to analyze the number of events (coughs) in that file.
The audio player displays a window that will show all events in the given audio file
and allow the user to click where he/she wants to start listening. It also
allows the user to skip areas where no events take place

'''


import wx, wx.media, wx.lib
import sys
import wave
import struct
import wx.lib.scrolledpanel as scrolled

class AudioPlayer(wx.Frame):
    
    def __init__(self,parent,title):
        super(AudioPlayer, self).__init__(parent, title=title, size=(705, 550))
        
        self.UI()
        
        self.Centre()
        self.Show()

        
    def UI(self):
        
        #Queue for choosing which audio file to analyze
        self.queue = []
        #Dictionary used in order to switch out analysis between different sets of data
        #Key = audio file name
        #Value = [file location, event list]
        self.audioDataInQueue = {}
        
        self.audioFile = None
        self.eventData = None
        self.panel = wx.Panel(self)
        
        #Sizers for the buttons and windows in the main view
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        
        #Create all the buttons needed for proper functionality
        playButton = wx.Button(self.panel, label = "Play", size = (70,30))
        playButton.Bind(wx.EVT_BUTTON,self.play)
        self.hbox1.Add(playButton, border = 1, flag = wx.ALL)
        
        stopButton = wx.Button(self.panel, label = "Stop", size = (70,30))
        stopButton.Bind(wx.EVT_BUTTON, self.stop)
        self.hbox1.Add(stopButton, border = 1, flag = wx.ALL)
        
        pauseButton = wx.Button(self.panel, label = "Pause", size = (70,30))
        pauseButton.Bind(wx.EVT_BUTTON,self.pause)
        self.hbox1.Add(pauseButton, border = 1, flag = wx.ALL)
        
        loadDataButton = wx.Button(self.panel, label = "Load Event Data", size = (120,30))
        loadDataButton.Bind(wx.EVT_BUTTON,self.loadEvents)
        self.hbox1.Add(loadDataButton, border = 1, flag = wx.ALL)
        
        loadAudioButton = wx.Button(self.panel, label = "Load Audio File", size = (120,30))
        loadAudioButton.Bind(wx.EVT_BUTTON,self.loadData)
        self.hbox1.Add(loadAudioButton, border = 1, flag = wx.ALL)
        
        publishButton = wx.Button(self.panel, label = "Publish", size = (80,30))
        publishButton.Bind(wx.EVT_BUTTON,self.publishAndDelete)
        self.hbox1.Add(publishButton, border = 1 , flag = wx.ALL)
        
        exitButton = wx.Button(self.panel,label = "Exit", size = (60,30))
        exitButton.Bind(wx.EVT_BUTTON,self.exitApp)
        self.hbox1.Add(exitButton, border = 1, flag = wx.ALL)
    
        #Inititialization of labesl and buttons for cough counting
        labelSize = wx.Size(60,30)
        self.decrement = wx.Button(self.panel,label = "<--", size = (60,30))
        self.decrement.Bind(wx.EVT_BUTTON,self.onDecrement)
        self.titleLabel = wx.StaticText(self.panel, label = "Number of coughs = ", style = wx.ALIGN_CENTRE)
        self.numCoughs = 0
        self.label = wx.StaticText(self.panel, label = str(self.numCoughs), size = labelSize, style = wx.ALIGN_CENTRE)
        self.increment = wx.Button(self.panel, label = "-->", size = (60,30))
        self.increment.Bind(wx.EVT_BUTTON,self.onIncrement)
        
        #Arrow key events for keeping track of number of coughs
        incUp = wx.NewId()
        incRight = wx.NewId()
        decDown = wx.NewId()
        decLeft = wx.NewId()
        self.Bind(wx.EVT_MENU,self.onIncrement, id = incUp)
        self.Bind(wx.EVT_MENU,self.onIncrement, id = incRight)
        self.Bind(wx.EVT_MENU,self.onDecrement, id = decDown)
        self.Bind(wx.EVT_MENU,self.onDecrement, id = decLeft)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_UP, incUp),
                                        (wx.ACCEL_NORMAL, wx.WXK_RIGHT, incRight),
                                        (wx.ACCEL_NORMAL, wx.WXK_DOWN, decDown),
                                        (wx.ACCEL_NORMAL, wx.WXK_LEFT, decLeft)
                                        ])                                          #Accelerator used to bind keys to the increment and decrement keys
        self.SetAcceleratorTable(accel_tbl)
        
        #drop down box that allows the user to 
        #choose which audio file they want to analyze (not functional at the moment)
        self.dropDownBox = wx.ComboBox(self.panel, -1, "Audio File", (15, 200), wx.DefaultSize, self.queue, wx.CB_READONLY) #wx.DefaultSize
        self.dropDownBox.SetEditable(False)
        self.Bind(wx.EVT_COMBOBOX,self.onDropDownSelect)

        self.vbox.Add(self.hbox1, proportion = 0)
        
        #Layout of the lables used to count the coughs
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.titleLabel, border = 1, flag = wx.ALL)
        self.hbox2.Add(self.label, border = 1, flag = wx.ALL)
        self.hbox2.Add(self.dropDownBox, border = 3, flag = wx.LEFT)
        #self.hbox2.Add(self.queue, border = 1, flag = wx.ALL)
        self.vbox.Add(self.hbox2, proportion = 0)
        
        #Layout for the dec and inc buttons
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3.Add(self.decrement, border = 1, flag = wx.ALL)
        self.hbox3.Add(self.increment, border = 1, flag = wx.ALL)
        self.vbox.Add(self.hbox3, proportion = 0)
        
        self.panel.SetSizer(self.vbox)
        self.Layout()
        #END OF LAYOUT MANAGEMENT
        
        self.player = wx.media.MediaCtrl(parent = self.panel, szBackend=wx.media.MEDIABACKEND_QUICKTIME) #Initialize the audio player (Be sure to change szBackend for different OS)
        
        #List used to store all events recorded by the user
        self.eventsToPublish = []
        
    def onIncrement(self, evt):
        #Increments the cough counter
        self.numCoughs += 1 
        self.label.SetLabel(str(self.numCoughs))
        
        #Find which event marker is the cough and stores it in a new DS --> Will be used for publishing later
        eventTime = (self.player.Tell()/1000.0)*self.audioFrameRate
        index = -1
        print eventTime
        for x in self.eventList:
            if x >= eventTime:
                index = self.eventList.index(x)
                index -= 1
                break
        self.eventsToPublish.append([self.eventList[index],self.eventLength[index]])
        
    def onDecrement(self, evt):
        #Decrements the cough counter
        if not (self.numCoughs < 1): #Do not decrement if we have less than 1 cough, we can't have negative coughs
            self.numCoughs -= 1
            self.label.SetLabel(str(self.numCoughs))
            del self.eventsToPublish[-1]

    def OnTimer(self,evt):
        #Happens everytime the timer hits the its designated mark (depends on what its set at)
        VS = self.eventWindow.GetVirtualSize()              #How large the scrolled window is (very large sometimes)
        maxScroll = VS[0] - 700                             #Subtract 700 (the length of the visible window (don't want to scroll if we already have everything in view)
        viewStart = self.eventWindow.GetViewStart()         #Get the x-value of virtual size window from where the window begins on the left side
        if viewStart[0] < maxScroll - 13:                   #11 is the amount we are scrolling, while we are still able to scroll
            self.eventWindow.Scroll((viewStart[0] + 13,0))  #Scroll the window by 11 pixels (any smaller results in lag)
        elif viewStart[0] < maxScroll:                      #If we are inbetween maxScroll and maxScroll -11, we scroll by the difference between maxScroll and where we are
            self.eventWindow.Scroll((viewStart[0] + (maxScroll - viewStart[0]),0))
        
    def exitApp(self,evt):
        self.Close()
        #sys.exit()
    
    def loadData(self,evt):
        #load in the audio file
        self.audioFile = wx.FileSelector("Choose a file you would like to analyze")
        #self.audioFile = "/Users/uicsi/Desktop/Dylan_back_up/Developer/Python/compEpi/audio_test1.wav"
        audio = wave.open(self.audioFile)
        self.audioFrameRate = audio.getframerate()
        audioFrames = audio.getnframes()        
        self.duration = float(audioFrames)/self.audioFrameRate
        print(self.audioFrameRate, self.duration, audioFrames)
        print "frame rate", "duration", "audio Frames"
        self.audioFileSize = audioFrames 
    
        coughAudioFile = wx.media.MediaCtrl(self.panel)                     #initialize the audio player for this class
        
        #Place the audio file in the queue so its ready to play
        self.player.Load(self.audioFile)
        
        audioNameList = self.audioFile.split("/")
        self.queue.append(str(audioNameList[-1]))
        self.dropDownBox.Append(str(audioNameList[-1]))
        self.dropDownBox.SetStringSelection(str(audioNameList[-1]))
        self.audioDataInQueue[str(audioNameList[-1])] = [self.audioFile,self.audioFileSize]
        
    def loadEvents(self,evt):
        
        #if the audio file has not been loaded yet... throws an Alert and prompts the user to select an audio file
        if not self.audioFile: 
            wx.MessageBox('You need to select an audio file before you select an event file', 'Alert!', wx.OK | wx.ICON_INFORMATION)
            self.loadData(evt)
            wx.MessageBox('Now you can select your event file for ' + self.audioFile + '.', 'Continue', wx.OK | wx.ICON_INFORMATION)
        
        #Asks the user to input a event file
        self.eventData = wx.FileSelector("Choose the event data for the audio data") 
        #self.eventData = "/Users/uicsi/Desktop/Dylan_back_up/Developer/Python/compEpi/eventFile.txt"
        eventFile = open(self.eventData)                                    #Open the file of events --> May need to change format (ask Dylan)
        self.eventList = []
        self.eventLength = []
        #Add points where events are located
        for line in eventFile:
            lineList = line.split()
            self.eventList.append(int(lineList[1]))                         #Extract the locations from the file and store in its own data structure
            self.eventLength.append(int(lineList[3]))
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
        getFileName = self.audioFile.split("/")
        self.audioDataInQueue[str(getFileName[-1])].append(self.eventList)
        self.audioDataInQueue[str(getFileName[-1])].append(self.eventLength)
        #Create the scrollable window using the pre-made class
        self.eventWindow = EventWindow(self.panel, self.eventList, self.audioFileSize)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4.Add(self.eventWindow, border = 1, flag = wx.ALIGN_BOTTOM)
        self.eventWindow.Bind(wx.EVT_LEFT_DOWN,self.Seek)
        self.audioFile = None
        self.numCoughs = 0
        
        #Factor for seeking in a song
        self.eventSpacing = self.audioFileSize/1000
        self.multiplicationFactor = (self.player.Length()/self.eventSpacing) + 2
        print self.multiplicationFactor
    
    def Seek(self,evt):
        # ///// multiplication facter \\\\\\\
        # self.multiplicationFactor
        
        mousePos = evt.GetPosition()
        Position = self.eventWindow.getPosition(mousePos)       #Gets position in relation to the scrolled window
        #print self.player.Tell()
        if Position != None:
            #currentSize = self.eventWindow.GetViewStart()
            #print currentSize, "currentSize"
            #print self.player.Length(), "audio length ms"
            #print self.player.Length(), (self.player.Tell() + mousePos[0]*self.multiplicationFactor)
            incrementFactor = self.player.Tell() + mousePos[0]*self.multiplicationFactor
            if (incrementFactor <= self.player.Length()):
                x = self.player.Seek(incrementFactor)
                self.eventWindow.Scroll((Position[0],0))

        
    #These speak for themselves
    def play(self,evt):
        self.player.Play()
        self.timer.Start(300) 
    def pause(self,evt):
        self.player.Pause()
        self.timer.Stop()
    def stop(self,evt):
        self.player.Stop()
        self.eventWindow.Scroll((0,0))
        self.timer.Stop()
        
    #Called when an new item is selected from the drop down menu,
    #it updates the event window and reloads the audio player class
    #with the correct audio file
    def onDropDownSelect(self, evt):
        newAudioFile = self.dropDownBox.GetValue()
        self.player.Load(self.audioDataInQueue[str(newAudioFile)][0])
        self.eventWindow = EventWindow(self.panel, self.audioDataInQueue[str(newAudioFile)][2],self.audioDataInQueue[str(newAudioFile)][1])
        self.numCoughs = 0
        self.label.SetLabel(str(self.numCoughs))
        #NOTE: Add functionality that allows user to return to previous position (SAVE SCROLL POSITION)
        #NOTE: Add functionality that allows user to keep its numCoughs value (SAVE self.numCoughs in dictionary)
        
    #Takes the current audio file and publishes the label (number of coughs)
    #to a text file with the other audio files analyed during the same run
    #Outputs 1 file per audio file being analyzed
    def publishAndDelete(self, evt):

        #print len(self.audioDataInQueue)
        #print self.audioDataInQueue.keys()
        #print self.audioDataInQueue.keys()[0]
        #print self.audioDataInQueue.keys()[0].encode("ascii")
        if (len(self.audioDataInQueue) > 1):
            audioFileToWrite = self.dropDownBox.GetValue()
            audioFileNumCoughs = audioFileToWrite.rstrip(".wav")
            audioFileNumCoughs += "_number_of_coughs.txt"
            newFile = open(audioFileNumCoughs,"w")
            newFile.write(audioFileToWrite + " contains " + str(self.numCoughs) + " coughs")
            temp = self.audioDataInQueue.pop(str(audioFileToWrite))
            index = self.queue.index(audioFileToWrite)
            self.dropDownBox.SetStringSelection(self.queue[len(self.queue)-index-1])
            self.onDropDownSelect(evt)
            del self.queue[index]
            newFile.close()
        
        elif (len(self.audioDataInQueue.keys()) == 1):
            audioFileToWrite = self.dropDownBox.GetValue()
            audioFileNumCoughs = audioFileToWrite.rstrip(".wav")
            audioFileNumCoughs += ".anno"
            newFile = open(audioFileNumCoughs,"w")
            if self.eventsToPublish:
                for events in self.eventsToPublish:
                    newFile.write(str(events[0]) + "," + str(events[1]) + "\n")
            else:
                newFile.write("No coughs")
            newFile.close()
            self.Close()
        else:
            print("No files in queue, nothing to publish")
        '''
        elif (len(self.audioDataInQueue.keys()) == 1):
            audioFileToWrite = self.dropDownBox.GetValue()
            audioFileNumCoughs = audioFileToWrite.rstrip(".wav")
            audioFileNumCoughs += "_number_of_coughs.txt"
            newFile = open(audioFileNumCoughs,"w")
            newFile.write(audioFileToWrite + " contains " + str(self.numCoughs) + " coughs")
            newFile.close()
            self.Close()
        '''
 
class EventWindow(wx.ScrolledWindow):
    def __init__(self,parent, ListOfEvents,audioSize):
        #Initialize the scrollable window, it scrolls horizontally, is 700p wide and 200p tall
        super(EventWindow, self).__init__(parent = parent, style= wx.HSCROLL,name = 'Event GUI',size = (700,400) , pos = (0,120))

        self.EnableScrolling(True,True) #Allow scrolling
        self.EventList = ListOfEvents #Contains all the events which we need to display
        self.size = audioSize
        
        self.GUI()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        #if len(queue) == 1:
            #self.queueBox = wx.TextCtrl(parent = self, id = -1, size = (200,80), pos = (350,20), style = wx.TE_READONLY)
            #self.queueBox.AppendText(queue[0])
            #self.queueBox.AppendText("" + "\n")
        #else:
            #self.queueBox = wx.TextCtrl(parent = self, id = -1, size = (200,80), pos = (0,420), style = wx.TE_READONLY)
            #for fileName in queue:
                #self.queueBox.AppendText(fileName + "\n")            
        #self.Bind(wx.EVT_SCROLLWIN,self.OnPaint1) #Called when we scroll on this window
        
    def GUI(self):
        #Use scrolled panel
        self.SetBackgroundColour((255,228,196))                           #Choose an arbitrairy background color
        eventSpacing = self.size/1000                                   #Divide by 1000 to make the spaces between events smaller (so we can seen the data better)
        #print self.size, "size"
        #print eventSpacing, "event spacing"
        self.SetScrollbars(1, 1, eventSpacing, 400, 0,0, False)         #Set the scrollbars on the window
        self.buffer = wx.EmptyBitmap(eventSpacing,400)                  #Used for drawing the events
        
        #Creates the list of events in proper drawing format (x1,y1,x2,y2)
        self.LinesList = []
        for lines in self.EventList:
            self.LinesList.append((lines/1000, 0, lines/1000, 400))
    
     #USELESS FUNCTION (DOESN'T SEEM TO GET CALLLED AT ALL)
    #OnPaint1 is called on any scroll event of the scrollable window
    def OnPaint1(self,evt):
        #Handles all the scrol events
        self.ScrollPos = evt.GetPosition() #Gets the scroll position
        cdc = wx.BufferedPaintDC(self)
        dc = wx.BufferedDC(cdc, self.buffer) #Buffer allows for a smooth scrolling without flickering
        self.PrepareDC(cdc)
        cdc.DrawLineList(self.LinesList) #Takes all the events and draws them via one function    
    
    #OnPaint is called on an EVT_PAINT event, usually only called once (when scrolledwindow is initiated)
    def OnPaint(self,evt):                                              #Draws the initial set of lines
        cdc = wx.PaintDC(self)                                          #wx.BufferedPaintDC(self)
        self.ScrollPos = 0
        self.PrepareDC(cdc)
        dc = wx.BufferedDC(cdc, self.buffer)                            #Creates the drawable device content on self.buffer (a bitmap) 
        cdc.DrawLineList(self.LinesList)                                #Draws events by using a series of 4 memmber tuples in a list
    
    #This function takes as input a mouse pointer position and returns, if applicable, the virtual position of the mouse pointer with regards the the scrolled window
    def getPosition(self,position):
        self.ScrollPos = self.GetViewStart()[0]
        if (position[0] <= 700 and position[0] >= 0) and (position[1] <= 400 and position[1] >= 0):     #Makes sure mouse is located within the event window
            return (position[0] + self.ScrollPos, position[1])
        else:
            return None
        
        

if __name__ == '__main__':
    app = wx.App()
    AudioPlayer(None, title='Cough Detector')
    app.MainLoop()
