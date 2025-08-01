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

  `py mtraskbar.py`

You can also save in the folder a go.bat script containing these 2 lines:

 ```
call myenv\Scripts\activate.bat
py mtraskbar.py
```

You can start the taskbar just by opening the batch file.



