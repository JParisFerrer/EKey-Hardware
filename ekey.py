from bluetooth import *
#from bluetooth.ble import BeaconService
import RPi.GPIO as GPIO
import time
from datetime import datetime
import sqlite3 as lite;
import os;
import os.path;
import rsa;

# --------- CONSTANTS -----------------------------------------------------

# Whether to use BLE beacon or normal bluetooth advertisement
BLE = False

# just a random uuid I generated
UUID = "dad8bf14-b6c3-45fa-b9a7-94c1fde2e7c6"

# what pin our servo is connected to
SERVO_PIN = 18


# --------- GLOBAL VARIABLES ----------------------------------------------

# BLE beacon
service = None

# our normal bluetooth socket
server_sock = None

# the connection to our SQL server
sqlCon = None

doorServo = None

# private key
pKey = None

#-------HELPER FUCNTIONS--------------------------------------------------
def printF(s):
	print("[" + str(datetime.now().time().hour) + ":" + str(datetime.now().time().minute) + ":" + str(datetime.now().time().second) + "] " + s)


#-------BLUETOOTH SHENANIGANS START HERE-----------------------------------
def startBLEBeacon():
	printF("Starting BLE Beacon")
	global service
	service = BeaconService()
	
	service.start_advertising(UUID, 		# uuid of server
		1,									# 'major' - no idea what this does (1 - 65535)
		1,									# 'minor' - no idea what this does either (1 - 65535)
		1,									# txPower, power of signal (-20 - 4)
		200)								# interval - not exactly sure what this does either, but this is the default
	
def stopBLEBeacon():
	printF("Stopping BLE Beacon")
	service.stop_advertising()
	
def setupDataListener():
	global server_sock
	server_sock = BluetoothSocket( RFCOMM )
	server_sock.bind(("",PORT_ANY))
	server_sock.listen(1)

	port = server_sock.getsockname()[1]
	
	# advertise normally if no BLE
	if(not BLE):
		printF ("Starting non-BLE beacon")
		advertise_service( server_sock, "EKey Lock",
                   service_id = UUID,
                   service_classes = [ UUID, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
	
	printF("Waiting for connection on RFCOMM channel %d" % port)

	
def listenForData():
	try:
		# keep accepting connections
		while True:
			client_sock, client_info = server_sock.accept()
			printF("Accepted connection from: %s" % client_info)
			
			allData = []
		
			try:
				while True:
					data = client_sock.recv(1024)
				
					if len(data) == 0: break
				
					printF("received [%d] bytes" % len(data))
					
					# add the received data to out variable of all dat
					allData.extend(data)
					
					processData(data)	# process data everyime for testing
				
			except IOError:
				printF("disconnected")
				
			# at this point all of our data should be read
			#processData(allData)
			
	except Exception as e:
		printF ("Error listening for data: %s" % str(e))
		raise	# throw it back up to terminate (can be changed later)
	
def processData(bytes):
	try:
		asString = ''.join(chr(v) for v in bytes)	# take our list of bytes, convert into char (ascii only)
		printF("Data: " + asString)
		isRSA = False
		
		# if input starts with rsa treat rest as encrypted data
		if(asString[0:3] == "rsa"):
			asString = decrypt(asString[3:].encode("utf-8"))
			isRSA = True
		
		if(isRSA):
			# 10 char timestamp
			try:
				timestamp = int(asString[0:9])
		
				dt = datetime.utcfromtimestamp(timestamp)
			
			except Exception as e:
				printF("Exception parsing timestamp '%s': %s" % (str(timestamp), str(e)))
		
			if(abs(timestamp, time.time()) > 60):
				printF("Open request denied at %d (delta: %d)" % (timestamp, timestamp-time.time()))
				break
		
		
		if (isRSA):
			cmd = asString[10:]
		else:
			cmd = asString
		
		if(cmd == "unlock"):
			unlockDoor()
		elif (cmd == "lock"):
			lockDoor()
			
	except Exception as e:
		printF ("Error printFing data: %s" % str(e))

# ---- DATABASE FUCNTIONS ----------------------------------------------------------------------------------------
def initDatabase():
	global sqlCon
	
	# if database doesn't exist, create it using external shell script
	if (not os.path.isfile("ekey.db")):
		printF("Creating database file...")
		os.system("./db.sh")
		
	sqlCon = lite.connect("./ekey.db")
	printF("Connected to database file")
	
	# returs our data by column name, so data["UUID"], instead of data[2] (or whatever column number it is)
	sqlCon.row_factory = lite.Row
	
def getKeyByUUID(uuid):
	try:
		cur = sqlCon.cursor()
		
		# use the parameterized query
		cur.execute("SELECT * FROM Keys WHERE UUID=?", (uuid))
	
		key = cur.fetchone()
		
		# key is a dictionary indexed by column names 
		return key;
	
	except lite.Error as e:
		#cur.rollback()	# nothing to rollback, its a SELECT nothing else
		printF("Error getting Key by UUID: %s" % e.args[0])
		
#-----------------------SERVO FUNCTIONS START HERE -------------------------------------

def degreeToDuty (angle):
        return angle/10 +2.5

def setDoorServo(angle):#angle is now in DEGREES
	angle = max(min(angle,175),5)#cap position between 0-100

	#doorServo.start(degreeToDuty(angle)) #between 0-100 % duty cycle, this will need adjustment in the lock/unlock functions
	doorServo.ChangeDutyCycle(angle)	# turns out that 5 - 11 (% apparently) is around 90 degrees for some reason
	
def stopDoorServo():
	doorServo.stop()
	
def unlockDoor():#these are there own functions rather than direct setservo calls because we will be fiddling with the 0/100 and 
	printF("Unlocking door")
	setDoorServo(11)	#Don't question it
	time.sleep(2)
	#stopDoorServo()	#once the servo stops it never comes back	

def lockDoor():
	printF("Locking door")
	setDoorServo(5)	#Don't question it
	time.sleep(2)
	#stopDoorServo()	#once the servo stops it doesn't come back
	
def initServo():
	global doorServo
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SERVO_PIN,GPIO.OUT) #phsyical pin 16
	doorServo = GPIO.PWM(SERVO_PIN, 50)
	
	doorServo.start(5);
	
	
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
		initDatabase()
		
		initRSA()
		
		initServo()
		
		if (BLE):
			startBLEBeacon()
		
		setupDataListener()
		
		listenForData()
		
		
	except Exception as e:
		printF("Exception " + str(e))
		
	finally:
		printF("Exiting...")
		
		if (BLE):
			stopBLEBeacon()
		server_sock.close()	
		
		if(sqlCon):
			sqlCon.close()
		
run()
