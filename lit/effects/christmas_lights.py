#This is what will appear in all interfaces
name = "Christmas Lights"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Colors of traditional colored christmas lights"

#This defines the format of update's 'state' parameter
#If a 'speed' key is defined it must be an int and will automatically be used by the daemon.
schema = {}

#This is the function that updates the effect.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   step: The number of times that this effect has been updated
#   state: Dict with information about the state of the effect
def update(lights, step, state):
    for i in lights.all_lights():
        seq = i%5
        if seq == 0:
            lights.set_pixel(i, 100, 0, 0)
        elif seq == 1:
            lights.set_pixel(i, 100, 0, 50)
        elif seq == 2:
            lights.set_pixel(i, 0, 100, 0)
        elif seq == 3:
            lights.set_pixel(i, 150, 100, 0)
        elif seq == 4:
            lights.set_pixel(i, 0, 0, 100)
