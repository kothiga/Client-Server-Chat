import thread
import socket
import pickle
import time
import signal
import multiprocessing as mp
from collections import defaultdict

#################################################################
# Variable Inits
#################################################################
UDP_IP = socket.gethostbyname(socket.gethostname())
USER_PORT = 5000
SERVER_PORT = 4000

#################################################################
# Socket Inits
#################################################################
CLIENTsendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
CLIENTreceiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVERroutSendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVERroutReceiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVERforwSendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVERforwReceiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#################################################################
# Clear Screen and Initiate Activity 
#################################################################
print(chr(27) + "[2J")
print "ACTIVITY LOG"
print "~~~~~~~~~~~~"
port = raw_input("What Server are you: ")
SERVER_PORT += int(port)
USER_PORT += int(port)

#################################################################
# Bind the Two Receiving Sockets
#################################################################
CLIENTreceiveSock.bind((UDP_IP, USER_PORT))
SERVERroutReceiveSock.bind((UDP_IP, SERVER_PORT))
SERVERforwReceiveSock.bind((UDP_IP, SERVER_PORT+20))

print UDP_IP
print SERVER_PORT

# append ###.##.###.##
"Enter The Entire IP Address of the Server: "
A = raw_input("Enter The Entire IP address of Machine i-1: ")
B = raw_input("Enter The Entire IP address of Machine i+1: ")

print A, B

IPTABLE = {}
MAILserver = defaultdict(list)

#################################################################
#              Code for ongoing communication
#                        with clients
#################################################################
def ComServer():
    
    while True:       
        if time.time()%5 == 0:
            ROUT(True)  #left
            ROUT(False) #right
            ROUT(True)  #left
            ROUT(False) #right
            ###################
            FORW(True)  #left
            FORW(True)  #left
            FORW(False) #right
            FORW(False) #right
    

#################################################################
#              Function for beginning different
#                      Routing threads
#################################################################
def ROUT(flow):
    print "In Rout"
    if flow: #flow is left
        PORT = SERVER_PORT-1
        print "flow is true"
        print PORT
        print SERVER_PORT
        if SERVER_PORT == 4001:
            PORT = 4005
        ############################
        # Start Thread for routSEND 
        # and run the routRECEIVE
        ############################
        thread.start_new_thread(routSEND, (A, PORT) )
        routRECEIVE()
           
    else: #flow is right
        PORT = SERVER_PORT+1
        print "flow is false"
        print PORT
        print SERVER_PORT
        if SERVER_PORT == 4005:
            PORT = 4001
        ############################
        # Start Thread for routSEND 
        # and run the routRECEIVE
        ############################
        thread.start_new_thread(routSEND, (B, PORT) )
        routRECEIVE()
   

#################################################################
#               Function for sending routing
#                       IPTABLES
#################################################################
def routSEND(i, port):
    print "trying to send to ", i, " ", port
    SERVERroutSendSock.sendto(pickle.dumps(IPTABLE), (i, port))
    print "Sent Something"


#################################################################
#              Function for receiving routing
#                        IPTABLES
#################################################################
def routRECEIVE():
    print "trying to receive"
    pIPTABLE, addr = SERVERroutReceiveSock.recvfrom(1024)
    table = pickle.loads(pIPTABLE)
    print "Got Something"

    for key in table:
        if key not in IPTABLE:
            IPTABLE[key] = addr[0]
            print IPTABLE


#################################################################
#  Function for forwarding mail that does not belong to 
#  the server based on a True/False value
#   True : Left
#  False : Right
#################################################################
def FORW(flow):
    print "In Forw"
    if flow:

        PORT = SERVER_PORT+19
        print "flow is true"
        print PORT
        print SERVER_PORT
        if SERVER_PORT+20 == 4021:
            PORT = 4025
        ############################
        # Start Thread for forwSEND 
        # and run the forwRECEIVE
        ############################
        thread.start_new_thread(forwSEND, (A, PORT) )
        forwRECEIVE()
           
    else:
        PORT = SERVER_PORT+21
        print "flow is false"
        print PORT
        print SERVER_PORT
        if SERVER_PORT+20 == 4025:
            PORT = 4021
        ############################
        # Start Thread for forwSEND 
        # and run the forwRECEIVE
        ############################
        thread.start_new_thread(forwSEND, (B, PORT) )
        forwRECEIVE()
    

#################################################################
# Function for sending Specific Methods to a left or right
# neighbor, and their receiving port
#################################################################
def forwSEND(i, port):
    OUTBOX = defaultdict(list)

    #########################
    # Iterate through the 
    # IPtable to see if there
    # are any messages for 
    # Left/Right Server
    #########################
    for key in IPTABLE:
        if i == IPTABLE[key]:
            OUTBOX[key] = MAILserver[key]
            del MAILserver[key]
    
    #########################
    # Send the messages on 
    # the passed in IP + port
    #########################
    print "trying to send mail to ", i, " ", port
    SERVERforwSendSock.sendto(pickle.dumps(OUTBOX), (i, port))
    print "Sent mail"
   
 
#################################################################
# Function for Receiving Mail from a neighbor
# If the received mail's destination has a mail box
# The server will put the mail in its box, until a get request is sent
#################################################################
def forwRECEIVE():
    print "trying to receive"
    pBOX, addr = SERVERforwReceiveSock.recvfrom(1024)
    BOX = pickle.loads(pBOX)
    print "Got Something"

    for key in BOX:
        if key in MAILserver:
            MAILserver[key] = MAILserver[key] + BOX[key]
            
        else:
            MAILserver[key] = BOX[key]


#################################################################
#                          main
#################################################################

startINPUT = raw_input("Enter Anything to Start: ")
thread.start_new_thread(ComServer, () )

# for the first
pPACKET, addr = CLIENTreceiveSock.recvfrom(1024) # buffer size is 1024 bytes
PACKET = pickle.loads(pPACKET)

IPTABLE[PACKET['My_ID']] = addr[0]

MAILserver.setdefault(PACKET['My_ID'], []).append(PACKET)

while True:
    pPACKET, addr = CLIENTreceiveSock.recvfrom(1024) # buffer size is 1024 bytes
    PACKET = pickle.loads(pPACKET)
    
    if PACKET['Type'] == "HNDS":
        IPTABLE[PACKET['My_ID']] = addr[0]

    if PACKET['Type'] == "GET":
        boxlength = len(MAILserver[PACKET['My_ID']])
        while(boxlength >= 0):
            if boxlength == 0:
                SENDINGPACK = {'SeqNo' : "-1", 'Type' : "HNDS", 'My_ID' : "SERVER", 'Dest_ID' : PACKET['My_ID'], 'Payload' : "NOMOREMAIL"}
                CLIENTsendSock.sendto(pickle.dumps(SENDINGPACK), (IPTABLE[SENDINGPACK['Dest_ID']], USER_PORT + 10))
                boxlength -= 1
                
            else:
                # get message
                SENDING = MAILserver[PACKET['My_ID']].pop(0)

                #while True:
                CLIENTsendSock.sendto(pickle.dumps(SENDING), (IPTABLE[SENDING['Dest_ID']], USER_PORT + 10))
                print "sent"

                # wait for ack
                ACKSENT, addr = CLIENTreceiveSock.recvfrom(1024)                     

                # decode
                received = pickle.loads(ACKSENT)
                print("Recieved an ACK from : "), received['My_ID'], 

                # if its an ACK
                if received['Type'] == "ACK":
                    boxlength -= 1
                
    if PACKET['Type'] == "SEND":
       if PACKET['Dest_ID'] in MAILserver:
           MAILserver[PACKET['Dest_ID']].append(PACKET)
       else:
           MAILserver.setdefault(PACKET['Dest_ID'], []).append(PACKET)



