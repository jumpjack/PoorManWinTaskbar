# PoorManWinTaskbar

PMWT- alias "Poor Man Win Taskbar"

* You are "poor", i.e.  you are not the admin of your machine? 

* You've been forced to use Windows 11 with its useless taskbar/appbar/quicklaunchBar?  

This app is for you!


----------

# Problem

Microsoft did a total mess with the application bar in Windows 11; it was already getting worse and worse year by year, but now it possibly reached lowest level:
- can't be resized; you're stuck with one line, even if you use 10 windows at same time as "normal work"
- quicklaunch and application bar are mixed together
- can't drag and drop a file directly on a button and get the file opened
- can't configure quite anything

And, if you are in office and you are not admin of your machine, you can't get rid of it by insatalling any app!

BUT

I found a workaround: start an app (without installing it) which creates a brand new taskbar (rather than modifying the existing one), **without requiring any administrator or special user privilige**!

# Solution (for developers...)

My solution is a python script, ran into a virtual environment created into the "secret" foldr MyApps, where you can copy and run any executable, even as a normal user. It's located in c:\users\USERNAME\MyApps folder .

Unfortunately I am very bad as python programmer (actually I am NOT a python programmer at all: I completely used AI to write this app!), so my app is bad, slow, buggish, its source code is ugly and redundant... but it works, and that's all I need. I** put it here hoping that some REAL python developer can grab it and make it a "real" app**. The biggest issue as of now is that Windows keeps closing it every 5 minutes, and I have no idea why; I am sure any real python deveoper knows why and how to fix it.

# Installation

- Download python to MyApps folder and install it
- Create a virtual python environment in the folder:

   `C:> python -m venv myenv`

"myenv" is the name of the folder which will be creted and which will become your virtual environment

- copy the script in this folder
- open a DOS prompt, go into the folder and launch the virtual environment:

   `call myenv\Scripts\activate.bat`

- your new taskbar is ready: just type

  `py mytaskbar.py`

You can also save in the folder a go.bat script containing these 2 lines:

 ```
call myenv\Scripts\activate.bat
py mtraskbar.py
```

You can start the taskbar just by opening the batch file.

## Dependencies

I am not a python expert, AI did all the job, so I am not very sure about mandatory dependencies, but my script works after installing:

- pywin32
- pillow
- tkinterdnd2
- shiboken6
- PySide6_Essentials
- PySide6_Addons

I think only first three or four ones are mandatory, probably the other ones were needed with a previous version of the script written by another AI.... Sorry, no idea.

Installing these dependencies wit **pip install** could **appear** impossible in a protected office-PC whith limited access network; the workaround is downloading .whl (wheel) file for each dependency and install it offline with:

`pip install --no-index wheelname.whl`

**WARNING:** Be sure to choose the .whl file compatible with your python version: I used python 3.10 in a 64 bit mahcine based on AMD CPU, so I downloaded pywin32-**310**-c**p310**-c**p310**-win_**amd64**.whl

# Usage

Right panel of the bar will just show currently opened app (and some other hidden app which I don't know how to get rid of....):

- Click on an app button to switch to it
- **Drag a file over an app to open a file in that app!** No hassles! No warnings! Just drag&open!

Left panel is the quicklaunch bar: d

- drag here any app or folder to get it permanently stored there
- click an app to launch it
- right click an app to remove it

**The list and position of apps in quicklaunch can be easily edited by user: no secret paths, no hidden folders, just edit the quicklaunch_config.json file!**

You can resize the appbar as you prefer: its size and position will be stored in window_position.json file and restored at startup.

**You can move the appbar to any screen!** Just drag it there, or click Position menu and select your screen.

# Bugs

Many:

- not all menu items are active/working , everything is under test...
- Windows keep closing the appbar time by time, but starting it again bu opening go.bat file is anyway much faster than searching something in the useless builtin taskbar
- Some apps with no visible windows appar anyway as button of available apps (?!?)


# Limits

- You need to install python and some dependencies
- **Currently** you can't drag around the buttons in the bar
- The quicklaunch bar behaves weirdly with mouusewheel...
