# Code that runs the AI in single play mode.

import queue
import threading
import random
import copy
import pygame
from Ship import Ship 

class GameAI(object):
    def __init__(self, recvMsgQueue, sendMsgQueue, squareSize):
        self.recvMsgQueue = recvMsgQueue
        self.sendMsgQueue = sendMsgQueue
        self.stopEvent = threading.Event()
        self.squareSize = squareSize
        self.rows = 10
        self.cols = 10
        self.computerBoard = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.playerBoard = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.ships = [[] for i in range(5)]
        self.aircraft = Ship('aircraft',(11,2),5,"images/carrier.png",self.squareSize)
        self.ships[0] = self.aircraft
        self.battleShip = Ship('battleShip',(12,2),4, "images/battle.png",self.squareSize)
        self.ships[1] = self.battleShip
        self.submarine = Ship('submarine',(13,2),3, "images/sub.png",self.squareSize)
        self.ships[2] = self.submarine
        self.destroyer = Ship('destroyer',(14,2),3, "images/destroyer.png",self.squareSize)
        self.ships[3] = self.destroyer
        self.patrolBoat = Ship('patrolboat',(15,2),2, "images/patrol.png",self.squareSize)
        self.ships[4] = self.patrolBoat
        self.selectedShip = None
        self.sunkShips = 0
        self.moves = set()
        self.checkShips = copy.copy(self.ships)
        self.pastHit = None
        self.startTime = 0
        self.sunkShipNames = []

    def receiveMsgs(self):
        while not self.stopEvent.is_set():
            try:
                recvMsg = self.recvMsgQueue.get(block=True, timeout=.1)
                self.handleRecvMsg(recvMsg[:-1])
                self.recvMsgQueue.task_done()
            except queue.Empty:
                pass

    def checkMove(self,x,y):
        if x > 9 or x < 0 or y > 9 or y < 0:
            return "invalid"
        result = self.checkHit((x,y))
        if result == 1:
            self.computerBoard[x][y] = "hit"
            return "hit"
        elif result == 0:
            self.computerBoard[x][y] = "miss"
            return "miss"
        elif result == -1:
            self.computerBoard[x][y] = "hit"
            return "sunk"

    def checkHit(self,pos):
        for ship in self.ships:
            position = ship.getFullPosition()
            if pos in position:
                ship.shipHit()
                if ship.sunkShip():
                    self.sunkShipNames.append(ship.shipName)
                    return -1
                return 1
        return 0
        
    
    def placeShips(self):
        for ship in self.ships:
            self.selectedShip = ship
            self.checkShips.remove(self.selectedShip)
            self.autoPlace()
            self.checkShips = copy.copy(self.ships)
        
    def autoPlace(self):
        length = self.selectedShip.getLength()
        x = random.randint(0,9)
        y = random.randint(0,9)
        orientation = random.randint(0,1)
        if orientation == 1:
            self.selectedShip.changeOrientation()
        self.selectedShip.moveShip((x,y))
        while not self.checkShipSpot() or not self.checkShipOnBoard():
            x = random.randint(0,9)
            y = random.randint(0,9)
            orientation = random.randint(0,1)
            if orientation == 1:
                self.selectedShip.changeOrientation()
            self.selectedShip.moveShip((x,y))
    
    def checkShipOnBoard(self):
        shipPos = self.selectedShip.getFullPosition()
        shipLength = self.selectedShip.shipLength
        for element in shipPos:
            x,y = element
            if x > 9 or x < 0 or y > 9 or y < 0:
                return False
        return True
        
    def checkShipSpot(self):
        selectedPos  = self.selectedShip.getFullPosition()
        for ship in self.checkShips:
            position = ship.getFullPosition()
            for element in selectedPos:
                if element in position:
                    return False
        return True
            
    def makeMove(self):
        while abs(pygame.time.get_ticks()-self.startTime) < 2000:
            pass
        x = random.randint(0,self.cols-1)
        y = random.randint(0,self.rows-1)
        while (x,y) in self.moves:
            x = random.randint(0,self.cols-1)
            y = random.randint(0,self.rows-1)
        self.moves.add((x,y))
        msg = "move " + str(x) + " " +str(y) + "\n"
        self.sendMsgQueue.put(msg)
    
    def makeHitMove(self,move):
        while abs(pygame.time.get_ticks()-self.startTime) < 2000:
            pass
        x,y = move
        coordMove = random.randint(0,1)
        if coordMove == 0:
            possibleX = self.possibleMoves(x)
            xIndex = random.randint(0,3)
            possibleY = [y]
            yIndex = 0
        else:
            possibleY = self.possibleMoves(y)
            yIndex = random.randint(0,3)
            possibleX = [x]
            xIndex = 0
        count = 0
        while (possibleX[xIndex], possibleY[yIndex]) in self.moves or \
        (possibleX[xIndex] < 0 or possibleX[xIndex] > self.cols-1) or \
        (possibleY[yIndex] < 0 or possibleY[yIndex] > self.rows-1):
            if count > 16:
                self.makeMove()
                break
            elif coordMove == 0:
                xIndex = random.randint(0,3)
            else:
                yIndex = random.randint(0,3)
            count += 1
        self.moves.add((possibleX[xIndex],possibleY[yIndex]))
        msg = "move " + str(possibleX[xIndex]) + " " +str(possibleY[yIndex]) + "\n"
        self.sendMsgQueue.put(msg)
    
    def possibleMoves(self, coord):
        possibleMoves = []
        possibleMoves.append(coord+1)
        possibleMoves.append(coord+2)
        possibleMoves.append(coord-1)
        possibleMoves.append(coord-2)
        return possibleMoves
    
    def handleRecvMsg(self, message):
        msg = message.split()
        command = msg[0]
        if (command == "move"):
            x = int(msg[1])
            y = int(msg[2])
            result = self.checkMove(x,y) 
            returnMsg = ""  
            if result == "invaild":
                returnMsg = "invalid \n"
            elif result == "hit":
                returnMsg = "hit " + str(x) + " " + str(y) + " \n"
            elif result == "miss":
                returnMsg = "miss " + str(x) + " " + str(y) + " \n"
            elif result == "sunk":
                returnMsg = "sunk " + str(x) + " " + str(y) + " " + self.sunkShipNames[-1] + " \n"
            if returnMsg != "":
                self.sendMsgQueue.put(returnMsg)
            self.startTime = pygame.time.get_ticks()
            if self.pastHit != None:
                self.makeHitMove(self.pastHit)
            else:
                self.makeMove()
        elif (command == "hit"):
            x = int(msg[1])
            y = int(msg[2])
            self.playerBoard[x][y] = "hit"
            self.pastHit = (x,y)
        elif (command == "miss"):
            x = int(msg[1])
            y = int(msg[2])
            self.playerBoard[x][y] = "miss"
        elif (command == "invalid"):
            pass
        elif (command == "sunk"):
            self.sunkShips +=1
            self.pastHit = None
            x = int(msg[1])
            y = int(msg[2])
            self.playerBoard[x][y] = "hit"
            if self.sunkShips == 5:
                returnMsg = "gameover \n"
                self.sendMsgQueue.put(returnMsg)
        
    def run(self):
        self.placeShips()
        self.stopEvent.clear()
        serverRecvThread = threading.Thread(target=self.receiveMsgs)
        serverRecvThread.daemon = True  
        serverRecvThread.start()
        sendMsg = 'start human computer'
        self.sendMsgQueue.put(sendMsg)

    def stop(self):
        self.stopEvent.set()