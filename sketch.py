from bluetooth import *

def run():
	uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
	addr = ""
	service_matches = find_service( uuid = uuid, address = addr )
	
	first_match = service_matches[0]
	port = first_match["port"]
	name = first_match["name"]
	host = first_match["host"]

	print("connecting to \"%s\" on %s" % (name, host))

	# Create the client socket
	sock=BluetoothSocket( RFCOMM )
	sock.connect((host, port))
	
	print("connected.  type stuff")
	while True:
    	data = input()
    	if len(data) == 0: break
    	sock.send(data)

	sock.close()
	
run()
	
