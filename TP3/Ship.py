
# File that handles ship objects. Contains name, size, image, location, etc..
import pygame

class Ship(object):
    def __init__(self, shipName, startLocation, shipLength,image=None,squareSize=0):
        self.shipName = shipName
        self.startSpot = startLocation
        self.startLocation = startLocation
        self.horizontal = True
        self.squareSize = squareSize
        self.numHits = 0
        self.shipLength = shipLength
        self.shipImg = image
        if self.shipImg != None:
            self.shipImg = pygame.image.load(self.shipImg)
            self.shipImg = pygame.transform.scale(self.shipImg, (self.squareSize*self.shipLength,\
            self.squareSize))
            self.img = self.shipImg
            self.shipRect = self.shipImg.get_rect()
        self.sunk = False

    def backToStart(self):
        self.startLocation = self.startSpot
    
    def getLength(self):
        return self.shipLength
        
    def getLocation(self):
        return(self.startLocation)
    
    def getFullPosition(self):
        position = set() 
        if self.horizontal:
            for i in range(self.shipLength):
                if self.startLocation != None:
                    x,y = self.startLocation
                    position.add((x,y+i))
        else:
            for i in range(self.shipLength):
                if self.startLocation != None:
                    x,y = self.startLocation
                    position.add((x+i,y))
        return position
                
    
    def moveShip(self,start):
        x,y = start
        self.startLocation = (x,y)
        
    
    def getOrientation(self):
        return(self.horizontal)
    
    def changeOrientation(self):
        if self.horizontal:
            self.shipImg = pygame.transform.rotate(self.shipImg,90)
            self.shipRect = self.shipImg.get_rect()
            self.horizontal = not self.horizontal
        else:
            self.shipImg = pygame.transform.rotate(self.shipImg,270)
            self.shipRect = self.shipImg.get_rect()
            self.horizontal = not self.horizontal


    def sunkShip(self):
        if self.numHits == self.shipLength:
            self.sunk = True
        return self.sunk
    
    def shipHit(self):
        self.numHits += 1