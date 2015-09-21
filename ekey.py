from bluetooth import *
from bluetooth.ble import BeaconService
import time

# make sure we have this global variable set up
service = None

# just a random uuid I generated
uuid = "dad8bf14-b6c3-45fa-b9a7-94c1fde2e7c6"

def startBLEBeacon():
	global service = BeaconService()
	
	service.start_advertising(uuid, 		# uuid of server
		1,									# 'major' - no idea what this does (1 - 65535)
		1,									# 'minor' - no idea what this does either (1 - 65535)
		1,									# txPower, power of signal (-20 - 4)
		200)								# interval - not exactly sure what this does either, but this is the default
	
def stopBLEBeacon():
	service.stop_advertising()
	
def listenForData():
	# TODO: listen for data
	pass	

def run():
	try:
		startBLEBeacon()
		
		listenForData()
		
		# temporary, listenForData will block when it is implemented
		time.sleep(20)
		
	except e:
		print("Exception " + e)
		
	finally:
		stopBLEBeacon()