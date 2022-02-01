# Code from Sockets Server Demo
# by Rohan Varma
# adapted by Kyle Chin

# Code to run the server for the sockets if multiple people are playing.
import socket
import threading
from queue import Queue

HOST = "" # put your IP address here if playing on multiple computers
PORT = 50003
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind((HOST,PORT))
server.listen(BACKLOG)


# Thread to handle messages from client.
def handleMsgsFromClient(client, clientsMsgQueue, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(10).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                clientsMsgQueue.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            # Will crash if client goes offline.
            return

# Thread to send messages to client.
def handleMsgToClient(clientele, clientsMsgQueue):
    while True:
        # No messages = wait
        msg = clientsMsgQueue.get(True, None)
        msgList = msg.split(" ")
        senderID = msgList[0]
        details = " ".join(msgList[1:])
        if (details != ""):
            # Code to just send messages to opponent.
            if clientele[senderID]['opponent'] is not None:
                sendMsg = details + "\n"
                recvID = clientele[senderID]['opponent']
                clientele[recvID]['conn'].send(sendMsg.encode())
        clientsMsgQueue.task_done()

clientele = dict()
playerNum = 0

# Creates clientsMsgQueue queue.
clientsMsgQueue = Queue(100)
threading.Thread(target = handleMsgToClient, args = (clientele, clientsMsgQueue)).start()

# Change code to consist of just player and opponent.
while True:
    localMachine = socket.gethostbyname(socket.getfqdn())
    print("Tell clients that host IP Address is :" + localMachine)
    client, address = server.accept()
    name = 'Player_' + str(playerNum + 1)
    myID = str(playerNum)
    new_client = {'conn': client, 'name': name, 'opponent': None}
    for cID in clientele:
        if clientele[cID]['opponent'] is None:
            clientele[cID]['opponent'] = myID
            new_client['opponent'] = cID
            break
    clientele[myID] = new_client
    if clientele[myID]['opponent'] is not None:
        opponentID = clientele[myID]['opponent']
        client.send(("start %s \n" % name).encode())
        clientele[opponentID]['conn'].send(("wait \n").encode())
    else:
        client.send(("connection \n").encode())
    print("connection recieved from %s" % myID)
    threading.Thread(target = handleMsgsFromClient, args = (client ,clientsMsgQueue, myID,clientele)).start()
    playerNum += 1
