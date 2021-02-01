# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=bad-whitespace
# pylint: disable=trailing-whitespace
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=singleton-comparison
from tkinter import *
from itertools import cycle
import copy

WHITE = 'white'
BLACK = 'black'

def kingList(x,y):
    return [(x+1,y),(x+1,y+1),(x+1,y-1),(x,y+1),(x,y-1),(x-1,y),(x-1,y+1),(x-1,y-1)]

def knightList(x,y):
    return [(x+2,y+1),(x-2,y+1),(x+2,y-1),(x-2,y-1),(x+1,y+2),(x-1,y+2),(x+1,y-2),(x-1,y-2)]

def isInBounds(x,y):
        if x >= 0 and x < 8 and y >= 0 and y < 8:
            return True
        return False

def _from_rgb(rgb):
    return "#%02x%02x%02x" % rgb

class Chessboard(Tk):

    chessboard = []

    def __init__(self):
        super(Chessboard, self).__init__()
        self.title("Chess game")
        self.minsize(800, 600)
        self.canvas = Canvas(self, bg="gray", height=600, width=800)
        self.selected = False
        self.create_chessboard()
        self.colorCycle = cycle([WHITE,BLACK])
        self.playersTurn = next(self.colorCycle)
        self.kings_in_check = [[False, None], [False, None]]
        self.stillcheck = False
        #self.reverse = [None, None]
        self.positions = []
    
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.selectPiece)

    def create_chessboard(self):
        piecespritelist = ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"]
        piecelist = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        color = cycle([_from_rgb((227,193,111)), _from_rgb((184,139,74))])
        coords = [0,0,75,75]
        for i in range(0, 8): 
            self.chessboard.append([])       
            for j in range(0, 8):
                if (i == 0):
                    self.chessboard[i].append(Square(self.canvas, coords, next(color), Piece(piecelist[j], BLACK,piecespritelist[j]),i,j,1))
                elif (i == 1):
                    self.chessboard[i].append(Square(self.canvas, coords, next(color), Piece(Pawn(), BLACK,"♙"),i,j,1))
                elif (i == 6):
                    self.chessboard[i].append(Square(self.canvas, coords, next(color), Piece(Pawn(), WHITE,"♙"),i,j,1))
                elif (i == 7):
                    self.chessboard[i].append(Square(self.canvas, coords, next(color), Piece(piecelist[j], WHITE,piecespritelist[j]),i,j,1))
                else:
                    self.chessboard[i].append(Square(self.canvas, coords, next(color), None,i,j,1))

                coords[0] += 75
                coords[2] += 75
            next(color)
            coords[0] = 0
            coords[2] = 75 
            coords[1] += 75
            coords[3] += 75

    @staticmethod
    def noConflict(x,y,color):
        if (isInBounds(x,y) and Chessboard.chessboard[x][y].piece == None ): 
            return True
        elif (isInBounds(x,y) and Chessboard.chessboard[x][y].piece != None and Chessboard.chessboard[x][y].piece.color != color):
            return True
        return False

    @staticmethod
    def calculateMoves(x,y, color, interval):
        answers = []
        for xint,yint in interval:
            xtemp = x + xint
            ytemp = y + yint

            while isInBounds(xtemp,ytemp):
                if (Chessboard.chessboard[xtemp][ytemp].piece == None):
                    answers.append((xtemp,ytemp))
                    xtemp += xint
                    ytemp += yint
                elif (Chessboard.chessboard[xtemp][ytemp].piece != color):
                    answers.append((xtemp,ytemp))
                    break
                else:
                    break

        return answers

    def selectPiece(self, event):
        x = event.x
        y = event.y
        brejk = False
        for row in self.chessboard:
            if(brejk == True):
                break
            for square in row:
                if(self.findSquare(square.coords, x, y)):
                    # Vyberie sa stvorec
                    if (self.selected == False):
                        if(square.piece != None and square.piece.color == self.playersTurn):
                            self.selected = True
                            self.selectedSquare = square
                            self.selectedSquare.drawSelectedSquare('cyan')
                            if(self.selectedSquare.piece != None):
                                self.selectedSquare.drawPiece()
                            brejk = True
                            break
                    # Je vybraty stvorec
                    else:
                        # Stvorec je totozny s predchadzajucim
                        if(self.selectedSquare == square):
                            self.deselect()
                            brejk = True
                            break
                        
                        #Figurka ma povoleny dany tah
                        if(self.kings_in_check[0][0] == True or self.kings_in_check[1][0] == True):
                            self.stillcheck = True

                        if(self.selectedSquare.piece.name in [Pawn,King]):
                            canMove = square.position in self.selectedSquare.piece.name.availableMoves(self.selectedSquare.piece.name, self.selectedSquare.position, self.selectedSquare.piece.color)
                            self.selectedSquare.piece.name.hasmoved(self.selectedSquare.piece.name)
                        else:
                            canMove = square.position in self.selectedSquare.piece.name.availableMoves(self.selectedSquare.position, self.selectedSquare.piece.color)
                        if(canMove):
                            if(square.piece == None):
                                self.reversed = [self.selectedSquare, square]
                                self.selectedSquare.drawSquare()
                                square.piece = self.selectedSquare.piece
                                square.drawPiece()
                                self.selectedSquare.piece = None
                                #self.deselect()
                            else:
                                self.isTakable(square)
                            



                            self.playersTurn = next(self.colorCycle)
                            self.kings_in_check = self.isKingInCheck()
                            
                            if(self.kings_in_check[0][0] == True):
                                self.markRed(self.kings_in_check[0][1])
                            elif(self.kings_in_check[1][0] == True):
                                self.markRed(self.kings_in_check[1][1])
                            else:
                                self.stillcheck = False
                                self.deselect()

                            if(self.stillcheck == True):
                                self.playersTurn = next(self.colorCycle)
                                self.chessboard = self.positions[-1]
                                for row in self.chessboard:
                                    for sq in row:
                                        sq.drawSquare()
                                        if(sq.piece != None):
                                            sq.drawPiece()
                                
                            else:
                                self.copyPosition()

                        else:
                            self.deselect()
                        
                        brejk = True
                        break
    
    def copyPosition(self):
        newboard = []
        for i in range(0, 8): 
            newboard.append([])       
            for j in range(0, 8):
                sq = self.chessboard[i][j] 
                newboard[i].append(Square(sq.canvas, sq.coords, sq. color, sq.piece, sq.position[0], sq.position[1],0))

        self.positions.append(newboard)

    def markRed(self, square):
        self.selectedSquare = square
        self.selectedSquare.drawSelectedSquare("red")
        self.selectedSquare.drawPiece()
        self.selected = False
        self.selectedSquare = None

    def isCheckMate(self, kingsInCheck):
        #White is in check
        Checkmate = True
        if(kingsInCheck[0][0] == True):
            for row in self.chessboard:
                for square in row:
                    if (square.piece != None and square.piece.color == WHITE):
                        #Can take the piece
                        if(square.piece.name != King):
                            if (square.piece.name == Pawn):
                                if(kingsInCheck[2] in square.piece.name.availableMoves(square.piece.name,square.position, WHITE)):
                                    Checkmate = False
                            elif(kingsInCheck[2] in square.piece.name.availableMoves(square.position, WHITE)):
                                Checkmate = False

        if(kingsInCheck[1][0] == True):
            for row in self.chessboard:
                for square in row:
                    if (square.piece != None and square.piece.color == BLACK):
                        #Can take the piece
                        if(square.piece.name != King):
                            if (square.piece.name == Pawn):
                                if(kingsInCheck[2] in square.piece.name.availableMoves(square.piece.name,square.position, BLACK)):
                                    Checkmate = False
                            elif(kingsInCheck[2] in square.piece.name.availableMoves(square.position, BLACK)):
                                Checkmate = False
        
        if(Checkmate == True):
            print("Checkmate")
                        

    
    #def undo(self):
    #    self.reversed[0].piece =  self.reversed[1].piece
    #    self.reversed[1].piece = None
    #    self.reversed[1].drawSquare()
    #    self.reversed[0].drawPiece()
    #    self.playersTurn = next(self.colorCycle)

    def deselect(self):
        self.selected = False
        self.selectedSquare.drawSquare()
        self.selectedSquare.drawPiece()
        self.selectedSquare = None

    def isKingInCheck(self):
        blackking_in_check = False
        whiteking_in_check = False

        for row in self.chessboard:
            for square in row:
                if(square.piece != None):
                    if (square.piece.name == King):
                        if (square.piece.color == WHITE):
                            whiteking_square = square
                        else:
                            blackking_square = square

        for row in self.chessboard:
            for square in row:
                if (square.piece != None and square.piece.color == WHITE):
                    if(square.piece.name != King):
                        if (square.piece.name == Pawn):
                            if(blackking_square.position in square.piece.name.availableMoves(square.piece.name,square.position, WHITE)):
                                piece_giving_check_position = square.position
                                blackking_in_check = True
                        elif(blackking_square.position in square.piece.name.availableMoves(square.position, WHITE)):
                            piece_giving_check_position = square.position
                            blackking_in_check = True

                if (square.piece != None and square.piece.color == BLACK):
                    if(square.piece.name != King):
                        if (square.piece.name == Pawn):
                            if(whiteking_square.position in square.piece.name.availableMoves(square.piece.name,square.position, BLACK)):
                                piece_giving_check_position = square.position
                                whiteking_in_check = True
                        elif(whiteking_square.position in square.piece.name.availableMoves(square.position, BLACK)):
                            piece_giving_check_position = square.position
                            whiteking_in_check = True
                        
        if(whiteking_in_check == True or blackking_in_check == True):
            self.isCheckMate([[whiteking_in_check, whiteking_square], [blackking_in_check, blackking_square], piece_giving_check_position])

        return [[whiteking_in_check, whiteking_square], [blackking_in_check, blackking_square]]

        
    def isTakable(self, square):
        if(self.selectedSquare.piece.color != square.piece.color):
            #self.reversedself.reversed = [self.selectedSquare, square]
            self.selectedSquare.drawSquare()
            square.piece = self.selectedSquare.piece
            square.drawSquare()
            square.drawPiece()
            self.selectedSquare.piece = None
            #self.deselect()
        else:
            pass
            #self.deselect()

    def findSquare(self, coords, x, y) : 
        if (x > coords[0] and x < coords[2] and y > coords[1] and y < coords[3]): 
            return True
        else : 
            return False  
        

class Square:

    def __init__(self, canvas, coords, color, piece, x,y, draw):
        self.canvas = canvas
        self.coords = [i for i in coords]
        self.color = color
        self.position = (x,y)
        self.center = [(self.coords[2] + self.coords[0])/2, (self.coords[1] + self.coords[3])/2]
        self.piece = piece
        if(draw == 1):
            self.drawSquare()
            self.drawPiece()
        
        
    def drawPiece(self):
        if (self.piece == None):
            piececolor = None
            piecetext = None
        else:
            piececolor = self.piece.color
            piecetext = self.piece.sprite
        
        self.canvas.create_text(self.center[0], self.center[1], fill=piececolor,font="Times 30 bold" ,text=piecetext)

    def drawSquare(self):
        self.canvas.create_rectangle(self.coords[0],self.coords[1],self.coords[2],self.coords[3], fill = self.color)

   
    def drawSelectedSquare(self,color):
        self.canvas.create_rectangle(self.coords[0],self.coords[1],self.coords[2],self.coords[3], fill = color)


chessCardinals = [(1,0),(0,1),(-1,0),(0,-1)]
chessDiagonals = [(1,1),(-1,1),(1,-1),(-1,-1)]


class Piece: 
    def __init__(self, name, color, sprite):
        self.name = name
        self.color = color
        self.sprite = sprite

class King(Piece):

    def __init__(self):
        self.moved = False

    def availableMoves(self, position, color):
        return [(xx,yy) for xx,yy in kingList(position[0],position[1]) if Chessboard.noConflict(xx, yy, color)]

    def hasmoved(self):
        self.moved = True

class Knight(Piece):
    @staticmethod
    def availableMoves(position, color):
        return [(xx,yy) for xx,yy in knightList(position[0],position[1]) if Chessboard.noConflict(xx, yy, color)]

class Queen(Piece):
    @staticmethod
    def availableMoves(position, color):
        return Chessboard.calculateMoves(position[0],position[1], color, chessCardinals+chessDiagonals)

class Bishop(Piece):
    @staticmethod
    def availableMoves(position, color):
        return Chessboard.calculateMoves(position[0],position[1], color, chessDiagonals)

class Rook(Piece):
    @staticmethod
    def availableMoves(position, color):
        return Chessboard.calculateMoves(position[0],position[1], color, chessCardinals)

class Pawn(Piece):

    def __init__(self):
        self.moved = False

    def availableMoves(self,position, color):
        
        if(color == WHITE):
            direction = -1
        else:
            direction = 1
        x = position[0]
        y = position[1]
        answers = []
        if self.moved == False:
            if (Chessboard.chessboard[x+direction*2][y].piece == None): answers.append((x+direction*2,y)) 
        if (Chessboard.chessboard[x+direction][y].piece == None): answers.append((x+direction,y))
        try:
            if (isInBounds(x+direction,y+1)):
                if Chessboard.chessboard[x+direction][y+1].piece != None and Chessboard.chessboard[x+direction][y+1].piece.color != color: 
                    answers.append((x+direction,y+1))
            if (isInBounds(x+direction,y-1)):
                if Chessboard.chessboard[x+direction][y-1].piece != None and Chessboard.chessboard[x+direction][y-1].piece.color != color: 
                    answers.append((x+direction,y-1))
        except:
            print("oopsie")
        return answers
    
    def hasmoved(self):
        self.moved = True






#uniDict = {WHITE : {Pawn : "♙", Rook : "♖", Knight : "♘", Bishop : "♗", King : "♔", Queen : "♕" }, BLACK : {Pawn : "♟", Rook : "♜", Knight : "♞", Bishop : "♝", King : "♚", Queen : "♛" }}

if __name__ == '__main__':
    root = Chessboard()
    root.mainloop()
