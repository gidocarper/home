this is a small service for the LED lights of the Respeaker 4Mic Array
if you want to use this project along with led lights going off and on install the device as described here
https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/

and install the services as a normal service for the raspberry pi
you though need to 

pip3 install -r requirements.txt

in this directory to make sure that the service will work.

alternative 
you can of course also add the lines from the ledLights.service.py to the intentHandler.py and make only a service of the intentHandler
