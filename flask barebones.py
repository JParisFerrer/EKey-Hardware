from flask import Flask
from flask_socketio import SocketIO
import threading
import time
import os;
import os.path;

#this sets up a flask server referred to in code as ekeyflask
ekeyflask = Flask(__name__)
socketio = SocketIO(ekeyflask)

#-------FLASK SHENANIGANS START HERE-----------------------------------

# @ekeyflask.route('/cmd/unlock/<encrypted_string>')
# def unlock(encryptedstring): 
    # not sure how python like overloaded functions, inactive for now
    # if string decrypts properly, timestamp is valid etc then open
    # for now just bounce the string back
    # return 'you sent %s!' %encryptedstring #these returns might be for html pages, so it's possible that none of these work
# @ekeyflask.route('/cmd/unlock/<encrypted_string>')
    # same deal
    # return 'you sent %s!' %encryptedstring

@ekeyflask.route('/cmd/unlock')
def unlock():
    return 'Door unlocked! please disable me in prod'

@ekeyflask.route('/cmd/lock')
def lock():
    return 'Door locked! please disable me in prod'
    
@ekeyflask.route('/cmd/checkstring/<encryptedstring>')
def checkstring(encryptedstring):
    print(encryptedstring + "was received!")
    return 'you sent %s!' %encryptedstring


    
@ekeyflask.route('/hello')
def hello():
    return 'hello!'
    print('hello!')

def startServer():
    socketio.run(ekeyflask, host = '0.0.0.0')
#--------BROADCAST STUFFS -------------------------------------

##def startBroadcast():
##    threading.Timer(1,broadcast).start()
##    broadcast('test data')
##    print('startBroadcast call')
def broadcast():
    socketio.emit('ekey-broadcast-event', 'data')
    print('broadcasting')
    threading.Timer(2,broadcast).start()
    
#--------MAIN EQUIVALENT --------------------------------------
    
def run():
    
    global ekeyflask
    global socketio
    ekeyflask.debug = False
    ekeyflask.use_reloader = False
    print('starting server...')
    serverThread = threading.Thread(target = startServer)
    serverThread.start()
    print('starting broadcast...')
    broadcastThread = threading.Timer(2,broadcast)
    broadcastThread.start()


run()
