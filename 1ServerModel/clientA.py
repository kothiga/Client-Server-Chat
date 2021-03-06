import socket 
import collections
import string
import pickle
import time
import sys, select

#init seq
SEQNO = 0

# set up the client to server port
UDP_IP = raw_input("Enter The Entire IP Address of the Server: ")
UDP_PORT = 5005
 
# bind send/receive sockets 
sockr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sockr.bind((socket.gethostbyname(socket.gethostname()), UDP_PORT + 1))
socks = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

#initialize time
START_TIME = time.time()

#this is the template for a packet
packet = {'SeqNo' : str(SEQNO), 'Type' : " ", 'My_ID' : "NULL", 'Dest_ID' : "NULL", 'Payload' : " "}
print(chr(27) + "[2J")
ID = raw_input("Enter a Username : ")

###############################
# returns the string SEND
###############################
def SEND():
    return "SEND"

###############################
# returns the string ACK
###############################
def ACK():
    return "ACK"

###############################
# returns the string GET
###############################
def GET():
    return "GET"

###############################
# returns the string HNDS
###############################
def HNDS():
    return "HNDS"

###############################
# returns the string SEQ
###############################
def SEQ() : 
    SEQNO = SEQNO + 1
    return SEQNO

###############################
# A function for sending 
# a get request
###############################
def getRequest():
    GETREQUEST = packet
    GETREQUEST['SeqNo'] = str(SEQNO)
    GETREQUEST['Type'] = GET()
    GETREQUEST['My_ID'] = ID
    GETREQUEST['Dest_ID'] = ID
    GETREQUEST['Payload'] = "0"
    
    socks.sendto(pickle.dumps(GETREQUEST), (UDP_IP, UDP_PORT)) 
    receiveMail()

###############################
# A function for sending 
# Ack of a received packet
###############################
def sendAck(seq, dest):
    ACKREQUEST = packet
    ACKREQUEST['SeqNo'] = seq
    ACKREQUEST['Type'] = ACK()
    ACKREQUEST['My_ID'] = dest
    ACKREQUEST['Dest_ID'] = ID
    ACKREQUEST['Payload'] = "0"
    socks.sendto(pickle.dumps(ACKREQUEST), (UDP_IP, UDP_PORT))
    
###############################
# A function to listen for 
# incoming packets
###############################
def receiveMail() :

    data, addr = sockr.recvfrom(1024)
    DATA = pickle.loads(data)
    while DATA['SeqNo'] != "-1":
        if(DATA['Type'] == "SEND"):
            print "\nFrom", DATA['My_ID'], ": \nMessage:", DATA['Payload'] 
        sendAck(DATA['SeqNo'], DATA['My_ID'])
        data, addr = sockr.recvfrom(1024)
        DATA = pickle.loads(data)
    
###############################################
#                  main
###############################################
Handshake = packet
Handshake['My_ID'] = ID
Handshake['Dest_ID'] = ID
Handshake['Type'] = HNDS()

socks.sendto(pickle.dumps(Handshake), (UDP_IP, UDP_PORT)) 

while True:
    print "\n\n                                      Press Enter to Begin Composing a Message: "
    while True:
        # sends a getRequest every 5 mili seconds
        if (time.time() - START_TIME)% 0.5 == 0:
            getRequest()

        # This will cause the while loop to exit if "Enter" is hit
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = raw_input()
            break
    
    # Build a packet from the Template with 
    # User specified Recipient & Message
    PACKET = packet 
    PACKET['SeqNo'] = str(SEQNO)
    PACKET['My_ID'] = ID
    PACKET['Dest_ID'] = raw_input("Enter the Username of a Recipient: ")
    PACKET['Payload'] = raw_input("Message: \n")
    PACKET['Type'] = SEND()
    
    # Send into the server
    socks.sendto(pickle.dumps(PACKET), (UDP_IP, UDP_PORT))

    # Increment the SEQNO
    SEQNO = SEQNO + 1
