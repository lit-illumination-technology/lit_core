import socket, threading, time, ConfigParser
import controls as np

config = ConfigParser.ConfigParser()
config.read("config.ini")
password = config.get("General", "password")
port = config.getint("General", "port")
data = bytearray(2048)

def start():
    # create a raw socket and bind it to the public interface
    si = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #Allow socket to be reopened immediately after closing
    si.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Binding to "" is the same as binding to any address
    si.bind(("", port))
    print "listening on port " + str(port)
    while True:    
        nbytes = si.recv_into(data)
        np.set_pixels([data[i:i+3] for i in xrange(0, nbytes, 3)])
        np.show()

if __name__=="__main__":
    start()
atexit.register(s.close)
