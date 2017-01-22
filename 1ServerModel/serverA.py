import select
import socket
import pickle
from collections import defaultdict

UDP_IP = socket.gethostbyname(socket.gethostname())
UDP_PORT = 5005

SENsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
RECsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
RECsock.bind((UDP_IP, UDP_PORT))

print(chr(27) + "[2J")
print "ACTIVITY LOG"
print "~~~~~~~~~~~~"
print UDP_IP

#//////////////////////////////
#   Build The Dictionaries
#//////////////////////////////

# for the first
pPACKET, addr = RECsock.recvfrom(1024) # buffer size is 1024 bytes
PACKET = pickle.loads(pPACKET)

IPTABLE = {PACKET['My_ID'] : addr[0]}
MAILserver = defaultdict(list)

MAILserver.setdefault(PACKET['My_ID'], []).append(PACKET)

while True:
    pPACKET, addr = RECsock.recvfrom(1024) # buffer size is 1024 bytes
    PACKET = pickle.loads(pPACKET)
    
    if PACKET['Type'] == "HNDS":
        IPTABLE[PACKET['My_ID']] = addr[0]
	print IPTABLE

    if PACKET['Type'] == "GET":
        boxlength = len(MAILserver[PACKET['My_ID']])
        while(boxlength >= 0):
            if boxlength == 0:
                SENDINGPACK = {'SeqNo' : "-1", 'Type' : "HNDS", 'My_ID' : "SERVER", 'Dest_ID' : PACKET['My_ID'], 'Payload' : "NOMOREMAIL"}
                SENsock.sendto(pickle.dumps(SENDINGPACK), (IPTABLE[SENDINGPACK['Dest_ID']], UDP_PORT + 1))
                boxlength -= 1
		        
            else:
                # get message
                SENDING = MAILserver[PACKET['My_ID']].pop(0)

                #while True:
                SENsock.sendto(pickle.dumps(SENDING), (IPTABLE[SENDING['Dest_ID']], UDP_PORT + 1))
                print "sent"

                # wait for ack
                ACKSENT, addr = RECsock.recvfrom(1024)                     

                # decode
                received = pickle.loads(ACKSENT)
                print("Recieved an ACK from : "), received['My_ID'], 

                # if its an ACK
                if received['Type'] == "ACK":
                    boxlength -= 1
		    print IPTABLE
                
    
    if PACKET['Type'] == "SEND":
       if PACKET['Dest_ID'] in MAILserver:
           MAILserver[PACKET['Dest_ID']].append(PACKET)
       else:
           MAILserver.setdefault(PACKET['Dest_ID'], []).append(PACKET)

