import socket, threading, time, ConfigParser
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Link"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Starts a server for music visualization or screen mirroring" 
#This defines which additional arguments this effect can take.
#Combine multiple options with a '|'
modifiers = NONE

#This is the function that controls the effect. Look at the included effects for examples.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   stop_event: A threading event that allows this effect to be stopped by the parent.
#   color: The color if passed, otherwise the default color. REMOVE IF COLOR IS NOT A MODIFIER.
#   speed: The speed multiplier if passed, otherwise the default speed. REMOVE IF SPEED IS NOT A MODIFIER.
#   **extras: Any other parameters that may have been passed. Do not use, but do not remove.
def start(lights, stop_event, color = [255, 255, 255], speed = 1, **extras):
    # create a raw socket and bind it to the public interface
    si = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #Allow socket to be reopened immediately after closing
    si.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Turn off blocking mode for the stop event can be the only factor
    si.setblocking(False)
    #Binding to "" is the same as binding to any address
    si.bind(("", port))
    while not stop_event.is_set():
        try:
            nbytes = si.recv_into(data)
            if data:
                lights.set_pixels([data[i:i+3] for i in xrange(0, nbytes, 3)])
                lights.show()
        except socket.error:
            pass

config = ConfigParser.ConfigParser()
config.read("configuration/config.ini")
username = config.get("Link", "username")
password = config.get("Link", "password")
port = config.getint("Link", "port")
data = bytearray(2048)
