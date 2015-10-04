from bluetooth import *
from bluetooth.ble import BeaconService
import RPi.GPIO as GPIO
import time
import sqlite3 as lite;
import os;
import os.path;

# Whether to use BLE beacon or normal bluetooth advertisement
BLE = True

# make sure we have this global variable set up
service = None

# our normal bluetooth socket
server_sock = None

# the connection to our SQL server
sqlCon = None

# just a random uuid I generated
uuid = "dad8bf14-b6c3-45fa-b9a7-94c1fde2e7c6"

doorServo = GPIO.PWM(1, 50)    # create an object p for PWM on port 25 at 50 Hertz
#We will need to fiddle wtih the frequency most likely. 


def startBLEBeacon():
	print("Starting BLE Beacon")
	global service
	service = BeaconService()
	
	service.start_advertising(uuid, 		# uuid of server
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
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
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
				
			except IOError:
				print("disconnected")
				
			# at this point all of our data should be read
			processData(allData)
			
	except Exception as e:
		print ("Error listening for data: %s" % str(e))
		raise	# throw it back up to terminate (can be changed later)
	
def processData(bytes):
	pass

def initDatabase():
	global sqlCon
	
	# if database doesn't exist, create it using external shell script
	if (not os.path.isfile("ekey.db")):
		os.system("./db.sh")
		
	sqlCon = lite.connect("./ekey.db")
	
	# returs our data by column name, so data["UUID"], instead of data[2] (or whatever column number it is)
	sqlCon.row_Factory = lite.row
	
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
		

def setDoorServo(pin, position):
	position = max(min(postion,100),0)#cap position between 0-100

	global doorServo
	doorServo.start(position) #between 0-100 % duty cycle, this will need adjustment in the lock/unlock functions
	
def stopDoorServo():
	global doorServo
	doorServo.stop()
	
def unlockDoor():#these are there own functions rather than direct setservo calls because we will be fiddling with the 0/100 and 
	setDoorServo(0)#this is better than search and replacing the 0/100 values and sleep times every time we want to fiddle with them
	time.sleep(5)
	stopDoorServo()

def lockDoor():
	setDoorServo(100)
	time.sleep(5)
	stopDoorServo()
	
def run():
	try:
		initDatabase()
		
		if (BLE):
			startBLEBeacon()
		
		setupDataListener()
		
		listenForData()
		
		# temporary, listenForData will block when it is implemented
		time.sleep(120)
		
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