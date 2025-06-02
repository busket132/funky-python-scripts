import tkinter as tk
import subprocess as sp
import os
import sys

root = tk.Tk()



def get_executable_name():
    # getting executable
    if getattr(sys, 'frozen', False):
        # if .exe
        return os.path.basename(sys.executable)
    else:
        # if .py
        return os.path.basename(sys.argv[0])

def Resize_Enabler(string1): #handles if program is resizable or not
    if string1.lower() == "true":
        root.resizable(True, True)
    else:
        root.resizable(False, False)

def Add_Attributes(*args):
    for arg in args:
        root.attributes(arg, True)

buttons = {}

def Add_Button(string1,*args):
    for arg in args:
        buttons["button"+str(arg)] = tk.Button(root, text=string1)
        buttons["button"+str(arg)].pack()
    return buttons["button"+str(args[0])]

labels = {}

def Add_Label(string1,*args):
    for arg in args:
        labels["label"+str(arg)] = tk.Label(root, text=string1)
        labels["label"+str(arg)].pack()
    return labels["label"+str(args[0])]

entries = {}

def Add_CheckButton(string1, *args):
    for arg in args:
        checkb["checkb"+str(arg)] = tk.Checkbutton(root, text=string1)
        checkb["checkb"+str(arg)].pack()
    return checkb["checkb"+str(arg)]

checkb = {}

def Add_Entry_DV(string1, value1="", *args):
    var = tk.StringVar(value=value1)
    if args:
        for arg in args:
            entries["entry"+str(arg)] = tk.Entry(root, textvariable=var)
            entries["entry"+str(arg)].pack()
        return entries["entry"+str(args[0])]
    else:
        entry = tk.Entry(root, textvariable=var)
        entry.pack()
        return entry

def Boolean(value1):
    return tk.BooleanVar(value=value1)

def Double(value1=0.0):
    return tk.DoubleVar(value=value1)

def Int(value1=0):
    return tk.IntVar(value=value1)

def String(value1):
    return tk.StringVar(value=value1)

def Get(value1):
    return value1.get

def CreateWindow(value1,value2, string1):
    executable_name = get_executable_name()
        # was meant to remove .exe in file name
    #executable_name_NoExe = os.path.splitext(executable_name)[0]
    root.geometry(str(value1) + "x" + str(value2))
    root.title(string1)
    def on_closing(): #handle killing process when user tries to close program, meant to be used when compiled into .exe
        sp.Popen('taskkill /im ' + str(executable_name) + ' /f') #added str() just to be sure, it doesnt rly matter if its there or not, btw executable shouldn't contain any spaces, use _ or - or literally anything but spaces instead
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
#yeah code is prolly trash but it works and i can understand and use it so ig it doesnt matter
