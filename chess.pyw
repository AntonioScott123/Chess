import pygame
import textwrap

pygame.init()
pygame.mixer.init()

scrnWidth = 1100
scrnHeight = 800


pygame.display.set_caption('Chess')
scrn = pygame.display.set_mode((scrnWidth, scrnHeight))
sqrDimension = scrnHeight // 8
timer = pygame.time.Clock()
whiteToMove = True
promoted = False
mover = "w"
move = 0
takes = ""
bum = 10
moveCounter = 0

fullNotation = []
fullNotationStr = ""

font = pygame.font.Font("assets/font/superKinds.ttf", 20)
notation = pygame.font.Font("assets/font/superKinds.ttf", 18)

board = 64

scrn.fill((31, 31, 31))


numtoabc = {
	"a": 0,
	"b": 1,
	"c": 2,
	"d": 3,
	"e": 4,
	"f": 5,
	"g": 6,
	"h": 7
}
abc_to_num = {v: k for k, v in numtoabc.items()}

pieces_images = {
	#White Pieces
	'wP': pygame.transform.scale(pygame.image.load("assets/pieces/wP.png"), (sqrDimension, sqrDimension)),
	'wR': pygame.transform.scale(pygame.image.load("assets/pieces/wR.png"), (sqrDimension, sqrDimension)),
	'wN': pygame.transform.scale(pygame.image.load("assets/pieces/wN.png"), (sqrDimension, sqrDimension)),
	'wB': pygame.transform.scale(pygame.image.load("assets/pieces/wB.png"), (sqrDimension, sqrDimension)),
	'wQ': pygame.transform.scale(pygame.image.load("assets/pieces/wQ.png"), (sqrDimension, sqrDimension)),
	'wK': pygame.transform.scale(pygame.image.load("assets/pieces/wK.png"), (sqrDimension, sqrDimension)),

	#Black Pieces
	'bP': pygame.transform.scale(pygame.image.load("assets/pieces/bP.png"), (sqrDimension, sqrDimension)),
	'bR': pygame.transform.scale(pygame.image.load("assets/pieces/bR.png"), (sqrDimension, sqrDimension)),
	'bN': pygame.transform.scale(pygame.image.load("assets/pieces/bN.png"), (sqrDimension, sqrDimension)),
	'bB': pygame.transform.scale(pygame.image.load("assets/pieces/bB.png"), (sqrDimension, sqrDimension)),
	'bQ': pygame.transform.scale(pygame.image.load("assets/pieces/bQ.png"), (sqrDimension, sqrDimension)),
	'bK': pygame.transform.scale(pygame.image.load("assets/pieces/bK.png"), (sqrDimension, sqrDimension)),
}

SFX = [

	pygame.mixer.Sound("assets/SFX/move-self.mp3"),
	pygame.mixer.Sound("assets/SFX/capture.mp3"),
	pygame.mixer.Sound("assets/SFX/promote.mp3"),


]


class Piece(pygame.sprite.Sprite):
	def __init__(self, pieceType, column, row):
		super().__init__()
		self.image = pieces_images[pieceType]
		self.original_image = self.image
		self.rect = self.image.get_rect(topleft =self.coordinate_to_pixel(column,row))
		self.picking_up = False
		self.scale_factor = 1
		self.pieceType = pieceType
		self.first_move = True

	def coordinate_to_pixel(self, column, row):
		x = column * sqrDimension
		y = scrnHeight - (row * sqrDimension) -100
		return x,y

	def update_position(self, x, y):
		if x < 0:
			x = 0
		elif x + sqrDimension > scrnWidth-200:
			x = scrnWidth - sqrDimension-200

		if y < 0:
			y = 0
		elif y + sqrDimension > scrnHeight +100:
			y = scrnHeight - sqrDimension +100

		self.rect.center = (x,y)

	def get_column_and_row(self):
		pieceRow = 8 - (self.rect.centery // sqrDimension) - 1
		pieceCol = self.rect.centerx // sqrDimension
		return pieceCol, pieceRow

	def ifLegalMove(self, prevX, prevY, curX, curY):
		global bum, promoted
		bum +=1
		selected_pieceColor = self.pieceType[0]
		selected_pieceType = self.pieceType[1]
		returned = False, False

		def customLogic(cond1, cond2):
			if not cond1 and not cond2:
				return True
			elif cond1 and not cond2:
				return False
			else:
				return True
		def customLogic1(cond1, cond2):
			if cond1 == True and cond2 == False:
				return False
			elif cond1 == True and cond2 == True:
				return True
			elif cond1 == False and cond2 == True:
				return True
			elif cond1 == False and cond2 == False:
				return False
		def customLogicForPawn(cond1, cond2):
			if cond1 == True and cond2 == False:
				return False
			elif cond1 == True and cond2 == True:
				return True
			elif cond1 == False and cond2 == True:
				return False
			elif cond1 == False and cond2 == False:
				return True


		def promoteCheck():
			global promoted
			if curY == promoteSquare:
				piece_dict[selected_pieceColor + "Q_" + str(bum)] = Piece(selected_pieceColor +'Q', curX, curY)
				all_pieces.add(piece_dict[selected_pieceColor + "Q_" + str(bum)])
				all_pieces.remove(self)
				SFX[2].play()
				promoted = True
			else:
				promoted = False

		def squareCheck(selected, canGoThroughPiece, canTake, pawnTakes=False):
			ranAlready = False
			legalMove = False
			checkX = curX
			checkY = curY
			checkXYList = []
			slopeOfPiece = (curX-prevX), (curY-prevY)
			if slopeOfPiece[0] < 0:
				slopeXDir = -1
			elif slopeOfPiece[0] > 0:
				slopeXDir = 1
			else:
				slopeXDir = 0
			if slopeOfPiece[1] < 0:
				slopeYDir = -1
			elif slopeOfPiece[1] > 0:
				slopeYDir = 1
			else:
				slopeYDir = 0

			if not ranAlready:
				while checkX != prevX and checkY != prevY:
					checkXYList.append(checkX)
					checkXYList.append(checkY)
					checkX -= slopeOfPiece[0]
					checkY -= slopeOfPiece[1]
					ranAlready = True
			if not ranAlready:
				while checkX == prevX and checkY != prevY:
					checkXYList.append(checkX)
					checkXYList.append(checkY)
					checkY -= 1 * slopeYDir
					ranAlready = True
			if not ranAlready:
				while checkX != prevX and checkY == prevY:
					checkXYList.append(checkX)
					checkXYList.append(checkY)
					checkX -= slopeXDir
					ranAlready = True
			k = 0
			GoingThroughPiece = False
			takes = False
			for k in range(len(checkXYList)):
				if k % 2 == 0:
					for piece in all_pieces:
						#checking if the square it is checking is the square the piece wants to be on and if it is it determines if it should take
						if checkXYList[k] == curX and checkXYList[k+1] == curY:
							if ((checkXYList[k] == piece.get_column_and_row()[0] and checkXYList[k+1] == piece.get_column_and_row()[1]) and selected != piece):
								takes = True
								PieceTaken = piece

						# checking if there is a piece on the way
						else:
							if (checkXYList[k] == piece.get_column_and_row()[0] and checkXYList[k+1] == piece.get_column_and_row()[1]):
								GoingThroughPiece = True
			

			if selected.pieceType[1] == "P":
				if pawnTakes:
					legalMove = customLogic(GoingThroughPiece, canGoThroughPiece) and (takes and canTake)
				else:
					legalMove = customLogic(GoingThroughPiece, canGoThroughPiece) and customLogicForPawn(takes, canTake)
			else:
				legalMove = customLogic(GoingThroughPiece, canGoThroughPiece) and customLogic(takes, canTake)

			if legalMove and takes:
				if selected.pieceType[0] == PieceTaken.pieceType[0]:
					legalMove = False
				else:
					all_pieces.remove(PieceTaken)
			
			return legalMove, takes

		if selected_pieceType == "P":
			if selected_pieceColor == "w":
				pWay = 1
				promoteSquare = 7
			else:
				pWay = -1
				promoteSquare = 0
			if self.first_move:
				if (prevY + pWay * 2  == curY or prevY + pWay  == curY) and prevX - curX == 0:
					returned = squareCheck(self, False, False)
				elif (prevX + 1 == curX or prevX - 1 == curX) and prevY + pWay == curY:
					returned = squareCheck(self, False, True, True)
				else:
					returned = False, False
			else:
				if prevY + pWay  == curY and prevX - curX == 0:
					returned = squareCheck(self, False, False)
				elif (prevX + 1 == curX or prevX - 1 == curX) and prevY + pWay == curY:
					returned = squareCheck(self, False, True, True)
				else:
					returned = False, False
			if returned[0]:
				promoteCheck()
		elif selected_pieceType == "R":
			if 0 <= curX <= 7 and curY == prevY:
				returned = squareCheck(self, False, True)
			elif 0 <= curY <= 7 and curX == prevX:
				returned = squareCheck(self, False, True)
			else:
				returned = False, False
		elif selected_pieceType == "B":
			if (curX-prevX) != 0 and (curY-prevY) != 0:
				if (curX-prevX) / (curY-prevY) == 1 or (curX-prevX) / (curY-prevY) == -1:
					returned = squareCheck(self, False, True)
			else:
				returned = False, False
		elif selected_pieceType == "Q":
			if (curX-prevX) != 0 and (curY-prevY) != 0:
				if (curX-prevX) / (curY-prevY) == 1 or (curX-prevX) / (curY-prevY) == -1:
					returned = squareCheck(self, False, True)
				else:
					returned = False, False
			elif 0 <= curX <= 7 and curY == prevY:
				returned = squareCheck(self, False, True)
			elif 0 <= curY <= 7 and curX == prevX:
				returned = squareCheck(self, False, True)
			else:
				returned = False, False
		elif selected_pieceType == "N":
			if abs(curX-prevX) == 2 and abs(curY-prevY) == 1:
				returned = squareCheck(self, True, True)
			if abs(curY-prevY) == 2 and abs(curX-prevX) == 1:
				returned = squareCheck(self, True, True)
		elif selected_pieceType == "K":
			if abs(curX-prevX) < 2 and abs(curY-prevY) < 2:
				returned = squareCheck(self, False, True)

		if selected_pieceType != "P":
			promoted = False

		return returned

def turnSwitch():
	global whiteToMove
	global mover
	global moveCounter
	if whiteToMove:
		whiteToMove = False
		mover = "b"
		moveCounter += 1
	else:
		whiteToMove = True
		mover = "w"

def drawWhiteBlack():
	if whiteToMove:
		pygame.draw.rect(scrn, (0, 0, 0), (820, 20, 35, 35))
		pygame.draw.rect(scrn, (255, 255, 255), (825, 25, 25, 25))
		scrn.blit(notation.render("White To Move", True, (255, 255, 255)), (860, 30))
	else:
		pygame.draw.rect(scrn, (255, 255, 255), (820, 20, 35, 35))
		pygame.draw.rect(scrn, (0, 0, 0), (825, 25, 25, 25))
		scrn.blit(notation.render("Black To Move", True, (255, 255, 255)), (860, 30))

def update_notation(piece, x, prevX, prevY):
	global fullNotation, fullNotationStr, whiteToMove, move, promoted
	pawnPrevCol = ""
	if promoted:
		promote = "=Q"
	else:
		promote = ""
	if piece.pieceType[1] == "P":
		if x != "":
			pawnPrevCol = abc_to_num[prevX]
		fullNotation.append(pawnPrevCol + x + list(numtoabc.keys())[column] + str(row + 1) + promote)
	else:
		fullNotation.append(piece.pieceType[1] + x + list(numtoabc.keys())[column] + str(row + 1) + promote)

def print_notation():
	global fullNotationStr, moveCounter, whitetoMove
	pygame.draw.rect(scrn, (31, 31, 31), (800, 0, 300, 800))
	for i in range(moveCounter):
		scrn.blit(notation.render(str(i + 1) + ".", True, (255, 255, 255)), (815, ((i + 1)) * 25 + 75))

	moveNum = 0
	for idx, move in enumerate(fullNotation):
		if idx % 2 == 0:
			moveNum += 1
			lenOfNumber = len(str(moveNum))
			scrn.blit(notation.render(move, True, (255, 255, 255)), (850, (idx // 2) * 25 + 100))
		else:
			scrn.blit(notation.render(move, True, (255, 255, 255)), (930, (idx // 2) * 25 + 100))


def draw_chessboard():
	for row in range(8):
		for col in range(8):
			if (row + col) % 2 == 1:
				color = (181, 136, 99) #dark square
				textColor = (240, 217, 181)
			else:
				color = (240, 217, 181) #white square
				textColor = (181, 136, 99)
			pygame.draw.rect(scrn, color, (col * sqrDimension, row * sqrDimension, sqrDimension, sqrDimension))
			if row + 1 == 8:
				scrn.blit(font.render(list(numtoabc.keys())[col], True, textColor), ((col * sqrDimension) + 80, (row * sqrDimension) + 80))
			if col == 0:
				scrn.blit(font.render(str(8 - (row)), True, textColor), ((col * sqrDimension) + 5, (row * sqrDimension) + 5))

def drawLastMove(prevX, prevY, curX, curY, take):
	global promoted
	color = (0, 160, 70)
	if take == True:
		color = (255,0,0)
	if promoted:
		color = (255,0,255)

	prevMoveSurface = pygame.Surface((sqrDimension, sqrDimension), pygame.SRCALPHA)
	curMoveSurface = pygame.Surface((sqrDimension, sqrDimension), pygame.SRCALPHA)


	prevMoveSurface.fill((0, 160, 70))
	curMoveSurface.fill(color)


	prevMoveSurface.set_alpha(100)  
	curMoveSurface.set_alpha(100)

	  
	scrn.blit(prevMoveSurface, (prevX * sqrDimension, 800 - (prevY * sqrDimension) -100))
	scrn.blit(curMoveSurface, (curX * sqrDimension, 800 - (curY * sqrDimension) -100))

def updateDrawing():
	global oldReturnY, returnY, oldReturnX, returnX, oldColumn, column, oldRow, row, oldTakes, oldTakes
	oldReturnY = returnY
	oldReturnX = returnX
	oldColumn = column
	oldRow = row
	oldTakes = takes



all_pieces = pygame.sprite.Group()

piece_dict = {}


def setup_pieces():
	for i in range(8):
		#Place White and Black Pawns
		piece_dict["wP_" + str(i)] = Piece('wP', i, 1)
		all_pieces.add(piece_dict["wP_" + str(i)])
		piece_dict["bP_" + str(i)] = Piece('bP', i, 6)
		all_pieces.add(piece_dict["bP_" + str(i)])
	for i in range(8):
		if i == 0 or i == 7:
			#Place White and Black Rooks
			piece_dict["wR_" + str(i)] = Piece('wR', i, 0)
			all_pieces.add(piece_dict["wR_" + str(i)])
			piece_dict["bR_" + str(i)] = Piece('bR', i, 7)
			all_pieces.add(piece_dict["bR_" + str(i)])
		if i == 1 or i == 6:
			#Place White and Black Knights
			piece_dict["wN_" + str(i)] = Piece('wN', i, 0)
			all_pieces.add(piece_dict["wN_" + str(i)])
			piece_dict["bN_" + str(i)] = Piece('bN', i, 7)
			all_pieces.add(piece_dict["bN_" + str(i)])
		if i == 2 or i == 5:
			#Place White and Black Bishops
			piece_dict["wB_" + str(i)] = Piece('wB', i, 0)
			all_pieces.add(piece_dict["wB_" + str(i)])
			piece_dict["bB_" + str(i)] = Piece('bB', i, 7)
			all_pieces.add(piece_dict["bB_" + str(i)])
		if i == 4:
			#Place White and Black Kings
			piece_dict["wK"] = Piece('wK', i, 0)
			all_pieces.add(piece_dict["wK"])
			piece_dict["bK"] = Piece('bK', i, 7)
			all_pieces.add(piece_dict["bK"])
		if i == 3:
			#Place White and Black Queens
			piece_dict["wQ_" + str(i)] = Piece('wQ', i, 0)
			all_pieces.add(piece_dict["wQ_" + str(i)])
			piece_dict["bQ_" + str(i)] = Piece('bQ', i, 7)
			all_pieces.add(piece_dict["bQ_" + str(i)])




selected_piece = None
offset_x = 0
offset_y = 0
returnX = 0
returnY = 0
column = 0
row = 0
legalMove = False

oldReturnY = -1
oldReturnX = -1
oldColumn = -1
oldRow = -1
oldTakes = False


setup_pieces()


run = True
while run:

	timer.tick(60)
	print_notation()
	drawWhiteBlack()
	draw_chessboard()
	drawLastMove(oldReturnX, oldReturnY, oldColumn, oldRow, oldTakes)
	for piece in all_pieces:
		if piece != selected_piece:
			scrn.blit(piece.image, piece.rect)

	if selected_piece:
		scrn.blit(selected_piece.image, selected_piece.rect)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				mouse_x, mouse_y = event.pos
				for piece in all_pieces:
					if piece.rect.collidepoint(mouse_x, mouse_y) and piece.pieceType[0] == mover:
						selected_piece = piece
						returnX = selected_piece.rect.x
						returnY = selected_piece.rect.y
						break
			

		if event.type == pygame.MOUSEMOTION:
			if selected_piece:
				mouse_x, mouse_y = event.pos
				selected_piece.update_position(mouse_x, mouse_y)

		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				if selected_piece:
					pieceCaptured = False
					mouse_x, mouse_y = event.pos
					returnX = returnX // sqrDimension
					returnY = 8 - (returnY // sqrDimension) - 1
					column = mouse_x // sqrDimension
					row = 8 - (mouse_y // sqrDimension) - 1
					#if mouse on chessboard then checks if it returns
					if scrnHeight > mouse_x > 0 and scrnWidth > mouse_y > 0:
						if returnX != column or returnY != row:
							both = selected_piece.ifLegalMove(returnX, returnY, column, row)
							legalMove = both[0]
							takes = both[1]
							if legalMove:
								selected_piece.first_move = False
								if takes:
									x = "x"
									if not promoted:
										SFX[1].play()
								else:
									x= ""
									if not promoted:
										SFX[0].play()
								update_notation(selected_piece, x, returnX, returnY)
								turnSwitch()
								updateDrawing()
								selected_piece.rect.topleft = selected_piece.coordinate_to_pixel(column, row)
							else:
								selected_piece.rect.topleft = selected_piece.coordinate_to_pixel(returnX, returnY)
						else:
							selected_piece.rect.topleft = selected_piece.coordinate_to_pixel(returnX, returnY)
					else:
						selected_piece.rect.topleft = selected_piece.coordinate_to_pixel(returnX, returnY)

				selected_piece = None
				

	pygame.display.update()


pygame.quit()
