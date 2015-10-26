from bluetooth import *

def run():
    uuid = "dad8bf14-b6c3-45fa-b9a7-94c1fde2e7c6"
    addr = "acfdce5ae1b8"
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
    
