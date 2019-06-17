import random
def evaluate(game, player):

	''' this function just adds up the pieces on board (100 = piece, 175 = king) and returns the difference '''
	def simple_score(game, player):
		white, black = 0, 0 # keep track of score
		for m in range(6):
			for n in range(6):
				if (game[m][n] != 0 and game[m][n].color == 'white'): # select white pieces on board
					if game[m][n].king == False: white += 100 # 100pt for normal pieces
					else: white += 175 # 175pts for kings
				elif (game[m][n] != 0 and game[m][n].color == 'black'): # select black pieces on board
					if game[m][n].king == False: black += 100 # 100pt for normal pieces
					else: black += 175 # 175pts for kings
		if player != 'white': return black-white
		else: return white-black

	''' this function will add bonus to pieces going to opposing side '''
	def piece_rank(game, player):
		white, black = 0, 0 # keep track of score
		for m in range(6):
			for n in range(6):
				if (game[m][n] != 0 and game[m][n].color == 'white'): # select white pieces on board
					if game[m][n].king != True: # not for kings
						white = white + (m*m)
				elif (game[m][n] != 0 and game[m][n].color == 'black'): # select black pieces on board
					if game[m][n].king != True: # not for kings
						black = black + ((5-m)*(5-m))
		if player != 'white': return black-white
		else: return white-black

	def edge_king(game, player):
		white, black = 0, 0 # keep track of score
		for m in range(6):
			if (game[m][0] != 0 and game[m][0].king != False):
				if game[m][0].color != 'black': white += +25
				else: black += +25
			if (game[m][5] != 0 and game[m][5].king != False):
				if game[m][5].color != 'black': white += +25
				else: black += +25
		if player != 'white': return black-white
		else: return white-black

	multi = random.uniform(0.97, 1.03) # will add +/- 3 percent to the score to make things more unpredictable

	return (simple_score(game, player) + piece_rank(game, player) + edge_king(game, player)) * 1
