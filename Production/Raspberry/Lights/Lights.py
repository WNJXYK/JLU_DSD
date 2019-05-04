import RPi.GPIO as gpio
import socket
import time
import json
from threading import Thread

gpio.setmode(gpio.BCM)
gpio.setup(18, gpio.OUT)

class Lights():
    def __init__(self):
        self.type = 'lights'
        self.port = None
        self.host = None
        self.address = None
        self.auth = None
        self.hid = None
        self.type = None
        gpio.setmode(gpio.BCM)
        gpio.setup(18, gpio.OUT)
        self.ss = None
    
    #Reads the config.txt and initializes the corresponding variables
    def ReadConfig(self):
        file = open("config.txt", "r")
        
        lines = file.readlines()
        i = 0
        for x in lines:
            for y in x.split(':'):                
                if i == 1:
                    self.host = y
                    self.host = self.host.split('\n')[0]
                elif i == 3:
                    self.port = y
                    self.port = self.port.split('\n')[0]
                elif i == 5:
                    self.hid = y
                    self.hid = self.hid.split('\n')[0]
                elif i == 7:
                    self.type = y
                    self.type = self.type.split('\n')[0]
                elif i == 9:
                    self.auth = y
                    self.auth = self.auth.split('\n')[0]
                i += 1  
        
    #Starts running the socket connection
    def Run(self):        
        self.ReadConfig()
        self.address = (self.host, int(self.port))
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ss.connect(self.address)
        
        if self.Authenticate() == 0:
            #Listening thread
            thread = Thread(target=self.Handle)
            thread.setDaemon(True)
            thread.start()
            print("Socket is listening on %s:%d" % self.address)
        else:
            self.ss.close()
            print("Authentication failed, closing socket...")       
        

    #Tries to Authenticathe on the server, returns the status received
    def Authenticate(self):
        authMsg = ('{"id":"%s", "type":"%s", "auth":"%s", "socket":"out" }' % (self.hid, self.type, self.auth) ).encode("utf8")
        self.ss.send(authMsg)
        
        while True:
            result = json.loads(self.ss.recv(1024).decode("utf8"))
            if result is not None:
                print(result["msg"])
                return result["status"]
        
    #Puts the rasp waiting for requests from the server
    def Handle(self):
        while True:
            data = json.loads(self.ss.recv(1024).decode("utf8"))
            
            #Checks if there is any data
            if not data:
                self.ss.send('No data'.encode("utf8"))
            else:
                #Checks the type of request(post), and turns the lights ON
                if(data["type"] == "post"):
                    if(self.GetState() == 1):
                        self.Switch(0)
                        self.ss.send('{"status":"0", "msg":"Operation successeful"}'.encode("utf8"))
                        log = ('State changed: %d on ' % self.GetState() + time.asctime() + '\n')
                        print (log)
                        self.WriteLog(log)
                    elif(self.GetState() == 0):
                        self.Switch(1)
                        self.ss.send('{"status":"0", "msg":"Operation successeful"}'.encode("utf8"))
                        log = ('State changed: %d on ' % self.GetState() + time.asctime() + '\n')
                        print (log)
                        self.WriteLog(log)                    
                    else:
                        self.ss.send('{"status":"0", "msg":"Operation unsuccesseful"}'.encode("utf8"))
                
                #Checks the type of request(get), and returns the state to the server
                if(data["type"] == "get"):
                    self.ss.send(('{"state":"%d"}' % self.GetState()).encode("utf8"))
                    log = ('State sent: %d on ' % self.GetState() + time.asctime() + '\n')
                    print (log)
                    self.WriteLog(log)
        
        
    #Turns on/off the light    
    def Switch(self, state):
        if(state != gpio.input(18)):
            gpio.output(18, state)
    
    #Returns the state of the lights
    def GetState(self):
        return gpio.input(18)
    
"""
def switch(self):        
    self.client.send('{"type":"post"}'.encode("utf8"))
    print(self.client.recv(1024).decode("utf8"))
    
def getState(self):
    self.client.send('{"type":"get"}'.encode("utf8"))
    print(self.client.recv(1024).decode("utf8"))

This two methods were the ones i used to call the methods above from the server.
"""
    #Saves the logs of every request from the server
    def WriteLog(self, log):
        #Open log file
        file = open("raspLog.txt", "a+")
        
        file.write(log)        
        file.close()
    
