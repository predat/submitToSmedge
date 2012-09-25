import os, sys, subprocess, re

import c4d
from c4d import documents
from c4d import gui
from c4d import plugins


## The submission dialog class.
class SubmitC4DToSmedgeDialog(gui.GeDialog):
    SmedgeSubmitCommand = "/Applications/Smedge.app/Contents/MacOS/Submit"
    SmedgePoolManagerCommand = "/Applications/Smedge.app/Contents/MacOS/PoolManager"
    Pools = []
    
    LabelWidth = 200
    TextBoxWidth = 600
    ComboBoxWidth = 180
    RangeBoxWidth = 190
    
    SliderLabelWidth = 180
    
    LabelID = 1000
    NameBoxID = 10
    PoolBoxID = 40
    PriorityBoxID = 60
    WaitForBoxID = 80
    FramesBoxID = 100
    PacketBoxID = 120
    PausedBoxID = 140
    radioboxID = 160

    SubmitButtonID = 910
    CancelButtonID = 920
    
    def __init__(self):
        stdout = None
        self.Pools = []
        
        # Get the pools.
        try:
            print("Loading pools")
            stdout = os.popen(self.SmedgePoolManagerCommand + ' List')
            output = stdout.read()
            for line in output.splitlines():
                if len(line) != 0:
                    self.Pools.append( line.replace("\n","").split("\t")[1] )
        except:
            print( "Error getting pools from Deadline" )
        
        if len(self.Pools) == 0:
            self.Pools.append("Whole System")
    
    def GetLabelID(self):
        self.LabelID = self.LabelID + 1
        return self.LabelID
    
    def StartGroup(self, label):
        self.GroupBegin( self.GetLabelID(), 0, 0, 20, label, 0)
        self.GroupBorder(c4d.BORDER_THIN_IN)
        self.GroupBorderSpace(4, 4, 4, 4)
    
    def EndGroup(self):
        self.GroupEnd()
    
    def AddTextBoxGroup(self, id, label):
        self.GroupBegin( self.GetLabelID(), 0, 2, 1, "", 0 )
        self.AddStaticText( self.GetLabelID(), 0, self.LabelWidth, 0, label, 0 )
        self.AddEditText( id, 0, self.TextBoxWidth, 0 )
        self.GroupEnd()
    
    def AddComboBoxGroup( self, id, label, checkboxID=-1, checkboxLabel="" ):
        self.GroupBegin( self.GetLabelID(), 0, 3, 1, "", 0 )
        self.AddStaticText( self.GetLabelID(), 0, self.LabelWidth, 0, label, 0 )
        self.AddComboBox( id, 0, self.ComboBoxWidth, 0 )
        if checkboxID >= 0 and checkboxLabel != "":
            self.AddCheckbox( checkboxID, 0, self.LabelWidth + self.ComboBoxWidth + 12, 0, checkboxLabel )
        else:
            self.AddStaticText( self.GetLabelID(), 0, self.LabelWidth + self.ComboBoxWidth + 12, 0, "", 0 )
        self.GroupEnd()
    
    def AddRangeBoxGroup( self, id, label, min, max, inc, checkboxID=-1, checkboxLabel="" ):
        self.GroupBegin( self.GetLabelID(), 0, 3, 1, "", 0 )
        self.AddStaticText( self.GetLabelID(), 0, self.LabelWidth, 0, label, 0 )
        self.AddEditNumberArrows( id, 0, self.RangeBoxWidth, 0 )
        if checkboxID >= 0 and checkboxLabel != "":
            self.AddCheckbox( checkboxID, 0, self.LabelWidth + self.ComboBoxWidth + 12, 0, checkboxLabel )
        else:
            self.AddStaticText( self.GetLabelID(), 0, self.LabelWidth + self.RangeBoxWidth + 4, 0, "", 0 )
        self.SetLong( id, min, min, max, inc )
        self.GroupEnd()
    
    def AddSelectionBoxGroup( self, id, label, buttonID ):
        self.GroupBegin( self.GetLabelID(), 0, 3, 1, "", 0 )
        self.AddStaticText( self.GetLabelID(), 0, self.LabelWidth, 0, label, 0 )
        self.AddEditText( id, 0, self.TextBoxWidth - 56, 0 )
        self.AddButton( buttonID, 0, 8, 0, "..." )
        self.GroupEnd()
    
    def AddCheckboxGroup( self, checkboxID, checkboxLabel, textID, buttonID ):
        self.GroupBegin( self.GetLabelID(), 0, 3, 1, "", 0 )
        self.AddCheckbox( checkboxID, 0, self.LabelWidth, 0, checkboxLabel )
        self.AddEditText( textID, 0, self.TextBoxWidth - 56, 0 )
        self.AddButton( buttonID, 0, 8, 0, "..." )
        self.GroupEnd()
    
    def AddRadioGroup( self, radioboxID, radioLabel):
        self.GroupBegin( self.GetLabelID(), 0, 2, 1, "", 0)
        self.AddStaticText( radioboxID, 0, self.LabelWidth, 0, radioLabel)
        # TODO
        self.GroupEnd()

    ## This is called when the dialog is initialized.
    def CreateLayout(self):
        self.SetTitle( "Submit To Smedge")
        
        # General Options Tab
        #self.TabGroupBegin(self.GetLabelID(), 0)
        self.GroupBegin(self.GetLabelID(), 0, 0, 20, "General Options", 0)
        self.GroupBorderNoTitle(c4d.BORDER_NONE)
        
        self.StartGroup("Basic Job Info")
        self.AddTextBoxGroup(self.NameBoxID, "Name")
        self.AddRangeBoxGroup(self.PriorityBoxID, "Priority", 0, 100, 1)
        # Paused CheckBox
        # Processes RatioBox
        self.AddComboBoxGroup(self.PoolBoxID, "Pool")
        self.AddComboBoxGroup(self.WaitForBoxID, "Wait For")

        self.GroupBegin( self.GetLabelID(), 0, 2, 1, "", 0 )
        self.AddStaticText( self.GetLabelID(), 0, 0, 0, "Paused", 0 )
        self.AddCheckbox( self.PausedBoxID, 0, self.LabelWidth, 0, "")
        self.GroupEnd()

        self.EndGroup()
        
        self.StartGroup("Type Specific Parameters")
        self.AddTextBoxGroup(self.FramesBoxID, "Range to Process")
        self.AddTextBoxGroup(self.PacketBoxID, "Packet Size")
        self.EndGroup()
        
        self.GroupEnd() #General Options Tab
        #self.GroupEnd() #Tab group
        
        self.GroupBegin(self.GetLabelID(), 0, 2, 1, "", 0)
        self.AddButton(self.SubmitButtonID, 0, 100, 0, "Submit")
        self.AddButton(self.CancelButtonID, 0, 100, 0, "Cancel")
        self.GroupEnd()
        
        return True

    ## This is called after the dialog has been initialized.
    def InitValues(self):
        scene = documents.GetActiveDocument()
        sceneName = scene.GetDocumentName()
        sceneName = sceneName.split('.')[0]
        frameRate = scene.GetFps()
        
        startFrame = 0
        endFrame = 0
        stepFrame = 0
        
        renderData = scene.GetActiveRenderData().GetData()
        frameMode = renderData.GetLong(c4d.RDATA_FRAMESEQUENCE)
        if frameMode == c4d.RDATA_FRAMESEQUENCE_MANUAL:
            startFrame = renderData.GetTime( c4d.RDATA_FRAMEFROM ).GetFrame( frameRate )
            endFrame = renderData.GetTime( c4d.RDATA_FRAMETO ).GetFrame( frameRate )
            stepFrame = renderData.GetLong( c4d.RDATA_FRAMESTEP )
        elif frameMode == c4d.RDATA_FRAMESEQUENCE_CURRENTFRAME:
            startFrame = scene.GetTime().GetFrame( frameRate )
            endFrame = startFrame
            stepFrame = 1
        elif frameMode == c4d.RDATA_FRAMESEQUENCE_ALLFRAMES:
            startFrame = scene.GetMinTime().GetFrame( frameRate )
            endFrame = scene.GetMaxTime().GetFrame( frameRate )
            stepFrame = renderData.GetLong( c4d.RDATA_FRAMESTEP )
        elif frameMode == c4d.RDATA_FRAMESEQUENCE_PREVIEWRANGE:
            startFrame = scene.GetLoopMinTime().GetFrame( frameRate )
            endFrame = scene.GetLoopMaxTime().GetFrame( frameRate )
            stepFrame = renderData.GetLong( c4d.RDATA_FRAMESTEP )
        
        frameList = str(startFrame)
        if startFrame != endFrame:
            frameList = frameList + '-' + str(endFrame)
        # if stefFrame > 1:
        #    frameList = frameList + 'x' + str(stepFrame)
        
        initName = sceneName
        initPool = "Whole System"
        initPriority = 0
        
        initFrames = frameList
        initPacketSize = 10
        initThreads = 0
        
        # Populate the combox boxes
        selectedPoolID = 0
        for i in range(0, len(self.Pools)):
            self.AddChild(self.PoolBoxID, i, self.Pools[i])
            if initPool == self.Pools[i]:
                selectedPoolID = i
        
        self.SetString(self.NameBoxID, initName)
        self.SetLong(self.PoolBoxID, selectedPoolID)
        self.SetLong(self.PriorityBoxID, initPriority)
        self.SetString(self.FramesBoxID, initFrames)
        self.SetString(self.PacketBoxID, initPacketSize)
        
        return True
    
    ## This is called when a user clicks on a button or changes the value of a field.
    def Command(self, id, msg):
        if id == self.SubmitButtonID or id == self.CancelButtonID:
            jobName =  self.GetString(self.NameBoxID)
            pool = self.Pools[self.GetLong(self.PoolBoxID)]
            priority = self.GetLong(self.PriorityBoxID)
            frames = self.GetString(self.FramesBoxID)
            packetSize = self.GetLong(self.PacketBoxID)
        
            if id == self.SubmitButtonID:
                scene = documents.GetActiveDocument()
                sceneName = scene.GetDocumentName()
                sceneFilename = os.path.join(scene.GetDocumentPath(), sceneName)
                renderData = scene.GetActiveRenderData().GetData()
                
                saveOutput = renderData.GetBool(c4d.RDATA_SAVEIMAGE)
                outputPath = renderData.GetFilename(c4d.RDATA_PATH)
                outputFormat = renderData.GetLong(c4d.RDATA_FORMAT)
                outputName = renderData.GetLong(c4d.RDATA_NAMEFORMAT)
                
                saveMP = renderData.GetBool(c4d.RDATA_MULTIPASS_SAVEIMAGE)
                mpPath = renderData.GetFilename(c4d.RDATA_MULTIPASS_FILENAME)
                mpFormat = renderData.GetLong(c4d.RDATA_MULTIPASS_SAVEFORMAT)
                mpOneFile = renderData.GetBool(c4d.RDATA_MULTIPASS_SAVEONEFILE)
                
                width = renderData.GetLong(c4d.RDATA_XRES)
                height = renderData.GetLong(c4d.RDATA_YRES)
                
                # Submit the job to Smedge
                print("Submit Job")
                
                cmd  = self.SmedgeSubmitCommand
                cmd += " Script"
                cmd += " -Type Cinema 4D"
                cmd += " -Scene " + str(sceneFilename)
                cmd += " -Range " + str(frames)
                cmd += " -Name " + str(sceneName)
                cmd += " -PacketSize " + str(packetSize)
                cmd += " -Pool " + str(pool)
                #cmd += " -CPUs 4"
                #cmd += " -Paused"
                
                print(cmd)
                #subprocess.call(cmd)
            self.Close()
        return True


## Class to create the submission menu item in C4D.
class SubmitC4DtoSmedgeMenu (plugins.CommandData):
    ScriptPath = ""
    
    def __init__( self, path ):
        self.ScriptPath = path
    
    def Execute(self,doc):
        if SaveScene():
            dialog = SubmitC4DToSmedgeDialog()
            dialog.Open(c4d.DLG_TYPE_MODAL)
        return True
    
    def GetScriptName(self):
        return "Submit To Smedge"



## Global function to save the scene. Returns True if the scene has been saved and it's OK to continue.
def SaveScene():
    scene = documents.GetActiveDocument()
    
    # Save the scene if required
    if scene.GetDocumentPath() == "" or scene.GetChanged():
        print("Scene file needs to be saved")
        c4d.CallCommand(12098) # this is the ID for the Save command (from Command Manager)
        if scene.GetDocumentPath() == "":
            gui.MessageDialog("The scene must saved before it can be submitted to Smedge")
            return False
    return True



## Global function used to register our submission script as a plugin.
def main(path):
    pluginID = 21434523
    plugins.RegisterCommandPlugin(pluginID, "Submit to Smedge", 0, None, "Submit a Cinema 4D job to Smedge", SubmitC4DtoSmedgeMenu(path))



## For debugging.
if __name__ == '__main__':
    if SaveScene():
        dialog = SubmitC4DToSmedgeDialog()
        dialog.Open(c4d.DLG_TYPE_MODAL)
