from bluetooth import *
from bluetooth.ble import BeaconService
import RPi.GPIO as GPIO
import time
import sqlite3 as lite;
import os;
import os.path;

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


#-------BLUETOOTH SHENANIGANS START HERE-----------------------------------
def startBLEBeacon():
	print("Starting BLE Beacon")
	global service
	service = BeaconService()
	
	service.start_advertising(UUID, 		# uuid of server
		1,									# 'major' - no idea what this does (1 - 65535)
		1,									# 'minor' - no idea what this does either (1 - 65535)
		1,									# txPower, power of signal (-20 - 4)
		200)								# interval - not exactly sure what this does either, but this is the default
	
def stopBLEBeacon():
	print("Stopping BLE Beacon")
	service.stop_advertising()
	
def setupDataListener():
	global server_sock
	server_sock = BluetoothSocket( RFCOMM )
	server_sock.bind(("",PORT_ANY))
	server_sock.listen(1)

	port = server_sock.getsockname()[1]
	
	# advertise normally if no BLE
	if(not BLE):
		print ("Starting non-BLE beacon")
		advertise_service( server_sock, "EKey Lock",
                   service_id = UUID,
                   service_classes = [ UUID, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
	
	print("Waiting for connection on RFCOMM channel %d" % port)

	
def listenForData():
	try:
		# keep accepting connections
		while True:
			client_sock, client_info = server_sock.accept()
			print("Accepted connection from: ", client_info)
			
			allData = []
		
			try:
				while True:
					data = client_sock.recv(1024)
				
					if len(data) == 0: break
				
					print("received [%d] bytes" % len(data))
					
					# add the received data to out variable of all dat
					allData.extend(data)
					
					processData(data)	# process data everyime for testing
				
			except IOError:
				print("disconnected")
				
			# at this point all of our data should be read
			#processData(allData)
			
	except Exception as e:
		print ("Error listening for data: %s" % str(e))
		raise	# throw it back up to terminate (can be changed later)
	
def processData(bytes):
	try:
		asString = ''.join(chr(v) for v in bytes)	# take our list of bytes, convert into char (ascii only)
		print("Data: " + asString)
		
		if(asString == "unlock"):
			unlockDoor()
		elif (asString == "lock"):
			lockDoor()
			
	except Exception as e:
		print ("Error printing data: %s" % str(e))

# ---- DATABASE FUCNTIONS ----------------------------------------------------------------------------------------
def initDatabase():
	global sqlCon
	
	# if database doesn't exist, create it using external shell script
	if (not os.path.isfile("ekey.db")):
		print("Creating database file...")
		os.system("./db.sh")
		
	sqlCon = lite.connect("./ekey.db")
	print("Connected to database file")
	
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
		print("Error getting Key by UUID: %s" % e.args[0])
		
#-----------------------SERVO FUNCTIONS START HERE -------------------------------------

def degreeToDuty (angle):
        return angle/10 +2.5

def setDoorServo(angle):#angle is now in DEGREES
	angle = max(min(angle,175),5)#cap position between 0-100

	doorServo.start(degreeToDuty(angle)) #between 0-100 % duty cycle, this will need adjustment in the lock/unlock functions
	
def stopDoorServo():
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
	
def initServo():
	global doorServo
	
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(SERVO_PIN,GPIO.OUT) #phsyical pin 16
	doorServo = GPIO.PWM(SERVO_PIN, 50)
	
	
#--------MAIN EQUIVALENT --------------------------------------
	
def run():
	
	try:
		initDatabase()
		
		initServo()
		
		if (BLE):
			startBLEBeacon()
		
		setupDataListener()
		
		listenForData()
		
		
	except Exception as e:
		print("Exception " + str(e))
		
	finally:
		print("Exiting...")
		
		if (BLE):
			stopBLEBeacon()
		server_sock.close()	
		
		if(sqlCon):
			sqlCon.close()
		
run()
