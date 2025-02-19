
import gym
import random
import requests
import numpy as np
import math
from gym_connect_four import ConnectFourEnv

env: ConnectFourEnv = gym.make("ConnectFour-v0")

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["ma6728bo-s"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                       })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res

"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""
def opponents_move(env):
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   action = random.choice(list(avmoves))

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

def valid_moves(state):
    avmoves = []
    for col in range(0, 7):
        if state[0][col] == 0:
            avmoves.append(col)
    return avmoves


def add_piece(state, col, player):
    tempState = state
    for i in range(0, 6):
        if tempState[i][col] != 0:
            tempState[i-1][col] = player
            break
        if i == 5:
            tempState[i][col] = player
            break
    return tempState

def can_win(state, player):
	# vert
	for col in range(7):
		for row in range(3):
			if state[row][col] == player and state[row+1][col] == player and state[row+2][col] == player and state[row+3][col] == player:
				return True

	# hor
	for col in range(4):
		for row in range(6):
			if state[row][col] == player and state[row][col+1] == player and state[row][col+2] == player and state[row][col+3] == player:
				return True

	# diagonal
	for col in range(4):
		for row in range(3, 6):
			if state[row][col] == player and state[row-1][col+1] == player and state[row-2][col+2] == player and state[row-3][col+3] == player:
				return True

	# diagonal
	for col in range(4):
		for row in range(3):
			if state[row][col] == player and state[row+1][col+1] == player and state[row+2][col+2] == player and state[row+3][col+3] == player:
				return True

def is_leaf(state, avmoves):
    if len(avmoves) == 0:
        return True
    if can_win(state, 1):
        return True
    if can_win(state, -1):
        return True

def calculate_range(range):
	value = 0

	if range.count(-1) == 3 and range.count(0) == 1:
		value -= 4

	if range.count(1) == 4:
		value += 99
	elif range.count(1) == 3 and range.count(0) == 1:
		value += 6
	elif range.count(1) == 2 and range.count(0) == 2:
		value += 2

	return value

def scoring(state, player):
    value = 0

    ## Points for having bricks in the middle
    center = []
    for r in range(6):
        center.append(state[r][3])
    center_amount = center.count(player)
    ## Gives 4 points per brick in middle
    value += center_amount * 4

	## Calculate score depending on amount of bricks in rows
    row = []
    for r in range(6):
        for c in range(0, 7):
            row.append(state[r][c])
        for c in range(0, 4):
            brick_range = row[c:c+4]
            value += calculate_range(brick_range)

	## Calculate vertical
    col = []
    for c in range(0, 7):
        for r in range(0, 6):
            col.append(state[r][c])
        for r in range(0, 3):
            brick_range = col[r:r+4]
            value += calculate_range(brick_range)

	## Calculate diagonal
    diag = []
    for r in range(0, 3):
        for c in range(0, 4):
            for i in range(0, 4):
                diag.append(state[r+i][c+i])
            brick_range = diag
            value += calculate_range(brick_range)

    ## Calculate diagonal
    diag2 = []
    for r in range(0, 3):
        for c in range(0, 4):
            for i in range(0, 4):
                diag2.append(state[r+3-i][c+i])
            brick_range = diag2
            value += calculate_range(brick_range)
    return value

def student_move(state, maxPlayer):
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """
   return minimax(state, 4, -math.inf, math.inf, maxPlayer)[0]


def minimax(state, depth, a, b, maxPlayer):
   avmoves = valid_moves(state)
   player = 1

   # If we have gone max distance down in tree return specific values depending on what kind of node it is
   if is_leaf(state, avmoves) or depth == 0:
       if is_leaf(state, avmoves):
           if can_win(state, -1):
               return (None, -99999999999)
           if can_win(state, 1):
               return (None, 99999999999)
           return (None, 0)
       else:
        return (None, scoring(state, player))
   if maxPlayer:
       # Start at negative infinity and work upwards
        value = -math.inf
        returnColumn = random.choice(avmoves)
        # Traverse every possible move recursively(for a certain depth)
        for col in avmoves:
            newState = state.copy()
            newState = add_piece(newState, col, 1)
            new_value = minimax(newState, depth-1, a, b, False)[1]
            if new_value > value:
                value = new_value
                returnColumn = col
            a = max(value, a)
            # If alpha is bigger than beta then we have a good move so we break and return the move
            if a >= b:
                break
        return returnColumn, value

   else:
       # Start at infinity and work downwards
        value = math.inf
        returnColumn = random.choice(avmoves)
        # Traverse every possible move recursively(for a certain depth)
        for col in avmoves:
            newState = state.copy()
            newState = add_piece(newState, col, -1)
            new_value = minimax(newState, depth-1, a, b, True)[1]
            if new_value < value:
                value = new_value
                returnColumn = col
            b = min(value, b)
            # If alpha is bigger than beta then we have a good move so we break and return the move
            if a >= b:
                break
        return returnColumn, value

def play_game(vs_server = False):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   maxPlayer = True

   # default state
   state = np.zeros((6, 7), dtype=int)

   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   print(state)
   print()

   done = False
   while not done:
      # Select your move
      stmove = student_move(state, maxPlayer) # TODO: change input here

      # make both student and bot/server moves
      if vs_server:
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tied to make an illegal move! Games ends.")
               break
            state, result, done, _ = env.step(stmove)

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            state, result, done = opponents_move(env)

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
         if result == 1:
            print("You won!")
         elif result == 0.5:
            print("It's a draw!")
         elif result == -1:
            print("You lost!")
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

      # Print current gamestate
      print(state)
      print()

def main():
   while True:
       a = input("Press ENTER to start a game:")
       play_game(vs_server = True)
   # TODO: Change vs_server to True when you are ready to play against the server
   # the results of your games there will be logged

if __name__ == "__main__":
    main()
