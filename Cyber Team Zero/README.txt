Hi There!

This file will briefly explain the file and directory structure of Cyber Team Zero.

TL;DR:
	Put your AI in a subdirectory of the "Bots" directory.

	If you want to run a game (between AI or between people or using an IDE) 
		- "Launcher.bat" on Windows
		- "Launcher.sh" on OS X and Linux
		

Bots
----

Your AI goes here! You should put it in a subdirectory, like Bots/Decimator9000

The subdirectory name will also be used as your AI's name.

Libraries
---------

The game's binary files are located here, along with the Python Client. If you want to set up an IDE,
this is where you find the files you need to run your client.

Logs
----

Output logs from the server and the clients are stored here. 
Client logs are logged to the client monitor window too, and server logs will be logged to the terminal window you run the launcher from.

Maps
----

This directory is for ... maps. Map files and their navigation caches go here. The navigation cache compiler is also located here.
See the manual for more information about what that is.

MatchPresets
------------

This directory contains the saved match presets from the launcher. They are in JSON format, but it is strongly recommended they not be edited manually.


Resources
---------

The game's assets are located here. Changing or removing anything in this folder may cause the server to crash.

Results
-------

After each game, all the results are stored in the Results folder.
Every game's result is saved in a file with a format like Player_1_name.Player_2_name.Map_name.json

These files contain the final scores and their breakdowns, as well as a history of all the moves received by the server during each turn.


The Shell Scripts
-----------------

There are 2 Shell scripts available to run the launcher.
The script ending in .bat is for Windows, while the one ending in .sh is for macOS and Linux.


Thanks for reading me! 

If you have any questions, please don't hesitate to read the manual :)
If you still have any questions after that, please don't hesitate to get in touch with us either via Slack or email.

Good luck!


