SLight is a modular system which transforms streetlights 
into intelligent lights which conserve energy and 
collect real time data about the state of the road. 
This package gives the code used, setup instructions 
and a video explaining the system and its benifits.

Code Folder Breakdown:
Pi-Contains the code which goes onto the raspberry pi's
   used. This code is done in python 2.7.

Portal-A website which pulls real time data collected from 
       the roads and displays some of it in a graph form.

CarControl-The scripts used for controlling the Anki Overdrive
           cars, this includes their speed, acceleration, lane
           changing and car light control. This is implemented
           in C. Note the scripts are from a github repo found 
           online @ http://anki.github.io/drive-sdk/ and not part
           of our code to marked.

SLight Dev Team
-Gerard Rique
-Jonathan Earle
-Kerschel James
-Sanjay Dookhoo
