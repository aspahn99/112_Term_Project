# Code from Sockets Server Demo
# by Rohan Varma
# adapted by Kyle Chin

# Code that handles the client side of sockets. 
# Deals with connecting to the server, handling and receiving messages
import socket
import threading
from queue import Queue


def connectToServer(recvMsgQueue,sendMsgQueue,host):
    PORT = 50003
    gameServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gameServer.connect((host,PORT))
    serverRecvThread = threading.Thread(target=handleMsgFromServer,args=(gameServer,recvMsgQueue))
    serverRecvThread.daemon = True
    serverRecvThread.start()

    serverSendThread = threading.Thread(target=handleMsgsToServer,args=(gameServer,sendMsgQueue))
    serverSendThread.daemon = True
    serverSendThread.start()



# Thread to receieve messages from server.
def handleMsgFromServer(gameServer, recvMsgQueue):
  gameServer.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += gameServer.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      recvMsgQueue.put(readyMsg)
      command = msg.split("\n")


# Thread to send messages to server.
def handleMsgsToServer(gameServer, sendMsgQueue):
  while True:
    msg = sendMsgQueue.get(True, None)
    gameServer.send(msg.encode())
    sendMsgQueue.task_done()