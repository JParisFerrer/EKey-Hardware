from flask import Flask
import RPi.GPIO as GPIO
import time
import sqlite3 as lite;
import os;
import os.path;

#this sets up a flask server referred to in code as ekeyflask
ekeyflask = Flask(__name__)
doorServo = None


#-------FLASK SHENANIGANS START HERE-----------------------------------

# @ekeyflask.route('/cmd/unlock/<encrypted_string>')
# def unlock(encryptedstring): 
	# not sure how python like overloaded functions, inactive for now
	# if string decrypts properly, timestamp is valid etc then open
	# for now just bounce the string back
	# return 'you sent %s!' encryptedstring #these returns might be for html pages, so it's possible that none of these work
# @ekeyflask.route('/cmd/unlock/<encrypted_string>')
	# same deal
	# return 'you sent %s!' encryptedstring

@ekeyflask.route('/cmd/unlock')
def unlock
	unlockDoor()
	return 'Door unlocked! please disable me in prod'

@ekeyflask.route('/cmd/lock')
def lock
	lockDoor()
	return 'Door locked! please diable me in prod'
	
@ekeyflask.route(/cmd/checkstring/<encryptedstring>)
	return 'you sent %s!' encryptedstring #should just bounce string back

	
@ekeyflask.route(/hello)
	return 'hello!'
	
#-----------------------SERVO FUNCTIONS START HERE -------------------------------------

def degreeToDuty (angle):
        return angle/10 +2.5

def setDoorServo(pin, angle):#angle is now in DEGREES
	angle = max(min(angle,175),5)#cap position between 0-100

	global doorServo
	doorServo.start(degreeToDuty(angle)) #between 0-100 % duty cycle, this will need adjustment in the lock/unlock functions
	
def stopDoorServo():
	global doorServo
	doorServo.stop()
	
def unlockDoor():#these are there own functions rather than direct setservo calls because we will be fiddling with the 0/100 and 
	setDoorServo(40)#this is better than search and replacing the 0/100 values and sleep times every time we want to fiddle with them
	time.sleep(5)
	stopDoorServo()
	print("Unlocking door")

def lockDoor():
	setDoorServo(140)
	time.sleep(5)
	stopDoorServo()
	print("Locking door")
	
#--------MAIN EQUIVALENT --------------------------------------
	
def run():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23,GPIO.OUT) #phsyical pin 16
	doorServo = GPIO.PWM(23, 50)
	
	
	ekeyflask.run(host ='0.0.0.0) #makes the script/server/thing listen on all IPs
		
run()
