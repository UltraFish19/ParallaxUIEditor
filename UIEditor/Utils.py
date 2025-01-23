import math
import tkinter as UI


# Contains any function and classes that doesn't directly change widgets and is safe to move




class EditorWidget(): #Instead of dict I'm using an object to store data
    
    Type : str = ""


    def __init__(Self,Type : str):
        Self.Type = Type
        Self.Name = f"Unnamed{Type}"


    def __str__(self): 
        return f"{self.Type} : {self.Name}" # If I do print(EditorWidget) it will print this :D


    Name: str = Type
    ID : str = ""
    FG : str = "#000000"
    BG : str = "#F0F0F0"

    PosX: int = 10
    PosY : int = 10


    Text : str = "Text"
    TextSize : int = 12
   # IsBold = False


    def Export(Self):
        return f'''
{Self.Name} = UI.{Self.Type}(Root,text="{Self.Text}",font=(None,{Self.TextSize}),foreground="{Self.FG}",background="{Self.BG}") # Creates a new {Self.Type} called {Self.Name} with the specified properties
{Self.Name}.place(x={Self.PosX},y={Self.PosY},anchor=UI.CENTER) # Places the widget to the specified position
        '''

    def Save(Self):
        Data = {}

        Data["Type"] = Self.Type
        Data["Name"] = Self.Name
        Data["FG"] = Self.FG
        Data["BG"] = Self.BG
        Data["PosX"] = Self.PosX
        Data["PosY"] = Self.PosY
        Data["Text"] = Self.Text
        Data["TextSize"] = Self.TextSize


        return Data










def CheckWidgetVarName(Name): # Checks input to see if it is valid for Python
    try:
        exec(f"{Name} = False")
    except:
        return False
    return True






def Clamp(Minimum, X, Maximum): 
    """Makes X so it doesn't go below Minimum and below Maximum"""
    return max(Minimum, min(X, Maximum))




def RoundUp(X,A):
    return math.ceil(X / float(A)) * A

