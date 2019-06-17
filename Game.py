
from copy import deepcopy
import math
import pygame
from pygame.locals import *
from sys import exit
import HeuristicFunctions
import mainwindow
#Global VARIABLES

turn = mainwindow.chooseturn() # keep track of whose turn it is
selected = (0, 1) # a tuple keeping track of which piece is selected
board = 0 # link to our 'main' board
move_limit = [150, 0] # move limit for each game (declares game as draw otherwise)
best_move = () # best move for the player as determined by alpha-beta algorithm
black, white = (), () # black and white players

# gui variables
window_size = (256, 256) # size of board in pixels
background_image_filename = 'board_brown1.png' # image for the background
title = 'Checkers' # window title
board_size = 6 # 6*6
left = 1 # left mouse button
fps = 5 # framerate of the scene (to save cpu time)
pause = 5 # number of seconds to pause the game for after end of game
start = True # are we at the beginnig of the game?


# class representing piece on the board
class Piece(object):
	def __init__(self, color, king):
		self.color = color
		self.king = king

# class representing player
class Player(object):
	def __init__(self, type, color, strategy, ply_depth):
		self.type = type # cpu or human
		self.color = color # black or white
		self.strategy = strategy
		self.ply_depth = ply_depth # ply depth for alpha-beta algorithm


# will initialize board with all the pieces
def init_board():
	global move_limit
	move_limit[1] = 0 # reset move limit
	palpha=0 # no of max prunes
	pbeta=0 #no of min prunes
	depth = 0 #depth of tree
	nodes=0 #depth of tree
	result = [
	[ 0, 1, 0, 1, 0, 1],
	[ 1, 0, 1, 0, 1, 0],
	[ 0, 0, 0, 0, 0, 0],
	[ 0, 0, 0, 0, 0, 0],
	[ 0,-1, 0,-1, 0,-1],
	[-1, 0,-1, 0,-1, 0]
	] # initial board setting
	for m in range(6):
		for n in range(6):
			if (result[m][n] == 1):
				piece = Piece('white', False) # basic black piece
				result[m][n] = piece
			elif (result[m][n] == -1):
				piece = Piece('black', False) # basic white piece
				result[m][n] = piece
	return result

# initialize players
def init_player(type, color, strategy, ply_depth):
	return Player(type, color, strategy, ply_depth)

# Functions

# will return array with available moves to the player on board
def avail_moves(board, player):
	moves = [] # will store available jumps and moves
# Jumps must be checked first since its the higher priority
	for m in range(6):
		for n in range(6):
			if board[m][n] != 0 and board[m][n].color == player:
				if can_jump([m, n], [m+1, n+1], [m+2, n+2], board) == True: moves.append([m, n, m+2, n+2])
				if can_jump([m, n], [m-1, n+1], [m-2, n+2], board) == True: moves.append([m, n, m-2, n+2])
				if can_jump([m, n], [m+1, n-1], [m+2, n-2], board) == True: moves.append([m, n, m+2, n-2])
				if can_jump([m, n], [m-1, n-1], [m-2, n-2], board) == True: moves.append([m, n, m-2, n-2])

	if len(moves) == 0: # if there are no jumps in the list (no jumps available)
		# ...check for regular moves
		for m in range(6):
			for n in range(6):
				if board[m][n] != 0 and board[m][n].color == player: # for all the players pieces...
					if can_move([m, n], [m+1, n+1], board) == True: moves.append([m, n, m+1, n+1])
					if can_move([m, n], [m-1, n+1], board) == True: moves.append([m, n, m-1, n+1])
					if can_move([m, n], [m+1, n-1], board) == True: moves.append([m, n, m+1, n-1])
					if can_move([m, n], [m-1, n-1], board) == True: moves.append([m, n, m-1, n-1])

	return moves # return the list with available jumps or moves

# will return true if the jump is legal
def can_jump(a, via, b, board):
	# is destination off board?
	if b[0] < 0 or b[0] > 5 or b[1] < 0 or b[1] > 5:
		return False
	# does destination contain a piece already?
	if board[b[0]][b[1]] != 0: return False
	# are we jumping something?
	if board[via[0]][via[1]] == 0: return False
	# for white piece
	if board[a[0]][a[1]].color == 'black':
		if b[0] > a[0]: return False # only move up
		if board[via[0]][via[1]].color != 'white': return False # only jump blacks
		return True # jump is possible
	# for black piece
	if board[a[0]][a[1]].color == 'white':
		if b[0] < a[0]: return False # only move down
		if board[via[0]][via[1]].color != 'black': return False # only jump whites
		return True # jump is possible

# will return true if the move is legal
def can_move(a, b, board):
	# is destination off board?
	if b[0] < 0 or b[0] > 5 or b[1] < 0 or b[1] > 5:
		return False
	# does destination contain a piece already?
	if board[b[0]][b[1]] != 0: return False
	# for white piece (not king)
	if board[a[0]][a[1]].color == 'black':
		if b[0] > a[0] or b[0] > 5: return False # only move up
		return True # move is possible
	# for black piece
	if board[a[0]][a[1]].color == 'white':
		if b[0] < a[0] or b[1]>5: return False # only move down
		return True # move is possible
	# for kings
	#if board[a[0]][a[1]].king == True: return True # move is possible

# make a move on a board, assuming it's legit
def make_move(a, b, board):
	board[b[0]][b[1]] = board[a[0]][a[1]] # make the move
	board[a[0]][a[1]] = 0 # delete the source

	# check if we made a king
	if b[0] == 0 and board[b[0]][b[1]].color == 'black': board[b[0]][b[1]].king = True
	if b[0] == 5 and board[b[0]][b[1]].color == 'white': board[b[0]][b[1]].king = True

	if (a[0] - b[0]) % 2 == 0: # we made a jump...
		board[int((a[0]+b[0])/2)][int((a[1]+b[1])/2)] = 0 # delete the jumped piece

def end_game(board):
	black, white = 0, 0 # keep track of score
	for m in range(6):
		for n in range(6):
			if board[m][n] != 0:
				if board[m][n].color == 'white': white += 1 # we see a black piece
				else: black += 1 # we see a white piece

	return black, white
def check_end(board):
	black, white = 0, 0 # keep track of score
	for m in range(6):
		for n in range(6):
			if board[m][n] != 0:
				if board[m][n].color == 'black': black += 1 # we see a black piece
				else: white += 1 # we see a white piece
	if (black > white):
		show_message("Black wins")

		show_winner("Black")
	elif(black < white):
		show_message("White wins")

		show_winner("White")
	elif (black == white):
		show_message("draw")
		show_winner("draw")
	else:
		pygame.display.flip()
def alpha_beta(player, board, ply, alpha, beta):
	global best_move,palpha,pbeta,depth
	depth = depth+ply
	print ("Max depth = "+str(ply))
	#print ("depth =" + str(depth))
	# find out ply depth for player
	ply_depth = 0
	if player != 'white': ply_depth = black.ply_depth
	else: ply_depth = white.ply_depth
	end = end_game(board)

	''' if(game over in current board position) '''
	if ply >= ply_depth or end[0] == 0 or end[1] == 0: # are we still playing?
		''' return winner '''
		score = HeuristicFunctions.evaluate(board, player) # return evaluation of board as we have reached final ply or end state
		return score

	''' children = all legal moves for player from this board '''
	moves = avail_moves(board, player) # get the available moves for player

	''' if(max's turn) '''
	if player == turn: # if we are to play on node...
		''' for each child '''
		for i in range(len(moves)):
			# create a deep copy of the board (otherwise pieces would be just references)
			new_board = deepcopy(board)
			make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), new_board) # make move on new board

			''' score = alpha-beta(other player,child,alpha,beta) '''
			# ...make a switch of players for minimax...
			if player == 'white': player = 'black'
			else: player = 'white'

			score = alpha_beta(player, new_board, ply+1, alpha, beta)

			''' if score > alpha then alpha = score (we have found a better best move) '''
			if score > alpha:

				palpha+=1
				if ply == 0: best_move = (moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]) # save the move
				alpha = score
			''' if alpha >= beta then return alpha (cut off) '''
			if alpha >= beta:
				#if ply == 0: best_move = (moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]) # save the move
				return alpha
		print (" Max pruning ="+str(palpha))
		print ("Min pruning ="+str(pbeta))
		print ("Nodes generated ="+str(depth))
		''' return alpha (this is our best move) '''
		return alpha
	else: # the opponent is to play on this node...
		''' else (min's turn) '''
		''' for each child '''
		for i in range(len(moves)):
			# create a deep copy of the board (otherwise pieces would be just references)
			new_board = deepcopy(board)
			make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), new_board) # make move on new board

			''' score = alpha-beta(other player,child,alpha,beta) '''
			# ...make a switch of players for minimax...
			if player == 'white': player = 'black'
			else: player = 'white'

			score = alpha_beta(player, new_board, ply+1, alpha, beta)

			''' if score < beta then beta = score (opponent has found a better worse move) '''
			if score < beta:

				pbeta=pbeta+1
				beta = score
			''' if alpha >= beta then return beta (cut off) '''
			if alpha >= beta: return beta
		print (" Min pruning ="+str(pbeta))
		print ("Max pruning ="+str(palpha))
		#print ("Nodes generated ="+str(nodes))
		''' return beta (this is the opponent's best move) '''
		return beta
def end_turn():
	global turn # use global variables

	if turn != 'black':	turn = 'black'
	else: turn = 'white'

# play as a computer
def cpu_play(player):
	global board, move_limit # global variables

	# find and print the best move for cpu
	if player.strategy == 'alpha-beta': alpha = alpha_beta(player.color, board, 0, -10000, +10000)
	#print player.color, alpha

	if alpha == -10000: # no more moves available... all is lost
		if player.color == black: show_winner("white")
		else: show_winner("black")

	make_move(best_move[0], best_move[1], board) # make the move on board

	move_limit[1] += 1 # add to move limit

	end_turn() # end turn

# initialize players and the board for the game
def game_init(difficulty):
	global white, black # work with global variables
	# hard difficulty
	if difficulty == 'hard':
		white = init_player('cpu', 'white', 'alpha-beta', 8) # init white player
		black = init_player('human', 'black', 'alpha-beta', 8) # init black player
		board = init_board()
	# moderate difficulty
	elif difficulty == 'moderate':
		white = init_player('cpu', 'white', 'alpha-beta', 4) # init white player
		black = init_player('human', 'black', 'alpha-beta', 4) # init black player
		board = init_board()
	# easy difficulty
	else:
		white = init_player('cpu', 'white', 'alpha-beta', 2) # init white player
		black = init_player('human', 'black', 'alpha-beta', 2) # init black player
		board = init_board()

	return board



# function that will draw a piece on the board
def draw_piece(row, column, color, king):
	# find the center pixel for the piece
	posX = ((window_size[0]/6)*column) - (window_size[0]/6)/2
	posY = ((window_size[1]/6)*row) - (window_size[1]/6)/2
	posX = int(posX)
	posY = int(posY)
	# set color for piece
	if color == 'white':
		border_color = (0, 0, 0)
		inner_color = (255, 255, 255)
	elif color == 'black':
		border_color = (255, 255, 255)
		inner_color = (0, 0, 0)

	pygame.draw.circle(screen, border_color, (posX, posY), 12) # draw piece border
	pygame.draw.circle(screen, inner_color, (posX, posY), 10) # draw piece

	# draw king 'status'
	if king == True:
		border_color = (255,48,48)
		inner_color = (255,48,48)
		pygame.draw.circle(screen, border_color, (posX, posY), 12) # draw piece border
		pygame.draw.circle(screen, inner_color, (posX, posY), 10) # draw piece

# show message for user on screen
def show_message(message):
	text = font.render(' '+message+' ', True, (255, 255, 255), (120, 195, 46)) # create message
	textRect = text.get_rect() # create a rectangle
	textRect.centerx = screen.get_rect().centerx # center the rectangle
	textRect.centery = screen.get_rect().centery
	screen.blit(text, textRect) # blit the text
def show_nodes(message):
	text = font.render('Possible moves ='+message+' ', True, (255, 255, 255), (120, 195, 46)) # create message
	textRect = text.get_rect() # create a rectangle
	screen.blit(text, textRect)

# will display the winner and do a countdown to a new game
def show_winner(winner):
	global board # we are resetting the global board
	global nodes
	if winner == 'draw':
		show_message("draw")
		pygame.time.wait(5000)# 1 sec = 1000
		print ("Draw1")
		#print ("Nodes generated ="+str(nodes))
		globalvaribales()
		board = init_board()
	else:
		print (winner+" wins")
		show_message(winner+" wins")
		pygame.time.wait(5000)
		print (winner+" wins")
		#print ("Nodes generated="+str(nodes))
		globalvaribales()
		board = init_board()
def globalvaribales():
	global palpha,pbeta,depth,nodes
	palpha=0 # no of max prunes
	pbeta=0 #no of min prunes
	depth = 0 #depth of tree
	nodes=0 #depth of tree
	print ("Max pruning = "+str(palpha))
	print ("Min pruning = "+str(pbeta))
	print ("Depth = "+str(depth))
	#print ("Nodes generated ="+str(nodes))
# function displaying position of clicked square
def mouse_click(pos):
	global selected, move_limit # use global variables

	# only go ahead if we can actually play :)
	if (turn != 'white' and black.type != 'cpu') or (turn != 'black' and white.type != 'cpu'):
		column = int(pos[0]/(window_size[0]/board_size))
		row = int(pos[1]/(window_size[1]/board_size))

		if board[row][column] != 0 and board[row][column].color == turn:
			selected = row, column # 'select' a piece
		else:
			moves = avail_moves(board, turn) # get available moves for that player
			if len(moves)== 0: end_turn()
			for i in range(len(moves)):
				if selected[0] == moves[i][0] and selected[1] == moves[i][1]:
					if row == moves[i][2] and column == moves[i][3]:
						make_move(selected, (row, column), board) # make the move
						move_limit[1] += 1 # add to move limit
						end_turn() # end turn

######################## START OF GAME ########################

pygame.init() # initialize pygame

board = game_init('easy') # initialize players and board for the game
palpha=0 # no of max prunes
pbeta=0 #no of min prunes
depth = 0 #depth of tree
nodes=0 #depth of tree
print ("Max pruning = "+str(palpha))
print ("Min pruning = "+str(pbeta))
print ("Depth = "+str(depth))
#print ("Nodes generated ="+str(nodes))
screen = pygame.display.set_mode(window_size) # set window size
pygame.display.set_caption(title) # set title of the window
clock = pygame.time.Clock() # create clock so that game doesn't refresh that often

background = pygame.image.load(background_image_filename).convert() # load background
font = pygame.font.Font('freesansbold.ttf', 11) # font for the messages
font_big = pygame.font.Font('freesansbold.ttf', 13) # font for the countdown

while True: # main game loop
	for event in pygame.event.get(): # the event loop
		if event.type == QUIT:
			exit() # quit game
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == left:
			mouse_click(event.pos) # mouse click
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_F1: # when pressing 'F1'...
				print ("reset difficulty to easy")
				globalvaribales()
				board = game_init('easy')
			if event.key == pygame.K_F2: # when pressing 'F2'...
				print ("reset difficulty to medium")
				globalvaribales()
				board = game_init('moderate')
			if event.key == pygame.K_F3: # when pressing 'F3'...
				print ("reset difficulty to hard")
				globalvaribales()
				board = game_init('hard')


	screen.blit(background, (0, 0)) # keep the background at the same spot


	if (turn != 'white' and black.type == 'human') or (turn != 'black' and white.type == 'human'):
		show_message('YOUR TURN, to change difficulty press F1,F2,F3')

	else: show_message('CPU THINKING,to change difficulty press F1,F2,F3')

	# draw pieces on board
	for m in range(6):
		for n in range(6):
			if board[m][n] != 0:
				draw_piece(m+1, n+1, board[m][n].color, board[m][n].king)

	# show intro
	if start == True:
		show_message('Welcome to '+title)

		start = False
	moves = avail_moves(board,turn)
	nodes=nodes+len(moves)
	show_nodes(str(len(moves)))
	#if len(moves)==0:
	#	check_end(board)
	# check state of game
	end = end_game(board)
	if end[1] == 0:	show_winner("black")
	elif end[0] == 0: show_winner("white")
	# check if we breached the threshold for number of moves
	elif move_limit[0] == move_limit[1]: show_winner("draw")

	else: pygame.display.flip() # display scene from buffer

	# cpu play
	if turn != 'white' and black.type == 'cpu': cpu_play(black) # white cpu turn
	elif turn != 'black' and white.type == 'cpu': cpu_play(white) # black cpu turn

	clock.tick(fps) # saves cpu time
