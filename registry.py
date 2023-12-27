
'''
    ##  Implementation of registry
    ##  150114822 - Eren Ulaş
'''

from socket import *
import threading
import select
import logging
import db

# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created
class ClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.ip = ip
        # port number of the connected peer
        self.port = port
        # socket of the peer
        self.tcpClientSocket = tcpClientSocket
        hostname = gethostname()
        IPAddr = gethostbyname(hostname)
        self.udpSocket = socket(AF_INET,SOCK_DGRAM) #udp socket for chat room broadcasting
        self.udpSocket.bind((IPAddr,0))
        # username, online status and udp server initializations
        self.username = None
        self.isOnline = True
        self.udpServer = None
        print("\033[35m")
        print("New thread started for " + ip + ":" + str(port))

    # main of the thread
    def run(self):
        # locks for thread which will be used for thread synchronization
        self.lock = threading.Lock()
        print("\033[35m")
        print("Connection from: " + self.ip + ":" + str(port))
        print("\033[35m")
        print("IP Connected: " + self.ip)
        
        while True:
            try:
                # waits for incoming messages from peers
                message = self.tcpClientSocket.recv(1024).decode().split(":")
                logging.info("Received from " + self.ip + ":" + str(self.port) + " -> " + " ".join(message))            
                #   Create Account   #
                if message[0] == "CRT":
                    # Create Account is sent to peer,
                    # if an account with this username already exists
                    if db.is_account_exist(message[1]):
                        response = "EXST"
                        print("\033[35m")
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)  
                        self.tcpClientSocket.send(response.encode())
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        db.register(message[1], message[2])
                        response = "OK"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                #   LOGIN    #
                elif message[0] == "LOG":
                    # WCRE is sent to peer,
                    # if an account with the username does not exist
                    if not db.is_account_exist(message[1]):
                        response = "WCRE"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                    # AON is sent to peer,
                    # if an account with the username already online
                    elif db.is_account_online(message[1]):
                        response = "AON"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())
                    # OK is sent to peer,
                    # if an account with the username exists and not online
                    else:
                        # retrieves the account's password, and checks if the one entered by the user is correct
                        retrievedPass = db.get_password(message[1])
                        # if password is correct, then peer's thread is added to threads list
                        # peer is added to db with its username, port number, and ip address
                        if retrievedPass == message[2]:
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                tcpThreads[self.username] = self
                            finally:
                                self.lock.release()

                            db.user_login(message[1], self.ip, message[3])
                            # OK is sent to peer,
                            # and a udp server thread is created for this peer, and thread is started
                            # timer thread of the udp server is started
                            response = "OK"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                            self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                            self.udpServer.start()
                            self.udpServer.timer.start()
                        # if password not matches and then WCRE response is sent
                        else:
                            response = "WCRE"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                #   LOGOUT  #
                elif message[0] == "LGO":
                    # if user is online,
                    # removes the user from onlinePeers list
                    # and removes the thread for this user from tcpThreads
                    # socket is closed and timer thread of the udp for this
                    # user is cancelled
                    if len(message) > 1 and message[1] is not None and db.is_account_online(message[1]):
                        db.user_logout(message[1])
                        self.lock.acquire()
                        try:
                            if message[1] in tcpThreads:
                                del tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print("\033[35m")
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break
                #   SEARCH  #
                elif message[0] == "SRCH":
                    # checks if an account with the username exists
                    if db.is_account_exist(message[1]):
                        # checks if the account is online
                        # and sends the related response to peer
                        if db.is_account_online(message[1]):
                            peer_info = db.get_peer_ip_port(message[1])
                            response = "IP: " + peer_info[0] + ":" + peer_info[1]
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                        else:
                            response = "NON"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                            self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist 
                    else:
                        response = "NOTEXST"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())


                elif message[0] == "GOP":
                    online_peers = db.get_online_peers()
                    response = "NOP:" + str(len(online_peers)) + "\nPeers:"
                    for peer in online_peers:
                        response += peer
                        response += "\n"
                    
                    self.tcpClientSocket.send(response.encode())     
                
                elif message[0] == "CCR":
                    if db.is_roomName_exist(message[1]):
                        response = "EXST"
                        print("\033[35m")
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)  
                        self.tcpClientSocket.send(response.encode())
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        db.createChatRoom(message[1],message[2],self.ip,message[3])
                        response = "OK"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response) 
                        self.tcpClientSocket.send(response.encode())

                elif message[0] == "JCR":
                    if not db.is_roomName_exist(message[1]):
                        response = "NOTEXST"
                        print("\033[35m")
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        print('ana da5lt')
                        db.addChatRoomMember(message[1],message[2],self.ip,message[3])
                        members = db.getRoomMembers(message[1])
                        IPs = members["userIPs"]
                        names = members["userNames"]
                        ports = members["userPorts"]
                        # logging.info(members)
                        # logging.info(str(IPs))
                        # logging.info(names)
                        # logging.info(ports)
                        # logging.info("Length of IPs: " + str(len(IPs)))
                        # logging.info("Length of names: " + str(len(names)))
                        # logging.info("Length of ports: " + str(len(ports)))

                        for i in range(len(IPs)):
                            if names[i] == message[2]:
                                continue
                            update = "JUPDT:" + message[2] + ":" + self.ip + ":" + str(message[3])
                            print("message is ",update)
                            print("IP is ",IPs[i], "port is ",ports[i])
                            self.udpSocket.sendto(update.encode(),(IPs[i],int(ports[i])))
                        response = "OK\n"
                        for i in range(len(IPs)):
                            response += (names[i] + ":" + str(IPs[i]) + ":" + str(ports[i]))
                            if i < len(IPs) - 1:  # If it's not the last iteration
                                response += "\n"

                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + str(response))
                        try:
                            self.tcpClientSocket.send(response.encode())
                        except Exception as e:
                            logging.error("Error sending message: " + str(e))

                elif message[0] == "XUPDT":
                    members = db.getRoomMembers(message[1])
                    IPs = members["userIPs"]
                    names = members["userNames"]
                    ports = members["userPorts"]
                    remove = "XUPDT:" + message[2]+ ":" + self.ip + ":" + str(message[3])
                    db.removeRoomMember(message[1],message[2],self.ip,message[3])
                    for i in range(len(IPs)):
                        if names[i] == message[2]:
                            continue
                        self.udpSocket.sendto(remove.encode(),(IPs[i],int(ports[i])))
                    if len(IPs) == 1:
                        db.removeRoom(message[1])

            except OSError as oErr:
                pass
                #logging.error("OSError: {0}".format(oErr)) 


    # function for resettin the timeout for the udp timer thread
    def resetTimeout(self):
        self.udpServer.resetTimer()

                            
# implementation of the udp server thread for clients
class UDPServer(threading.Thread):


    # udp server thread initializations
    def __init__(self, username, clientSocket):
        threading.Thread.__init__(self)
        self.username = username
        # timer thread for the udp server is initialized
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.tcpClientSocket = clientSocket
    

    # if hello message is not received before timeout
    # then peer is disconnected
    def waitHelloMessage(self):
        if self.username is not None:
            db.user_logout(self.username)
            if self.username in tcpThreads:
                del tcpThreads[self.username]
        self.tcpClientSocket.close()
        print("\033[31m")
        print("Removed " + self.username + " from online peers")


    # resets the timer for udp server
    def resetTimer(self):
        self.timer.cancel()
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.timer.start()


# tcp and udp server port initializations
print("\033[35m")
print("Registy started...")
port = 15600
portUDP = 15500

# db initialization
db = db.DB()

# gets the ip address of this peer
# first checks to get it for windows devices
# if the device that runs this application is not windows
# it checks to get it for macos devices
hostname=gethostname()
try:
    host=gethostbyname(hostname)
except gaierror:
    import netifaces as ni
    host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

print("\033[35m")
print("Registry IP address: " + host)
print("\033[35m")
print("Registry port number: " + str(port))

# onlinePeers list for online account
onlinePeers = {}
# accounts list for accounts
accounts = {}
# tcpThreads list for online client's thread
tcpThreads = {}

#tcp and udp socket initializations
tcpSocket = socket(AF_INET, SOCK_STREAM)
udpSocket = socket(AF_INET, SOCK_DGRAM)
tcpSocket.bind((host,port))
udpSocket.bind((host,portUDP))
tcpSocket.listen(5)

# input sockets that are listened
inputs = [tcpSocket, udpSocket]

# log file initialization
logging.basicConfig(filename="registry.log", level=logging.INFO)

# as long as at least a socket exists to listen registry runs
while inputs:
    print("\033[35m")
    print("Listening for incoming connections...")
    # monitors for the incoming connections
    readable, writable, exceptional = select.select(inputs, [], [])
    for s in readable:
        # if the message received comes to the tcp socket
        # the connection is accepted and a thread is created for it, and that thread is started
        if s is tcpSocket:
            tcpClientSocket, addr = tcpSocket.accept()
            newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
            newThread.start()
        # if the message received comes to the udp socket
        elif s is udpSocket:
            # received the incoming udp message and parses it
            message, clientAddress = s.recvfrom(1024)
            message = message.decode().split()
            # checks if it is a hello message
            if message[0] == "HELLO":
                # checks if the account that this hello message 
                # is sent from is online
                if message[1] in tcpThreads:
                    # resets the timeout for that peer since the hello message is received
                    tcpThreads[message[1]].resetTimeout()
                    print("\033[35m")
                    print("Hello is received from " + message[1])
                    logging.info("Received from " + clientAddress[0] + ":" + str(clientAddress[1]) + " -> " + " ".join(message))
                    
# registry tcp socket is closed
tcpSocket.close()

