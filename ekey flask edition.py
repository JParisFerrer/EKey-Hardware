from flask import Flask
import RPi.GPIO as GPIO
import time
import sqlite3 as lite;
import os;
import os.path;
import rsa;
from datetime import datetime;

#this sets up a flask server referred to in code as ekeyflask
ekeyflask = Flask(__name__)
doorServo = None

SERVO_PIN = 18 #servo constant

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
	unlockDoor()
	return 'Door unlocked! please disable me in prod'

@ekeyflask.route('/cmd/lock')
def lock():
	lockDoor()
	return 'Door locked! please diable me in prod'
	
@ekeyflask.route(/cmd/checkstring/<encryptedstring>)
def checkstring():
        try:
		
		# if input starts with rsa treat rest as encrypted data
		if(encryptedstring[0:3] == "rsa"):
			asString = decrypt(asString[3:].encode("utf-8"))
		
		if(encryptedstring == "unlock"):
			unlockDoor()
		elif (encryptedstring == "lock"):
			lockDoor()
			
	except Exception as e:
		printF ("Error printFing data: %s" % str(e))
	return 'you sent %s!' %encryptedstring #should just bounce string back

	
@ekeyflask.route(/hello)
def hello():
	return 'hello!'
	
#-----------------------SERVO FUNCTIONS START HERE -------------------------------------

def degreeToDuty (angle):
        return angle/10 +2.5

def setDoorServo(pin, angle):#angle is now in DEGREES
        angle = max(min(angle,175),5)#cap position between 0-100
        
	#doorServo.start(degreeToDuty(angle)) #between 0-100 % duty cycle, this will need adjustment in the lock/unlock functions
	doorServo.ChangeDutyCycle(angle)	# turns out that 5 - 11 (% apparently) is around 90 degrees for some reason
	
def stopDoorServo():
	doorServo.stop()
	
def unlockDoor():#these are there own functions rather than direct setservo calls because we will be fiddling with the 0/100 and 
	printF("Unlocking door")
	setDoorServo(11)	#Voodoo motor crap. Don't question it
	time.sleep(2)

def lockDoor():
printF("Locking door")
	setDoorServo(5)	#Again, don't question it
	time.sleep(2)

def initServo():
	global doorServo
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SERVO_PIN,GPIO.OUT) #phsyical pin 16
	doorServo = GPIO.PWM(SERVO_PIN, 50)
	
	doorServo.start(5);
	
#-------HELPER FUCNTIONS--------------------------------------------------
def printF(s):
	print("[" + str(datetime.now().time().hour) + ":" + str(datetime.now().time().minute) + ":" + str(datetime.now().time().second) + "] " + s)
	
#--------ENCRYPTION STUFF--------------------------------------
def initRSA():
	global pKey
	
	with open("ekey.pem") as pFile:
		keyData = pFile.read()
		
	pKey = rsa.PrivateKey.load_pkcs1(keyData)

def decrypt(bytes):
	try:
		plain = rsa.decrypt(bytes, pKey)
	except Exception as e:
		printF("Error decrypting bytes: %s; %s" % (str(bytes), str(e)))
	
	return plain	
	
#--------MAIN EQUIVALENT --------------------------------------
	
def run():
	try:
                initServo()
                initRSA()
                ekeyflask.run(host ='0.0.0.0) #makes the script/server/thing listen on all IPs
                              
        except Exception as e:
                printF("Exception " + str(e))
	
		
run()
