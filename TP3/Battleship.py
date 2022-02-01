# Template for pygame starter code from Lukas Peraza's code for F15 Pygame
# Optional Lecture 11/11/15
# Code for text box based on 
# https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame
# Code for explosions based on
# https://stackoverflow.com/questions/14044147/animated-sprite-from-few-images
# File for how to use a json file
# https://www.copterlabs.com/json-what-it-is-how-it-works-how-to-use-it/

# Main battleship file. File that runs the whole game.
import argparse
import pygame
import copy
import random
import sys
import json
import time
import os
from queue import Queue
from Board import Board
from Ship import Ship
from Player import Player
import Client
from Battleship_AI1 import GameAI
from Explosion import Explosion

parser = argparse.ArgumentParser(description='Client')
parser.add_argument('-i', action='store', dest='host', type=str,\
default='127.0.01', help='The IP Address of the host computer, Default: 127.0.01')
args = parser.parse_args()


class Battleship(object):
    def init(self, screen):
        self.recvMsgQueue = Queue(100)
        self.sendMsgQueue = Queue(100)
        self.gameServer = None
        self.serverRecvThread = None
        self.serverSendThread = None
        self.backgroundImg = pygame.transform.scale(pygame.image.load('images/background.jpg').convert(),(self.height,self.width))
        self.backgroundImg.set_alpha(128)
        self.startImg = pygame.transform.scale(pygame.image.load('images/battleship.jpg'), (self.height,self.width))
        self.shipImg = pygame.transform.scale(pygame.image.load('images/ship.jpg'),(self.height//2,self.width//2))
        self.winImg = pygame.transform.scale(pygame.image.load('images/winner.jpg'),(self.height,self.width))
        self.loseImg = pygame.transform.scale(pygame.image.load('images/loser.jpg'),(self.height,self.width))
        self.instructionsImg = pygame.transform.scale(pygame.image.load('images/instructions.jpg'),(self.height,self.width))
        self.rows = 10
        self.cols = 10
        self.playerBoard = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.opponentBoard = [[None for col in range(self.cols)] for row in range(self.rows)]
        self.state = "startScreen"
        self.mouseX = 0
        self.mouseY = 0
        self.instructions = None
        self.playAgainLost = None
        self.playAgainWon = None
        self.multiPlay = None
        self.singlePlay = None
        self.shipsReady = False
        self.squareSize = (self.width//2-40)//10
        self.ships = [[] for i in range(5)]
        self.aircraft = Ship('aircraft',(11,2),5,"images/carrier.png",self.squareSize)
        self.ships[0] = self.aircraft
        self.battleShip = Ship('battleship',(12,2),4, "images/battle.png",self.squareSize)
        self.ships[1] = self.battleShip
        self.submarine = Ship('submarine',(13,2),3, "images/sub.png",self.squareSize)
        self.ships[2] = self.submarine
        self.destroyer = Ship('destroyer',(14,2),3, "images/destroyer.png",self.squareSize)
        self.ships[3] = self.destroyer
        self.patrolBoat = Ship('patrolboat',(15,2),2, "images/patrol.png",self.squareSize)
        self.ships[4] = self.patrolBoat
        self.highlightedSquares = []
        self.board = Board(self.playerBoard, self.opponentBoard, self.width,self.height, \
        self.ships, self.highlightedSquares)
        self.selectedShip = None
        self.shipsPlaced = 0
        self.checkShips = copy.copy(self.ships)
        self.sunkShips = 0
        self.Player = Player(self.ships, self.playerBoard, self.squareSize, self.sunkShips)
        self.waitTurn = False
        self.message = None
        self.startTime = 0
        self.AI = GameAI(self.sendMsgQueue, self.recvMsgQueue, self.squareSize)
        self.messageWait = False
        self.colorInactive = pygame.Color('lightskyblue3')
        self.colorActive = pygame.Color('dodgerblue2')
        self.color = self.colorInactive
        self.inputBox = pygame.Rect(self.width-310, self.height-92, 300, 32)
        self.outputBox = pygame.Rect(self.width-310,self.height-42, 300, 32)
        self.nameBox = pygame.Rect(self.width//3.5,self.height//2.5,300,32)
        self.textActive = False
        self.textFull = False
        self.nameActive = False
        self.nameFull = False
        self.textInput = ''
        self.nameInput = ''
        self.textOutput = ''
        self.highScore = 9999999999999
        self.highName = ""
        self.boomHit = Explosion("images/exp2a.png",64,64)
        self.boomSunk = Explosion("images/exp4a.png", 256,256)
        self.hit = (0,0)
        self.sunk = (0,0)
        self.gameTime = 0 
        self.gameStartTime = 0
        self.hitSprite = self.boomHit.loadExplosion()
        self.sunkSprite = self.boomSunk.loadExplosion()
        self.hitCounter = 0
        self.sunkCounter = 0
        self.nameSet = False
        self.playerScores = dict()
        self.sunkShipName = ""
        self.playAgain = False
        self.playing  = True
    
    def mousePressed(self, pos, screen):
        if self.state == "startScreen":
            x,y = pos
            pos = (x-self.width//3, y-self.height//2.5)
            if self.instructions.collidepoint(pos):
                self.state = "instructions"
            pos = (x-self.width//3, y-self.height//1.62)
            if self.multiPlay.collidepoint(pos):
                self.state = "player1"
                self.message = "gameSetUp"
            else:
                pos = (x-self.width//3.1, y-self.height//1.18)
                if self.singlePlay.collidepoint(pos):
                    self.state = "singlePlay"
                    self.message = "gameSetUp"
        elif self.state == "gameLost":
            x,y = pos
            pos = (x-self.width//3.1,y-self.height//1.2)
            if self.playAgainLost.collidepoint(pos):
                self.playAgain = True
                self.playing = False
                self.state = "startScreen"
        elif self.state == "gameWon":
            x,y = pos
            pos = (x-self.width//2.8, y-self.height//1.4)
            if self.playAgainWon.collidepoint(pos):
                self.playAgain = True
                self.playing = False
                self.state = "startScreen"
        elif (self.state == "player1" or self.state =="singlePlay") and not self.waitTurn:
            msg = ""
            x,y = self.translateCoord(pos)
            if x > -1 and x < 10 and y > -1 and y < 10:
                msg = "move " + str(x) + " " +str(y) + "\n"
                if (msg != ""):
                    self.sendMsgQueue.put(msg)
        
    
    def translateCoord(self, pos):
        x,y = pos
        x = (x-(20+11*self.squareSize))//(self.squareSize)
        y = (y-20)//(self.squareSize)
        return(y,x)
            
    def mouseReleased(self, x, y):
        pass

    def mouseMotion(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass

    
    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_RETURN and self.checkAllShips() and self.state == "player1":
            self.gameStartTime = pygame.time.get_ticks()
            Client.connectToServer(self.recvMsgQueue,self.sendMsgQueue,args.host)
        elif keyCode == pygame.K_RETURN and self.checkAllShips() and self.state == "singlePlay":
            self.gameStartTime = pygame.time.get_ticks()
            self.AI.run()
        elif keyCode == pygame.K_SPACE and self.selectedShip != None:
            self.selectedShip.changeOrientation()
            del self.board.highlightedSquares[:]
            self.boardOverlap()
        elif self.state == "instructions" and keyCode == pygame.K_b :
            self.state = "startScreen"
        elif keyCode == pygame.K_a and (self.state == "player1" or self.state == "singlePlay"):
            for ship in self.ships:
                self.selectedShip = ship
                self.checkShips.remove(self.selectedShip)
                self.autoPlace()
                self.checkShips = copy.copy(self.ships)
        
    def checkAllShips(self):
        for ship in self.ships:
            shipPos = ship.getFullPosition()
            for element in shipPos:
                x,y = element
                if x > 9 or x < 0 or y > 9 or y < 0:
                    self.message = "missingShips"
                    return False
        return True
        

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
        index = self.ships.index(self.selectedShip)
        checkShips = self.ships[0:index] + self.ships[index+1:]
        for ship in checkShips:
            position = ship.getFullPosition()
            for element in selectedPos:
                if element in position:
                    return False
        return True
        checkShips = self.ships
        
    def keyReleased(self, keyCode, modifier):
        pass
    

    def displayMessage(self,screen,message):
        if self.state == "player1" or self.state == "singlePlay":
            text1 = ""
            text2 = ""
            text3 = ""
            if message == "wait":
                text1 = "Waiting for"
                text2 = "opponent..."
            elif message == "opponentHit":
                text1 = "You hit one of" 
                text2 = "the opponent's ships!"
            elif message == "opponentMiss":
                text1 = "You missed!"
                text2 = ""
            elif message == "opponentSunk":
                text1 = "You sunk the" 
                text2 = "opponents " + self.sunkShipName 
            elif message == "playerHit":
                text1 = "One of your ships" 
                text2 = "have been hit!"
            elif message == "playerMiss":
                text1 = "The opponent missed!"
                text2 = ""
            elif message == "playerSunk":
                text1 = "Your " + self.sunkShipName 
                text2 = " has sunk"
            elif message == "start":
                text1 = "Your move player"
                text2 = ""
            elif message == "missingShips":
                text1 = "Please place all"
                text2 = "ships on the board"
            elif message == "connectionWait":
                text1 = "Waiting for another" 
                text2 = "player to connect..."
            elif message == "gameSetUp":
                text1 = "Place your ships to begin"
                text2 = "Press a to auto place"
                text3 = "Press enter to begin"
            if self.messageWait == False:
                basicFont = pygame.font.Font(None,35)
                messageText1 = basicFont.render(text1, True, (0,0,0))
                screen.blit(messageText1, [self.width//2,self.height//1.7])
                messageText2 = basicFont.render(text2, True, (0,0,0))
                screen.blit(messageText2, [self.width//2,self.height//1.6])
                messageText3 = basicFont.render(text3, True, (0,0,0))
                screen.blit(messageText3, [self.width//2,self.height//1.5])
            else:
                if abs(pygame.time.get_ticks()-self.startTime) < 1500:
                    basicFont = pygame.font.Font(None,35)
                    messageText1 = basicFont.render(text1, True, (0,0,0))
                    screen.blit(messageText1, [self.width//2,self.height//1.7])
                    messageText2 = basicFont.render(text2, True, (0,0,0))
                    screen.blit(messageText2, [self.width//2,self.height//1.6])
                    messageText3 = basicFont.render(text3, True, (0,0,0))
                    screen.blit(messageText3, [self.width//2,self.height//1.5])
                else:
                    if self.waitTurn == True:
                        self.message = "wait"
                    else:
                        self.message = "start"
                    self.messageWait = False
                
    
    def timerFired(self, dt, screen):
        while (self.recvMsgQueue.qsize() > 0):
            msg = self.recvMsgQueue.get(False)
            msg = msg.split()
            command = msg[0]
            if (command == "move"):
                self.waitTurn = False
                x = int(msg[1])
                y = int(msg[2])
                result = self.Player.checkMove(x,y) 
                returnMsg = ""  
                if result == "invaild":
                    returnMsg = "invalid \n"
                elif result == "hit":
                    returnMsg = "hit " + str(x) + " " + str(y) + " \n"
                    self.hitCounter = len(self.hitSprite)
                    self.hit = (x,y)
                    self.message = "playerHit"
                    self.startTime = pygame.time.get_ticks()
                elif result == "miss":
                    returnMsg = "miss " + str(x) + " " + str(y) + " \n"
                    self.message = "playerMiss"
                    self.startTime = pygame.time.get_ticks()
                elif result == "sunk":
                    returnMsg = "sunk " + str(x) + " " + str(y) +\
                    " " + self.Player.sunkShipNames[-1] + " \n"
                    self.sunk = (x,y)
                    self.sunkShipName = self.Player.sunkShipNames[-1]
                    self.sunkCounter = len(self.sunkSprite)
                    self.message = "playerSunk"
                    self.startTime = pygame.time.get_ticks()
                if returnMsg != "":
                    self.sendMsgQueue.put(returnMsg)
                self.messageWait = True
            elif (command == "message"):
                self.textOutput = ""
                for i in range(1,len(msg)):
                    self.textOutput += msg[i] + " "
            elif (command == "connection"):
                self.message = "connectionWait"
            elif (command == "start"):
                self.message = "start"
            elif (command == "wait"):
                self.waitTurn = True
                self.message = "wait"
                self.startTime = pygame.time.get_ticks()
            elif (command == "hit"):
                x = int(msg[1])
                y = int(msg[2])
                self.opponentBoard[x][y] = "hit"
                self.waitTurn = True
                self.message = "opponentHit"
                self.startTime = pygame.time.get_ticks()
                self.messageWait = True
            elif (command == "miss"):
                x = int(msg[1])
                y = int(msg[2])
                self.opponentBoard[x][y] = "miss"
                self.waitTurn = True
                self.message = "opponentMiss"
                self.startTime = pygame.time.get_ticks()
                self.messageWait = True
            elif (command == "invalid"):
                self.message = "invalid"
                self.startTime = pygame.time.get_ticks()
            elif (command == "sunk"):
                self.waitTurn = True
                self.message = "opponentSunk"
                self.startTime = pygame.time.get_ticks()
                self.messageWait = True
                self.sunkShips +=1
                x = int(msg[1])
                y = int(msg[2])
                self.sunkShipName = msg[3]
                self.opponentBoard[x][y] = "hit"
                if self.sunkShips == 5:
                    self.state = "gameWon"
                    self.message = None
                    self.gameTime = pygame.time.get_ticks()-self.gameStartTime
                    returnMsg = "gameover \n"
                    self.sendMsgQueue.put(returnMsg)
            elif (command == "gameover"):
                self.gameTime = pygame.time.get_ticks()-self.gameStartTime
                self.state = "gameLost"
                self.message = None
            self.recvMsgQueue.task_done()
        

    def drawStartScreen(self, screen):
        screen.blit(self.startImg,[0,0])
        screen.blit(self.shipImg,[self.width//4.7,self.height//3.95])
        screen.blit(self.shipImg,[self.width//4.7,self.height//2.12])
        screen.blit(self.shipImg,[self.width//4.7,self.height//1.44])
        basicFont = pygame.font.Font(None,48)
        instructionsText = basicFont.render('Instructions', True, (255,0,0))
        self.instructions = pygame.Surface.get_rect(instructionsText)
        screen.blit(instructionsText, [self.width//3,self.height//2.5])
        multiText = basicFont.render('Multi Player', True, (255,0,0))
        self.multiPlay = pygame.Surface.get_rect(multiText)
        screen.blit(multiText, [self.width//3,self.height//1.62])
        singleText = basicFont.render('Single Player', True, (255,0,0))
        self.singlePlay = pygame.Surface.get_rect(singleText)
        screen.blit(singleText, [self.width//3.1,self.height//1.18])

      
    def drawInstructionsScreen(self, screen):
        screen.blit(self.instructionsImg, [0,0])
        instructionsFont = pygame.font.Font(None,54)
        instructionsTxt = instructionsFont.render('Instructions', True, (255,255,255))
        screen.blit(instructionsTxt,[self.width//3.2,self.height//15])
        font = pygame.font.Font(None,30)
        txt1 = font.render('-Each player has 5 ships placed secretly on the board',True,(255,255,255))
        screen.blit(txt1,[10,self.height//7])
        txt2 = font.render('-The 5 ships are a battleship, a destroyer,a patrol boat, ', True,(255,255,255))
        screen.blit(txt2,[10,self.height//5.5])
        txt3 = font.render('an aircraft carrier and a submarine ', True,(255,255,255))
        screen.blit(txt3,[60,self.height//4.7])
        txt4 = font.render('-The goal of the game is to sink all the opponents ships ', True,(255,255,255))
        screen.blit(txt4,[10,self.height//4])
        txt5 = font.render('-To sink a ship, you must hit all the squares in the ship', True,(255,255,255))
        screen.blit(txt5,[10,self.height//3.45])
        txt6 = font.render('-A battleship has 4 squares, a destroyer has 3,', True,(255,255,255))
        screen.blit(txt6,[10,self.height//3])
        txt7 = font.render('a patrol boat has 2, an aircraft carrier has 5,', True,(255,255,255))
        screen.blit(txt7,[50,self.height//2.75])
        txt8 = font.render('and a submarine has 3', True,(255,255,255))
        screen.blit(txt8,[50,self.height//2.5])
        txt9 = font.render('-The players take turns guessing a spot on the board', True,(255,255,255))
        screen.blit(txt9,[10,self.height//2.25])
        txt10 = font.render('-To make a guess, click on that spot on the opponents board ', True,(255,255,255))
        screen.blit(txt10,[10,self.height//2.08])
        txt11 = font.render('-A white peg is a miss and a red peg is a hit', True,(255,255,255))
        screen.blit(txt11,[10,self.height//1.92])
        txt12 = font.render('-The opponents guesses will show up on your board ', True,(255,255,255))
        screen.blit(txt12,[1,self.height//1.80])
        txt13 = font.render('-If you want to send a message to your opponent ', True,(255,255,255))
        screen.blit(txt13,[10,self.height//1.70])
        txt14 = font.render('type into the top box in the lower left of the screen ', True,(255,255,255))
        screen.blit(txt14,[50,self.height//1.60])
        txt15 = font.render('your opponents message will show up in the bottom box ', True,(255,255,255))
        screen.blit(txt15,[50,self.height//1.52])
        txt16 = font.render('-In the lower right is the fastest time for a win', True,(255,255,255))
        screen.blit(txt16,[10,self.height//1.44])
        txt17 = font.render('-Try to beat that time and your opponent!', True,(255,255,255))
        screen.blit(txt17,[10,self.height//1.37])
        txt18 = font.render('-Press b to go back to the main page ', True,(255,255,255))
        screen.blit(txt18,[10,self.height//1.3])
        txt19 = instructionsFont.render('Good Luck!', True,(255,255,255))
        screen.blit(txt19,[self.width//3.2,self.height//1.2])
        
    def drawPlayer1Screen(self, screen):
        screen.blit(self.backgroundImg, [0,0])
        self.board.drawPlayer(screen)
        self.board.drawOpponent(screen)
        self.displayHighScore(screen)

    def drawWon(self,screen):
        screen.blit(self.winImg,[0,0])
        font = pygame.font.Font(None,54)
        winnerText = font.render('You Won!', True, (0,0,0))
        screen.blit(winnerText,[self.width//2.8,self.height//7])
        playAgain = font.render('Play Again?',True,(0,0,0))
        self.playAgainWon = pygame.Surface.get_rect(playAgain)
        screen.blit(playAgain,[self.width//2.8,self.height//1.4])
        nameFont = pygame.font.Font(None,40)
        nameTxtA = nameFont.render('Enter your name ',True,(0,0,0))
        screen.blit(nameTxtA,[self.width//3.5,self.height//3.2])
        nameTxtB = nameFont.render('and press enter:',True,(0,0,0))
        screen.blit(nameTxtB,[self.width//3.5,self.height//2.9])
        self.getName(screen)
    
    def getName(self,screen):
        font = pygame.font.Font(None, 24)
        textInSurface = font.render(self.nameInput, True, (0,0,0))
        if textInSurface.get_width() + 15 > self.nameBox.width:
            self.textFull = True
        else:
            self.textFull = False
        screen.blit(textInSurface, (self.nameBox.x+5, self.nameBox.y+8))
        pygame.draw.rect(screen, self.color, self.nameBox, 2)
        if self.nameSet:
            self.playerScores[self.nameInput] = str(self.gameTime)
            with open(os.path.join("topScores.json"),'w') as topScores:
                json.dump(self.playerScores,topScores)
            
    
    def drawLost(self,screen):
        pass
        screen.blit(self.loseImg,[0,0])
        font = pygame.font.Font(None, 54)
        loserText = font.render('You Lost!',True,(0,0,0))
        screen.blit(loserText,[self.width//3.1,self.height//7])
        playAgain = font.render('Play Again?',True,(0,0,0))
        self.playAgainLost = pygame.Surface.get_rect(playAgain)
        screen.blit(playAgain,[self.width//3.1,self.height//1.2])
    
    def drawText(self, screen):
        font = pygame.font.Font(None, 24)
        textInSurface = font.render(self.textInput, True, (0,0,0))
        if textInSurface.get_width() + 15 > self.inputBox.width:
            self.textFull = True
        else:
            self.textFull = False
        pygame.draw.rect(screen,(255,255,255),(self.width-310, self.height-92, 300, 32))
        pygame.draw.rect(screen,(255,255,255),(self.width-310, self.height-42, 300, 32))
        screen.blit(textInSurface, (self.inputBox.x+5, self.inputBox.y+8))
        pygame.draw.rect(screen, self.color, self.inputBox, 2)
        if self.textOutput is not '': 
            textOutSurface = font.render(self.textOutput, True, (0,0,0))
            screen.blit(textOutSurface, (self.outputBox.x + 5, self.outputBox.y + 8))
        pygame.draw.rect(screen, self.colorInactive, self.outputBox, 2)
    
    def displayHighScore(self,screen):
        with open(os.path.join("topScores.json")) as topScores:
            self.playerScores = json.load(topScores)
        for player in self.playerScores:
            if int(self.playerScores[player]) < int(self.highScore):
                self.highScore = self.playerScores[player]
                self.highName = player
        pygame.draw.rect(screen,(255,255,255),(10, self.height-110,200,100))
        font = pygame.font.Font(None, 24)
        title = font.render("High Score",True,(0,0,0))
        screen.blit(title,(55,self.height-100))
        playerTxt = font.render(self.highName +"   "+str(self.highScore),True,(0,0,0))
        screen.blit(playerTxt,(20,self.height-70))
        
        
    def redrawAll(self, screen):
        if self.state == "startScreen":
            self.drawStartScreen(screen)
            pass
        elif self.state == "instructions":
            self.drawInstructionsScreen(screen)
        elif self.state == "player1" or self.state == "singlePlay":
            if self.message != None:
                self.displayMessage(screen,self.message)
            self.drawPlayer1Screen(screen)
            if self.state == "player1":
                self.drawText(screen)
            xHit,yHit = self.hit
            xHit = (20+xHit*self.squareSize)
            yHit = (20+yHit*self.squareSize)
            self.fps = 10
            if self.hitCounter > 0:
                screen.blit(self.hitSprite[len(self.hitSprite)-self.hitCounter],(yHit,xHit))
                self.hitCounter = self.hitCounter - 1
            elif self.sunkCounter > 0:
                screen.blit(self.sunkSprite[len(self.sunkSprite)-self.sunkCounter],(20,20))
                self.sunkCounter = self.sunkCounter - 1
            pass
        elif self.state == "gameWon":
            self.drawWon(screen)
        elif self.state == "gameLost":
            self.drawLost(screen)
        if self.message != None:
            self.displayMessage(screen,self.message)

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def boardOverlap(self):
        temp = set(self.board.highlightedSquares)
        x = self.selectedShip.startLocation[0]
        y = self.selectedShip.startLocation[1]
        horizontal = self.selectedShip.horizontal
        if x > -1 and x < self.cols and y > -1 and y < self.rows:
            for i in range(self.selectedShip.shipLength):
                if horizontal:
                    self.board.highlightedSquares.append((x,y+i))
                elif not horizontal:
                    self.board.highlightedSquares.append((x+i,y))
    
    def replaceShip(self):
        overX = 0
        overY = 0
        underX = 0
        underY = 0
        shipPos = self.selectedShip.getFullPosition()
        shipLength = self.selectedShip.shipLength
        for element in shipPos:
            x,y = element
            if x > 9 :
                overX += 1
            elif x < 0:
                uderX += 1
            elif y > 9:
                overY += 1
            elif y < 0:
                underY += 1
        x,y = self.selectedShip.startLocation
        if overX > 0:
            self.selectedShip.startLocation = (x-overX,y)
        elif overY > 0:
            self.selectedShip.startLocation = (x,y-overY)
        elif underX > 0:
            self.selectedShip.startLocation = (x+underX,y)
        elif underY > 0:
            self.selectedShip.startLocation = (x,y+underY)
            
    def __init__(self, width=600, height=600, fps=50, title="112 Battleship"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (255, 255, 255)
        pygame.init()

    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        self.init(screen)
        #playing = True
        drag = False
        offsetX = 0
        offsetY = 0
        start = tuple()
        while self.playing:
            time = clock.tick(self.fps)
            self.timerFired(time,screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.playing = False
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.inputBox.collidepoint(event.pos) and self.state == "player1":
                        self.textActive = not self.textActive
                    elif self.nameBox.collidepoint(event.pos) and self.state == "gameWon":
                        self.nameActive = not self.nameActive
                    else:
                        self.textActive = False
                        self.nameActive= False
                        i = 0
                        for ship in self.ships:
                            if ship.shipRect != None:
                                x,y = event.pos
                                x = x -(20+self.squareSize*ship.startLocation[1])
                                y = y - (20+self.squareSize*ship.startLocation[0])
                                start = ((20+ship.startLocation[1]*self.squareSize)\
                                ,(20+ship.startLocation[0]*self.squareSize))
                                if ship.shipRect.collidepoint((x,y)):
                                    self.selectedShip = ship
                                    x,y = event.pos
                                    offsetX = start[0] - x
                                    offsetY = start[1] - y
                                    drag = True
                                    break
                            i += 1
                    self.color = self.colorActive if self.textActive or self.nameActive else self.colorInactive
                    self.mousePressed(pygame.mouse.get_pos(), screen)
                elif event.type == pygame.MOUSEBUTTONUP:
                    drag = False
                    if len(self.board.highlightedSquares) != 0 and self.selectedShip != None:
                        self.selectedShip.moveShip(self.board.highlightedSquares[0])
                        if not self.checkShipOnBoard():
                            self.replaceShip()
                        elif not self.checkShipSpot():
                            self.selectedShip.backToStart()
                elif event.type == pygame.KEYDOWN:
                    if self.textActive:
                        if event.key == pygame.K_RETURN:
                            msg = "message " + self.textInput + " \n"
                            self.sendMsgQueue.put(msg)
                            self.textInput = ''
                            self.textActive = False
                            self.color = self.colorInactive
                            #self.textOuputTimer = time.time()
                        elif event.key == pygame.K_BACKSPACE:
                            self.textInput = self.textInput[:-1]
                        else:
                            if self.textFull is False:
                                self.textInput += event.unicode
                    elif self.nameActive:
                        if event.key == pygame.K_RETURN:
                            self.nameActive = False
                            self.color = self.colorInactive
                            self.nameSet = True
                            #self.textOuputTimer = time.time()
                        elif event.key == pygame.K_BACKSPACE:
                            self.nameInput = self.nameInput[:-1]
                        else:
                            if self.nameFull is False:
                                self.nameInput += event.unicode
                    else:
                        self.keyPressed(event.key, pygame.key.get_mods)
                elif event.type == pygame.MOUSEMOTION:
                    self.board.highlightedSquares = []
                    if drag:
                        x,y = event.pos
                        x = (x+offsetX)//self.squareSize
                        y = (y+offsetY)//self.squareSize
                        self.selectedShip.startLocation = (y,x)
                        self.boardOverlap()
                        self.redrawAll(screen)
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()
        return self.playAgain

def main():
    quit = False
    while not quit:
        game = Battleship()
        quit = not game.run()

if __name__ == '__main__':
    main()
    sys.exit()


