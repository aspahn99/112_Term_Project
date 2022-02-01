# Draws player board and opponent board, draws pegs for both boards and
# draws ships for player board.

import pygame

class Board(object):
    def __init__(self, playerBoard, opponentBoard, width, height, ships, highlightedSquares):
        self.width = width
        self.height = height
        self.playerBoard = playerBoard
        self.opponentBoard = opponentBoard
        self.highlightedSquares = highlightedSquares
        self.ships = ships
        self.squareSize = (self.width//2-40)//10
        self.circleRadius = self.squareSize//4

        
        
    def drawPlayer(self, screen):
        for row in range(len(self.playerBoard)):
            for col in range(len(self.playerBoard[0])):
                if (row,col) in self.highlightedSquares:
                    pygame.draw.rect(screen, (255,255,0), (20+col*self.squareSize,20+row*self.squareSize\
                    ,self.squareSize,self.squareSize),)
                else:
                    pygame.draw.rect(screen, (0,0,0), (20+col*self.squareSize,20+row*self.squareSize\
                    ,self.squareSize,self.squareSize),2)

        self.drawShips(screen)
        self.drawPegs(screen, "player")
    
    def drawOpponent(self, screen):
        offset = self.width//2 + 12
        for row in range(len(self.opponentBoard)):
            for col in range(len(self.opponentBoard[0])):
                pygame.draw.rect(screen, (0,0,0), (offset+col*self.squareSize,20+row*self.squareSize\
                ,self.squareSize,self.squareSize),2)
        self.drawPegs(screen, "opponent")
    
        
    def drawPegs(self, screen, person):
        if person == "player":
            board = self.playerBoard
            offset = 20
        else:
            board = self.opponentBoard
            offset = self.width//2 + 12
        for row in range(len(board)):
            for col in range(len(board[0])):
                circleX = ((offset+(col+1)*self.squareSize)+(offset+col*self.squareSize))//2
                circleY = ((20+(row+1)*self.squareSize)+(20+row*self.squareSize))//2
                if board[row][col] == "hit":
                    pygame.draw.circle(screen, (250,0,0),(circleX,circleY),self.circleRadius)
                elif board[row][col] == "miss":
                    pygame.draw.circle(screen, (255,255,255),(circleX,circleY),self.circleRadius)
    
        
    def drawShips(self, screen):
        i = 0
        for ship in self.ships:
            i += 1
            start = ship.getLocation()
            horizontal = ship.getOrientation()
            length = ship.getLength()
            image = ship.shipImg
            startRow,startCol = start
            if not horizontal:
                screen.blit(image,(20+startCol*self.squareSize,\
                20+startRow*self.squareSize))
            else:
                screen.blit(image,(20+startCol*self.squareSize,\
                20+startRow*self.squareSize))
                
                
        