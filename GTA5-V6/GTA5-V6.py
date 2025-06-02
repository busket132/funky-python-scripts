import tkinter as tk
import keyboard as kb
import pywinauto
import pydirectinput as pdi
import time
import os
import comtypes.stream
from threading import Thread
from threading import Lock
import subprocess as sp
import queue
import EZTkinter as iql
#from EZTkinter import config

#app = pywinauto.Application(backend="win32").connect(title_re="Grand Theft Auto V")  # Update the title_re parameter if needed
#window = app.top_window()

input_queue = queue.Queue()



toggled = False  # Define the toggled variable outside of any function
laststate = False # Define the laststate variable outside of any function

# Create the main application window
#root = tk.Tk()
#root.title("Anti-AFK Script")

# Add the topmost attribute to the window
#root.wm_attributes("-topmost", True)


TurnOffPc = iql.Int(0)
TurnOffPcAfter = iql.Double(0.0)
TurnOffGta = iql.Int(0)
TurnOffGtaAfter = iql.Double(0.0)

#TurnOffGtaAfter.config(value=0.0)

toggle_label = iql.Add_Label("Anti-AFK is disabled.",1)
toggle_button = iql.Add_Button("Toggle Anti-AFK",1)

TurnOffPc = iql.Add_Label("Turn Off PC after (hours):",1)
TurnOffPcAfter = iql.Add_Entry_DV("TurnOffPcAfter",1)
TurnOffGta = iql.Add_Label("Turn Off GTA after (hours):",1)
TurnOffGtaAfter = iql.Add_Entry_DV("TurnOffGtaAfter",1)

iql.Resize_Enabler("false")
iql.Add_Attributes("-topmost")












# Create labels and buttons for the GUI
#toggle_label = tk.Label(root, text="Anti-AFK is disabled.")
#toggle_button = tk.Button(root, text="Toggle Anti-AFK")

# Create input fields for TurnOffPc and TurnOffGta variables
#pc_label = tk.Label(root, text="Turn Off PC after (hours):")
#pc_entry = tk.Entry(root, textvariable=TurnOffPcAfter)

#gta_label = tk.Label(root, text="Turn Off GTA after (hours):")
#gta_entry = tk.Entry(root, textvariable=TurnOffGtaAfter)




def toggle_anti_afk():
    global toggled
    toggled = not toggled
    if toggled:
        toggle_label.config(text="Anti-AFK is working, open game window.")
    else:
        toggle_label.config(text="Anti-AFK is disabled.")

#config(toggle_button,command, print("1"),1)

toggle_button.config(command=toggle_anti_afk)

#toggle_label.pack()
#toggle_button.pack()
#pc_label.pack()
#pc_entry.pack()
#gta_label.pack()
#gta_entry.pack()


# Start the worker threads
def KeyBindLoop():
    while True:
        time.sleep(0.1)
        global laststate
        global toggled
        pressed = kb.is_pressed("k")
        if pressed != laststate:
            laststate = pressed
            if laststate:
                toggled = not toggled
                if toggled:
                    toggle_label.config(text="Anti-AFK is working, open game window.")
                else:
                    toggle_label.config(text="Anti-AFK is disabled.")

Thread(target=KeyBindLoop).start()

def Simulate_key_press():
    global toggled
    while True:
        time.sleep(0)
        while toggled:
            if not toggled:
                break
            time.sleep(5)
            if not toggled:
                break
            # Simulate pressing the "A" key for 1 second
            pdi.keyDown("a")  # Adjust the pause value if needed
            time.sleep(1)
            pdi.keyUp("a")
            if not toggled:
                break
            time.sleep(150)
            if not toggled:
                break
            # Simulate pressing the "D" key for 1 second
            pdi.keyDown("d")  # Adjust the pause value if needed
            time.sleep(1)
            pdi.keyUp("d")
            if not toggled:
                break
            time.sleep(145)
            if not toggled:
                break

'''def Simulate_key_press():
    global toggled
    while True: 
        time.sleep(0)
        while toggled:
            time.sleep(10)
            if not toggled:
                break
            kb.press("a")
            if not toggled:
                break
            time.sleep(1)
            if not toggled:
                break
            kb.release("a")
            if not toggled:
                break
            time.sleep(150)
            if not toggled:
                break
            kb.press("d")
            if not toggled:
                break
            time.sleep(1)
            if not toggled:
                break
            kb.release("d")
            if not toggled:
                break
            time.sleep(140)
            if not toggled:
                break'''

Thread(target=Simulate_key_press).start()

def PC_Hybernation():
    global toggled
    while True:
        time.sleep(0.1)
        if toggled:
            if float(TurnOffPcAfter.get()) > 0:
                while True:
                    if not input_queue.empty():
                        input_data = input_queue.get()
                        if input_data == 'terminate':
                            if not toggled:
                                break
                            time.sleep(float(TurnOffGtaAfter.get()) * 60 * 60)
                            if not toggled:
                                break
                            os.system('shutdown -h')
                            
                    if not toggled:
                        break
            else:
                print("Pc will not be hybernated")
                break

Thread(target=PC_Hybernation).start()

def GTA_Termination():
    global toggled
    while True:
        time.sleep(0.1)
        if toggled:
            if float(TurnOffGtaAfter.get()) > 0:
                
                while True:
                    if not toggled:
                        break
                    time.sleep(float(TurnOffGtaAfter.get()) * 60 * 60)
                    if not toggled:
                        break
                    sp.Popen('taskkill /im GTA5.exe /f')
                    sp.Popen('taskkill /im' + str(iql.get_executable_name()) + '/f')
                    break
            else:
                print("Gta will not be terminated")
                break

Thread(target=GTA_Termination).start()

iql.CreateWindow(200,200,"Gta Anti-AFK")

# Add 'terminate' to the input queue to initiate shutdown processes
input_queue.put('terminate')



input()