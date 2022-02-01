# Checks the opponents move on player board and returns result
# Stores everything about the player's board

import pygame

class Player(object):
    def __init__(self,ships,board,squareSize,sunkShips):
        self.ships = ships
        self.board = board
        self.squareSize = squareSize
        self.sunkShips = sunkShips
        self.sunkShipNames = []
    
    def checkMove(self,x,y):
        if x > 9 or x < 0 or y > 9 or y < 0:
            return "invalid"
        result = self.checkHit((x,y))
        if result == 1:
            self.board[x][y] = "hit"
            return "hit"
        elif result == 0:
            self.board[x][y] = "miss"
            return "miss"
        elif result == -1:
            self.board[x][y] = "hit"
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
        
        
    

    