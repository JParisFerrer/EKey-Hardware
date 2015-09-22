from bluetooth import *
from bluetooth.ble import BeaconService
import time

# Whether to use BLE beacon or normal bluetooth advertisement
BLE = True

# make sure we have this global variable set up
service = None

# our normal bluetooth socket
server_sock = None

# just a random uuid I generated
uuid = "dad8bf14-b6c3-45fa-b9a7-94c1fde2e7c6"

def startBLEBeacon():
	print("Starting BLE Beacon")
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
		print ("Error listening for data: %s" % e)
		raise	# throw it back up to terminate (can be changed later)
	
def processData(bytes):
	pass

def run():
	try:
		if (BLE):
			startBLEBeacon()
		
		setupDataListener()
		
		# temporary, listenForData will block when it is implemented
		time.sleep(20)
		
	except Exception as e:
		print("Exception " + e)
		
	finally:
		print("Exiting...")
		
		if (BLE):
			stopBLEBeacon()
		
run()