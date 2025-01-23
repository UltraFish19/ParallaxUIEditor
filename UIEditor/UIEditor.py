import tkinter as UI
from tkinter import *
from tkinter import ttk as UUI # Updated UI
from tkinter import messagebox
from tkinter.colorchooser import askcolor
from tkinter.simpledialog import askstring
from tkinter import filedialog as FileDialog
import copy
from Utils import *
import json as Json
import os



Editor = UI.Tk()
Editor.geometry("1000x600")
Editor.resizable(False, False)
Editor.iconbitmap(R"Icon.ico")

#--------------------------<Vars>---------------------------------

DefaultColor = "#F0F0F0" # Default tkinter color

RootName : str = "Unnamed Application"
ResizeX : bool = False
ResizeY : bool = False
GeometryX : int = 300
GeometryY : int = 400
RootColor : str = DefaultColor #Default color




Editor.title(f"Parallax UI Designer | {RootName}")



PreviewRoot : UI.Tk = None
LiveEditorRoot : UI.Tk = None
CodeRoot : UI.Tk = None






Widgets : list[EditorWidget] = [] # Widgets in application

SelectedWidget : EditorWidget = None # Represents the Widget selected to be edited
SelectedWidgetLeaf : str = "" # Represents the Widget selected Treeview ID


# Determines the Save file version. Since the save file and format are set to change.
Version = "1"
SupportedVersions = ["1"] 
SupportedWidgets = ["Label","Entry","Button"]

#--------------------------<TKVars>---------------------------------

RootNameVar = UI.StringVar(value=RootName) #Stores name of application
ResizeXVar = UI.BooleanVar(value=ResizeX) #Store whether to resize x
ResizeYVar = UI.BooleanVar(value=ResizeY) #Store whether to resize y
GeometryXVar = UI.StringVar(value=GeometryX) #Stores apps X geometry
GeometryYVar = UI.StringVar(value=GeometryY) #Stores apps Y geometry

PropNameVar = UI.StringVar() #Stores widget name

PropTextVar = UI.StringVar() #Stores widget text


PropTextSizeVar = UI.StringVar()
PropPosXVar = UI.StringVar()
PropPosYVar = UI.StringVar()

CodeEnabled = False
CodeEnabledVar = UI.BooleanVar(value=CodeEnabled) #Stores whether live code is

LiveEditorEnabled = False
LiveEditorEnabledVar = UI.BooleanVar(value=LiveEditorEnabled) #Stores whether live editor is

Snapping = 10
SmartSnapping = False

FontSizeChange = 5



#--------------------------<Functions>-------------------------------






def SetWidgetProperty(): # Set widget properties on SelectedWidget
    SelectedWidget.Text = PropTextVar.get()
    SelectedWidget.BG = BackgroundPicker.cget("background")
    SelectedWidget.FG = ForegroundPicker.cget("background")
    
    try:
        SelectedWidget.TextSize = Clamp(0,int(PropTextSizeVar.get()),100)
    except: pass
    
    try:
        SelectedWidget.PosX = Clamp(0,int(PropPosXVar.get()),10000)
    except: pass
    
    try:
        SelectedWidget.PosY = Clamp(0,int(PropPosYVar.get()),10000)
    except: pass
    

    if CheckWidgetVarName(PropNameVar.get()) == True:
        SelectedWidget.Name = PropNameVar.get()
    else:
        messagebox.showerror("Invalid name","Name has not been changed, lease set name to a valid Python variable name and should not start with a number or have spaces!")
        PropNameVar.set(SelectedWidget.Name)

    CheckNameDuplicate(SelectedWidget)

    ItemHierarchy.item(SelectedWidgetLeaf,text=SelectedWidget.Name) #Change name on treeview
    UpdateLiveEditor()





def CheckNameDuplicate(Check : EditorWidget): #Checks and changes a name if it is a duplicate. This doesn't work super well at making nice looking games. But it does "encourage" the user to rename
    for ToCompare in Widgets:
        if Check.Name == ToCompare.Name and Check.ID != ToCompare.ID:
            LastCharacter = Check.Name[len(Check.Name) - 1]
            
            try:
                LastCharacterNumber = int(LastCharacter)
            except:
                LastCharacterNumber = None


            if LastCharacterNumber:
                Check.Name = Check.Name[:-1] + str(LastCharacterNumber + 1)
            else:
                Check.Name = Check.Name + "1"

            CheckNameDuplicate(Check) # Checks again if the name is still a duplicate






def SetRoot():
    global RootName,ResizeX,ResizeY,GeometryX,GeometryY, RootColor,RootColorPicker
    RootName = RootNameVar.get()

    ResizeX = ResizeXVar.get()
    ResizeY = ResizeYVar.get() 
    
    RootColor = RootColorPicker.cget("background")
    

    try:
        GeometryX = Clamp(1,int(GeometryXVar.get()),2000)
        GeometryY = Clamp(1,int(GeometryYVar.get()),2000)
    except: pass
        


    GeometryXVar.set(str(GeometryX))
    GeometryYVar.set(str(GeometryY))



    Editor.title(f"Parallax UI Editor™ | {RootName}")
    messagebox.showinfo("Info","Successfully set root")
    UpdateLiveEditor()






def ShowContextMenu(Event): # Show Context Menu 
    try:
        ContextMenu.tk_popup(Event.x_root, Event.y_root)
    finally:
        ContextMenu.grab_release
        
    




def SetSelectedWidget(_): #Responsible for setting SelectedWidget and SelectedWidgetLeaf, Event is unused but i'm forced to put it there
    global SelectedWidget, SelectedWidgetLeaf
    if len(ItemHierarchy.selection()) != 0: #Check if selected is not empty
        Leaf = ItemHierarchy.selection()[0]

        for ToSet in Widgets:
            if ToSet.ID == Leaf:
                SelectedWidgetLeaf = Leaf
                SelectedWidget = ToSet
                DisablePropertyTab(False)
                FillWidgetProperties()
            
            


def FillWidgetProperties (): #Fill the Wigget property window with the selected widgets values
    
    PropTextVar.set(SelectedWidget.Text)
    PropNameVar.set(SelectedWidget.Name)
    BackgroundPicker.config(background=SelectedWidget.BG)
    ForegroundPicker.config(background=SelectedWidget.FG)
    PropTextSizeVar.set(SelectedWidget.TextSize)
    
    PropPosXVar.set(SelectedWidget.PosX)
    PropPosYVar.set(SelectedWidget.PosY)



def ChangeText(Event : UI.Event): # When right clicking a widget, change its text
    ChangedWidget = Event.widget
    Properties : EditorWidget = ChangedWidget.EditorWidget

    EnteredName = askstring(f'Changing "{Properties.Name}"',f'You are planning to change the text of "{Properties.Text}" to:')
    if EnteredName:
        Properties.Text = EnteredName
        UpdateLiveEditor()
        FillWidgetProperties()





def Drag(Event : UI.Event):

    global SmartSnapping, Snapping,LiveEditorRoot, SelectedWidget, SelectedWidgetLeaf

    Properties : EditorWidget = Event.widget.EditorWidget

    if LiveEditorRoot != None:
        NewX = RoundUp(Event.x_root - LiveEditorRoot.winfo_rootx(),Snapping)
        NewY = RoundUp(Event.y_root - LiveEditorRoot.winfo_rooty(),Snapping)
        Properties.PosX = NewX
        Properties.PosY = NewY
        Event.widget.place(x=NewX, y=NewY,anchor=UI.CENTER)

        if SelectedWidget != Properties and SelectedWidgetLeaf != Properties.ID:
            ItemHierarchy.selection_set((Properties.ID))
            SetSelectedWidget(None)

        FillWidgetProperties()



def ChangeTextSize(Event : UI.Event): # Runs when someone scrolls in the Live Editor on a widget
    ChangedWidget = Event.widget
    
    Properties : EditorWidget = ChangedWidget.EditorWidget
    ChangeBy = FontSizeChange

    if Event.delta < 0:
        ChangeBy = FontSizeChange * -1

    if SelectedWidget != Properties and SelectedWidgetLeaf != Properties.ID:
        ItemHierarchy.selection_set((Properties.ID))
        SetSelectedWidget(None)

    FillWidgetProperties()
  
    Properties.TextSize = Clamp(4,Properties.TextSize + ChangeBy,100)
    ChangedWidget.config(font=("Arial", Properties.TextSize))
    



def MoveWidget(Up : bool): # Moves the widget somewhere on the Hierarchy


    global SelectedWidget, SelectedWidgetLeaf
    
    if len(ItemHierarchy.selection()) != 0 and SelectedWidget: #Check if selected is not empty and SelectedWidget registered
        WidgetSelected = ItemHierarchy.selection()[0]
        ItemHierarchy.move(WidgetSelected,parent=ItemHierarchy.parent(WidgetSelected),index=ItemHierarchy.index(WidgetSelected) + (-1 if Up else 1))
        


            
        Index = Widgets.index(SelectedWidget)
        Widgets.pop(Index)
        Widgets.insert(Index + (-1 if Up else 1),SelectedWidget)
        UpdateLiveEditor()




def ResetPropTab(): # Resets the property tab
    PropTextVar.set("")
    PropNameVar.set("")






def DeleteWidget(): #Delete Widgets
    global SelectedWidget, SelectedWidgetLeaf
    if len(ItemHierarchy.selection()) != 0 and SelectedWidgetLeaf and SelectedWidget: #Check if selected is not empty and if Selected Widget is registered

        
        
        ResetPropTab()
        DisablePropertyTab(True)


        Widgets.remove(SelectedWidget)
        SelectedWidget = None
        ItemHierarchy.delete(SelectedWidgetLeaf)
        SelectedWidgetLeaf = ""
        UpdateLiveEditor()




def DuplicateWidget(): #Duplicate Selected Widget
    global SelectedWidget, SelectedWidgetLeaf
    
    if len(ItemHierarchy.selection()) != 0 and SelectedWidget: #Check if selected is not empty and if SelectedWidget exists     

        Duplicate = copy.deepcopy(SelectedWidget) # Copys the object
        Widgets.append(Duplicate)
        Duplicate.ID = "" # Makes the ID blank so it goes through the CheckNameDuplicate
        CheckNameDuplicate(Duplicate)
        WidgetID = ItemHierarchy.insert("",UI.END,text=Duplicate.Name,values=(Duplicate.Type))
        Duplicate.ID = WidgetID
        UpdateLiveEditor()
        




def CreateWidget(Type): # Create widget
    global EditorWidget
    EditWidget =  EditorWidget(Type)
    CheckNameDuplicate(EditWidget)
    Widgets.append(EditWidget)
    EditWidget.ID =  ItemHierarchy.insert("",UI.END,text=EditWidget.Name,values=(EditWidget.Type)) # Returns ID and inserts widget into hierarchy

    try: # Not taking chances
        UpdateLiveEditor()
    except: pass
    
    return EditWidget


def DisablePropertyTab(SetTo : bool): #Disable or enable Property tab
    global PropertyFrame
    for Child in PropertyFrame.winfo_children():
        
        if SetTo == True and Child.cget("text") != "Widget Properties":  #Avoid disabling Widget Properties text and greying it out
            Child.config(state="disabled")
        else:
            Child.config(state="normal")
            



def GetColor(Self : Button): #Add this function to a button to make it behave like a color picker. Self is the Widget that this function was called from
    Color = askcolor(Self.cget("background"),title="Pick a color default color is RGB(240, 240, 240) Hex(#f0f0f0)")[1]
    if Color:
        Self.config(background=Color)

        

def GenerateWidgetsForPreview(Master,ForLiveEditor : bool): # Generates widgets for Preview, Live Editor and Update Live Editor
    for ToAdd in Widgets:
        PreviewedWidget : UI.Widget
        if ToAdd.Type == "Label":
            PreviewedWidget = UI.Label(Master,text=ToAdd.Text,font=(None,ToAdd.TextSize),foreground=ToAdd.FG,background=ToAdd.BG)
        elif ToAdd.Type == "Button":
            PreviewedWidget = UI.Button(Master,text=ToAdd.Text,font=(None,ToAdd.TextSize),foreground=ToAdd.FG,background=ToAdd.BG)
        elif ToAdd.Type == "Entry":
            PreviewedWidget = UI.Entry(Master,font=(None,ToAdd.TextSize),foreground=ToAdd.FG,background=ToAdd.BG)

        PreviewedWidget.place(x=ToAdd.PosX,y=ToAdd.PosY,anchor=UI.CENTER)
        if ForLiveEditor == True:
                setattr(PreviewedWidget,"EditorWidget",ToAdd)
                PreviewedWidget.bind("<B1-Motion>",Drag)
                PreviewedWidget.bind("<MouseWheel>",ChangeTextSize)
                PreviewedWidget.bind("<Button-3>",ChangeText)


def ExportPYFile():
    Code = GenerateCode()

    SaveLocation = FileDialog.asksaveasfilename(defaultextension=".py",filetypes=[("Python Source Code","*.py")])
    if SaveLocation != "":
        SaveFile = open(SaveLocation,"x")
        SaveFile.write(Code)
        SaveFile.close()


def SaveProject(): #Saves the project
    RootData = {}
    DecodedData = []
    EncodedData = ""

    RootData["ProjectName"] = RootName
    RootData["RootSizeX"] = GeometryX
    RootData["RootSizeY"] = GeometryY
    RootData["BG"] = RootColor
    RootData["Version"] = Version
    DecodedData.append(RootData)

    for ToSave in Widgets:
        DecodedData.append(ToSave.Save())


    try:
        EncodedData = Json.dumps(DecodedData,indent=1)
    except:
        messagebox.showerror("Error trying to save!","Unable to parse data!")
        return
    
    SaveLocation = FileDialog.asksaveasfilename(defaultextension=".pxu",filetypes=[("Parallax UI Project","*.pxu*")])

    try:
        if SaveLocation != "":

            if os.path.exists(SaveLocation) == False:
                SaveFile = open(SaveLocation,"x")
                SaveFile.write(EncodedData)
                SaveFile.close()
            else:
                SaveFile = open(SaveLocation,"w")
                SaveFile.write(EncodedData)
                SaveFile.close()
    except:
        messagebox.showerror("Error trying to save!","Error when trying to save file!")




LoadError = "Unable to load file"

def LoadProject():
    global RootName,RootNameVar, RootColor, GeometryX, GeometryXVar, GeometryY, GeometryYVar, Widgets

    LoadLocation = FileDialog.askopenfilename(defaultextension=".pxu",filetypes=[("Parallax UI Project","*.pxu*")])

    if LoadLocation != "":
        LoadFile = open(LoadLocation,mode="r")

        EncodedData = LoadFile.read()

        DecodedData : list[str] = []

        RootData : dict = {}


        LoadFile.close()

        try:
            DecodedData = Json.loads(EncodedData)
        except:
            messagebox.showerror(LoadError,"Malformed file!")
            return
        
        try:
            RootData = DecodedData[0]
            DecodedData.pop(0)
        except:
            messagebox.showerror(LoadError,"There's a problem with the save file!")
            return

        try:
            if  not RootData["Version"] in SupportedVersions:
                messagebox.showerror(LoadError,"Version not supported!")
                return
            else:
                RootData["Version"] = None
        except:
                messagebox.showerror(LoadError,"Version invalid!")
                return
        

        try: # Add name to root
            RootName = str(RootData["ProjectName"])
        except: pass

        try:
            GeometryX = int(RootData["RootSizeX"])
            GeometryY = int(RootData["RootSizeY"])
        except: pass

        try:
            RootColorPicker.config(background = str(RootData["BG"]))
            RootColor = RootColorPicker.cget("background")
        except: pass


        RootNameVar.set(RootName)
        GeometryXVar.set(GeometryX)
        GeometryYVar.set(GeometryY)

        Editor.title(f"Parallax UI Editor™ | {RootName}")

    Widgets.clear()
    ItemHierarchy.delete(*ItemHierarchy.get_children())

    for ToAdd in DecodedData:
        try:    
            if ToAdd["Type"] in SupportedWidgets:
                AddedWidget = CreateWidget(ToAdd["Type"])
                AddedWidget.Name = str(ToAdd["Name"])   
                AddedWidget.Text = str(ToAdd["Text"])
                AddedWidget.FG = str(ToAdd["FG"])
                AddedWidget.BG = str(ToAdd["BG"])
                AddedWidget.PosX = int(ToAdd["PosX"])
                AddedWidget.PosY = int(ToAdd["PosY"])
                AddedWidget.TextSize = int(ToAdd["TextSize"])
                ItemHierarchy.item(AddedWidget.ID,text = AddedWidget.Name)
            else:
                messagebox.showerror(LoadError,"Error with widget type!")
                return
        except:
            messagebox.showerror(LoadError,"Error with loading widgets!")
            return

    UpdateLiveEditor()


            



def PreviewUI(): #IMPORTANT
    global PreviewRoot, Editor
    try:
        PreviewRoot.destroy()
    except: pass




    PreviewRoot = UI.Toplevel(Editor)
    PreviewRoot.title(RootName)
    PreviewRoot.geometry(f"{GeometryX}x{GeometryY}")
    PreviewRoot.resizable(ResizeX,ResizeY)
    PreviewRoot.config(background=RootColor)
    
    GenerateWidgetsForPreview(PreviewRoot,False)




        
        
        
    PreviewRoot.mainloop()



def ChangeRootWindowSizeViaLiveEditor(Event : UI.Event): # Only used once 
    global GeometryX, GeometryY, GeometryXVar, GeometryYVar

    GeometryX = RoundUp(LiveEditorRoot.winfo_width(),Snapping)
    GeometryXVar.set(GeometryX)

    GeometryY = RoundUp(LiveEditorRoot.winfo_height(),Snapping)
    GeometryYVar.set(GeometryY)

    LiveEditorRoot.config(width=GeometryX,height=GeometryY)
    CodeViewUI()
    


def LiveEditorUI(): 
        global LiveEditorRoot, LiveEditorEnabled

        LiveEditorEnabled = LiveEditorEnabledVar.get()

        if LiveEditorEnabled == True:
            try:
                LiveEditorRoot.destroy()
            except: pass

        



            LiveEditorRoot = UI.Toplevel(Editor,background=RootColor)
            LiveEditorRoot.protocol("WM_DELETE_WINDOW",CloseLiveEditor)
            LiveEditorRoot.title("Edit UI Elements and Root Geometry")
            LiveEditorRoot.iconbitmap("Move.ico")
            LiveEditorRoot.geometry(f"{GeometryX}x{GeometryY}")
            LiveEditorRoot.bind("<Configure>",ChangeRootWindowSizeViaLiveEditor)


            GenerateWidgetsForPreview(LiveEditorRoot,True)

                
        

                
            LiveEditorRoot.mainloop()
        else:
            try:
                LiveEditorRoot.destroy()
            except: pass


def CloseLiveEditor():
    global LiveEditorEnabled
    LiveEditorEnabledVar.set(False)
    LiveEditorEnabled = False
    LiveEditorRoot.destroy()

def UpdateLiveEditor():
    CodeViewUI() # Update the code view UI to reflect the changes made in the live editor

    if LiveEditorRoot:
        LiveEditorRoot.config(background=RootColor)
        for ToDelete in LiveEditorRoot.winfo_children():
            ToDelete.destroy()

        GenerateWidgetsForPreview(LiveEditorRoot,True)




def GenerateCode() -> str: # Generates a code 
    EssentialPart = f"""  
# Created with Parallax UI Editor


import tkinter as UI


Root = UI.Tk() # Create the main root

Root.title("{RootName}")

Root.config(background = "{RootColor}") # SystemButtonFace is the default color of the root window

Root.geometry("{GeometryX}x{GeometryY}") # Set Root Geometry

Root.resizable({ResizeX}, {ResizeY})

#---------------------------------<Widgets>---------------------------------

    """

    FinalCode = EssentialPart

    for ToExport in Widgets:
        FinalCode += ToExport.Export()

    EndPart = F"""
    
Root.mainloop() # Run the program
    """

    FinalCode += EndPart

    return FinalCode
        

def CloseCodeView():
    global CodeEnabled, CodeRoot
    CodeRoot = CodeRoot.destroy()
    CodeEnabled = False
    CodeEnabledVar.set(False)



def CopyCode():
    Editor.cli
    Editor.clipboard_append(GenerateCode())


CodeText : UI.Text

def CodeViewUI():
    global CodeRoot, CodeEnabled, CodeEnabledVar, CodeText

    LinesOfCode = GenerateCode().splitlines()


    CodeEnabled = CodeEnabledVar.get()

    if CodeEnabled == True:
        if CodeRoot == None:
            CodeRoot = UI.Toplevel(Editor,background="#2f2f2f")
            CodeRoot.title("Code View")
            CodeRoot.iconbitmap("Code.ico")
            CodeRoot.resizable(False,False)
            CodeRoot.geometry("1020x750")
            ScrollY = Scrollbar(CodeRoot,orient="vertical")
            ScrollY.pack(side="right",fill="y") 

            ScrollX = Scrollbar(CodeRoot,orient="horizontal")
            ScrollX.pack(side="bottom",fill="x") 
            


            CodeRoot.protocol("WM_DELETE_WINDOW",CloseCodeView)

            CodeText = UI.Text(CodeRoot,foreground="White",background="#2f2f2f",yscrollcommand=ScrollY,xscrollcommand=ScrollX,width=200,height=40,borderwidth=0,wrap="none")
            CodeText.pack(anchor="w")

            UUI.Button(CodeRoot,text="Copy to Clipboard",command=CopyCode).pack()
            

        CodeText.config(state=UI.NORMAL)

        CodeText.delete(1.0,END)    
        
        

        for Line in LinesOfCode: # Add new code
            CodeText.insert(END,f"{Line}\n")
            
        
        CodeText.config(state=UI.DISABLED)
            



    else:
        try:
            CodeRoot = CodeRoot.destroy()
        except: pass



#------------------------<Menu Bar>------------------------------------
MenuBar = Menu(Editor)

 # FileMenu.add_command(label="New")      Was gonna be added but i changed my mind ¯\_(ツ)_/¯

FileMenu = Menu(MenuBar,tearoff=0)
FileMenu.add_command(label="Save 💾",command=SaveProject)
FileMenu.add_command(label="Load 💿",command=LoadProject)
FileMenu.add_separator()
FileMenu.add_command(label="Export 📦",command=ExportPYFile)

WidgetMenu = Menu(MenuBar,tearoff=0)
WidgetMenu.add_command(label="Label",command=lambda: CreateWidget("Label"))
WidgetMenu.add_command(label="Button",command=lambda: CreateWidget("Button"))
WidgetMenu.add_command(label="Entry",command=lambda: CreateWidget("Entry"))
#More Widgets added later

ViewMenu = Menu(MenuBar,tearoff=0)
ViewMenu.add_checkbutton(label="Live Editor",variable=LiveEditorEnabledVar,command=LiveEditorUI)
ViewMenu.add_checkbutton(label="Code View",variable=CodeEnabledVar,command=CodeViewUI)


MenuBar.add_cascade(label="File",menu=FileMenu)
MenuBar.add_cascade(label="Widgets",menu=WidgetMenu)
MenuBar.add_cascade(label="View",menu=ViewMenu)
MenuBar.add_cascade(label="Preview",command=PreviewUI)
Editor.config(menu=MenuBar)


ContextMenu = Menu(Editor,tearoff=0)

ContextMenu.add_command(label="Move Up 🔼",command= lambda: MoveWidget(True))
ContextMenu.add_command(label="Move Down 🔽",command=lambda: MoveWidget(False))
ContextMenu.add_separator()
ContextMenu.add_command(label="Delete ❌",command=DeleteWidget)
ContextMenu.add_separator()
ContextMenu.add_command(label="Duplicate 📰",command=DuplicateWidget)



#--------------------------<UI Widgets>-------------------------------





FrameLabelFont = ("Roboto","20","bold") #What style all the tabs will have

PropertyFrame = UI.Frame(Editor) #Frames
PropertyFrame.grid(column=0,row=0,sticky="n")
PropertyFrameLabel = UI.Label(text="Widget Properties",master=PropertyFrame,font=FrameLabelFont)
PropertyFrameLabel.pack(anchor="center")


ItemFrame = UI.Frame(Editor)
ItemFrame.grid(column=1,row=0,padx=75,sticky="n")
ItemFrameLabel = UI.Label(text="Added Widgets",master=ItemFrame,font=FrameLabelFont)
ItemFrameLabel.pack(anchor="center")


RootEditorFrame = UI.Frame(Editor)
RootEditorFrame.grid(column=2,row=0,sticky="n")
RootEditorLabel = UI.Label(text="Edit Root",master=RootEditorFrame,font=FrameLabelFont)
RootEditorLabel.pack(anchor="center")




# ---------------------------------------------<Root UI>--------------------------------------------------

UI.Label(RootEditorFrame,text="Root Name",font = ("Roboto","12")).pack() 
UUI.Entry(RootEditorFrame,textvariable=RootNameVar).pack()
UI.Label(RootEditorFrame,text="Geometry X",font = ("Roboto","12")).pack()
UUI.Entry(RootEditorFrame,textvariable=GeometryXVar).pack()
UI.Label(RootEditorFrame,text="Geometry Y",font = ("Roboto","12")).pack()
UUI.Entry(RootEditorFrame,textvariable=GeometryYVar).pack()

# ResizeableX = UI.Checkbutton(RootEditorFrame,text="Resizeable X",font = ("Roboto","12"),variable=ResizeXVar)
# ResizeableX.pack()
# ResizeableY = UI.Checkbutton(RootEditorFrame,text="Resizeable Y",font = ("Roboto","12"),variable=ResizeYVar)
# ResizeableY.pack()

UI.Label(RootEditorFrame,text="Root Color",font = ("Roboto","12")).pack()

RootColorPicker = UI.Button(RootEditorFrame,command=lambda: GetColor(RootColorPicker),width=10) # Button to set Root
RootColorPicker.pack()


UI.Button(RootEditorFrame,text="Set Root",command=SetRoot).pack() # Button to set Root

# ---------------------------------------------<Widget Viewer>--------------------------------------------------

ItemHierarchy = UUI.Treeview(master=ItemFrame,columns=("Widget"),selectmode=UI.BROWSE,height=25) # Widget Viewer UI
ItemHierarchy.pack()
ItemHierarchy.heading("#0",text="Name")
ItemHierarchy.heading("Widget",text="Widget")

ItemHierarchy.bind("<Button-3>",ShowContextMenu) # Show context menu
ItemHierarchy.bind("<ButtonRelease-1>",SetSelectedWidget) # Edit the Widget


#Var names will start with Prop meaning Property
# ---------------------------------------------<Property tab>--------------------------------------------------
UI.Label(PropertyFrame,text="Name",font = ("Roboto",12)).pack()
UUI.Entry(PropertyFrame,font = ("Roboto","12"),textvariable=PropNameVar).pack()



UI.Label(PropertyFrame,text="Text",font = ("Roboto","12")).pack() 
UUI.Entry(PropertyFrame,font = ("Roboto","12"),textvariable=PropTextVar).pack()



UI.Label(PropertyFrame,text="Text Size",font = ("Roboto","12")).pack() 
UUI.Entry(PropertyFrame,font = ("Roboto","12"),width=5,textvariable=PropTextSizeVar).pack()


UI.Label(PropertyFrame,text="Foreground",font = ("Roboto","12")).pack() 
ForegroundPicker = UI.Button(PropertyFrame,command=lambda: GetColor(ForegroundPicker),width=10) # Button to set Root
ForegroundPicker.pack()


UI.Label(PropertyFrame,text="Background",font = ("Roboto","12")).pack() 
BackgroundPicker = UI.Button(PropertyFrame,command=lambda: GetColor(BackgroundPicker),width=10) # Button to set Root
BackgroundPicker.pack()


UI.Label(PropertyFrame,text="Position X",font = ("Roboto","12")).pack() 
UUI.Entry(PropertyFrame,font = ("Roboto","12"),width=5,textvariable=PropPosXVar).pack()
UI.Label(PropertyFrame,text="Position Y",font = ("Roboto","12")).pack() 
UUI.Entry(PropertyFrame,font = ("Roboto","12"),width=5,textvariable=PropPosYVar).pack()

UI.Button(PropertyFrame,text="Set Properties",command=SetWidgetProperty).pack() # Button to set Root

DisablePropertyTab(True)




Editor.mainloop()