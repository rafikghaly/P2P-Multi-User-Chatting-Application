from pymongo import MongoClient

#Includes database operations
class DB:


    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.get_database('p2p-chat')


    # checks if an account with the username exists
    def is_account_exist(self, username):
        if self.db.accounts.count_documents({'username': username}) > 0:
            return True
        else:
            return False


    # registers a user
    def register(self, username, password):
        account = {
            "username": username,
            "password": password
        }
        self.db.accounts.insert_one(account)


    # retrieves the password for a given username
    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]


    # checks if an account with the username online
    def is_account_online(self, username):
        if self.db.online_peers.count_documents({"username": username}) > 0:
            return True
        else:
            return False


#logs in the user
    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert_one(online_peer)



    # logs out the user 
    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})


    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return (res["ip"], res["port"])
    
    # returns a list of online users
    def get_online_peers(self):
        online_peers_list = list()
        for online_peer in self.db.online_peers.find():
            online_peers_list.append(online_peer['username'])
        return online_peers_list
    
    def is_roomName_exist(self,roomName):
        if self.db.chatRooms.count_documents({'roomName': roomName}) > 0:
            return True
        else:
            return False        

    # Create Chat Room
    def createChatRoom(self, roomName,userName,userIP):
        room = {
            "roomName": roomName,
            "userNames": userName,
            "userIPs" : userIP
        }
        self.db.rooms.insert_one(room)

