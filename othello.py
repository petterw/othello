# Implementation of the board game Othello/Reversi. 
# Suggested uses: Backend for game programming, AI research.
#
# Try running this script to play a game against a random-playing
# opponent.
#
# Copyright (C) 2010-2011 Petter Westby <petter@pwestby.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, random

class Board:
	def __init__(self, size = 8):
		# create board
		self.board = [[0]*size for x in xrange(size)]
		self.size = size
		self.counts = {0:size**2,1:0,-1:0}
		
		# setup successor state memoization
		self.memoized_successors = {1:False,-1:False}
		
		# populate starting positions
		self.set_value(size/2, size/2, -1)
		self.set_value(size/2-1, size/2-1, -1)
		self.set_value(size/2, size/2-1, 1)
		self.set_value(size/2-1, size/2, 1)
	
	def to_list(self):
		""" return the board state as a list, useful for evaluating it 
			externally
		"""
		return [item for sublist in self.board for item in sublist]
		
	def show(self):
		""" print board to stdout
		"""
		#hnumbers
		sys.stdout.write("\n   ")
		for y in xrange(self.size):
			sys.stdout.write(str(y+1) + "   ")
		print ""
		for x in xrange(self.size):
			#vnumbers
			sys.stdout.write(str(x+1) + " ")
			for y in xrange(self.size):
				if(self.board[x][y]==0):
					sys.stdout.write('   ,')
				elif(self.board[x][y]==1):
					sys.stdout.write(' + ,')
				elif(self.board[x][y]==-1):
					sys.stdout.write(' O ,')
			print "\n"
		print "\n"
	
	def count(self,value):
		""" return number of pieces there are with the given value
		"""
		return self.counts[value]
	
	def done(self):
		""" can any more moves be made given the current board state?
		"""
		return self.counts[0] == 0 or (len(self.successors(1)) == 0 and len(self.successors(-1)) == 0)
	
	def __eq__(self,other):
		""" is this board state the same as other?
		"""
		if self.size != other.size or self.size != other.size:
			return False
		for x in xrange(self.size):
			for y in xrange(self.size):
				if self.board[x][y] != other.board[x][y]:
					return False
		return True
	
	def set_value(self,x,y,value):
		""" set the value in coordinate x,y
		"""
		# check if we are breaking the rules/have a bug
		assert not (value == 0 and self.board[x][y] != 0)
		
		# clear successor state memoization
		self.memoized_successors = {1:False,-1:False}
		
		#update counts and set value
		self.counts[self.board[x][y]] -= 1
		self.board[x][y] = value
		self.counts[value] += 1
	
	def put(self, x, y, value):
		""" put method for the console player. prevents illegal moves
		"""
		flips = self.flips(x,y,value)
		if(self.legal(x,y,value,flips)):
			self.set_value(x,y,value)
			for f in flips:
				self.set_value(f[0],f[1],value)
	
	def legal(self,x,y,value,flips):
		""" is it legal to place the value in x,y? Flips are passed in
			to avoid repeated computation
		"""
		return len(flips) > 0 and x > -1 and x < self.size and y > -1 and y < self.size and self.board[x][y]==0
	
	def flips(self,x,y,value):
		""" Returns the flip operations that follow as a consequence of
			placing a piece in x,y
		"""
		ret = []
		for xdelta in xrange(-1,2):
			for ydelta in xrange(-1,2):
				# not in the center
				if xdelta != 0 or ydelta != 0:
					# try move
					ret.extend(self.beam(x,y,value,xdelta,ydelta))
		return ret
	
	def beam(self,x,y,value,xdelta,ydelta):
		""" attempt a chain of flips from x,y in the direction indicated
			by xdelta,ydelta, returns an empty list (no flips) if none 
			can be made legally
		"""
		newx = x + xdelta
		newy = y + ydelta
		coords = []
		#find the intermediate opposite colored pieces, or stop
		while newx > -1 and newx < self.size and newy > -1 and newy < self.size and self.board[newx][newy] == -1*value:
			coords.append((newx,newy))
			newx = newx + xdelta
			newy = newy + ydelta
		#if we find our piece at the other end, flip the intermediates
		if newx > -1 and newx < self.size and newy > -1 and newy < self.size and self.board[newx][newy] == value:
			return coords
		return []
	
	def successors(self, value):
		""" generate possible successor states given values turn 
		"""
		if self.memoized_successors[value] != False:
			return self.memoized_successors[value]
		s = []
		for x in xrange(self.size):
			for y in xrange(self.size):
				flips = self.flips(x, y, value)
				if self.legal(x, y, value, flips):
					successor = self.clone()
					successor.set_value(x,y,value)
					for f in flips:
						successor.set_value(f[0],f[1],value)
					s.append(successor)
		self.memoized_successors[value] = s
		return s
	
	def clone(self):
		""" clone the current board state
		"""
		c = Board(self.size)
		for x in xrange(self.size):
			for y in xrange(self.size):
				c.set_value(x,y,self.board[x][y])
		return c

class RandomPlayer:
	""" A player which chooses the next board state randomly
	"""
	def __init__(self):
		pass
	def rate(self, successors, board, my_value):
		return [random.random() for a in successors]

class ConsolePlayer:
	""" An interactive player, which prompts for the next move on the 
		command line
	"""
	def __init__(self):
		pass
	def rate(self,successors,board,my_value):
		choice_made = False
		ret = []
		while not choice_made:
			print "-------------------------------------"
			print "Opponents move was: "
			board.show()
			choice = [-1,-1]
			try:
				print "Enter coordinates separated by a comma."
				choice = [int(v)-1 for v in raw_input("Put: ").split(",")]
			except ValueError:
				print "Invalid input"
			temp = board.clone()
			try:
				temp.put(choice[0], choice[1], my_value)
			except IndexError:
				print "Enter coordinates separated by a comma"
			ret = []
			for x in xrange(len(successors)):
				if temp == successors[x]:
					print "-------------------------------------"
					print "Your move was: "
					successors[x].show()
					ret.append(1.0)
					choice_made = True
				else:
					ret.append(0.0)
			if not choice_made:
				print "Try again"
		return ret

class AIPlayer:
	""" An AI player placeholder, for plugging in a custom state rating 
		function
	"""
	def __init__(self,rate):
		self.rate = rate

def game(A, B, board_size = 8):
	""" A generator yielding the states of a game between A and B
	"""
	players = {1:A,-1:B}
	board = Board(board_size)
	player = 1
	while not board.done():
		successors = board.successors(player)
		if not len(successors) == 0:
			ratings = players[player].rate(successors,board, player)
			successor = 0
			for x in xrange(1,len(successors)):
				if ratings[x] > ratings[successor]:
					successor = x
			board = successors[successor]
			yield (board, False)
		player *= -1
	yield (board,True)

def result(A, B, board_size = 8):
	""" Convenience method for retrieving the final board state of a
		game between A and B
	"""
	return filter(lambda x: x[1], list(game(A, B, board_size)))[0][0]

# play a game against the random player
if __name__ == "__main__":
	A = RandomPlayer()
	B = ConsolePlayer()
	result(A,B)
