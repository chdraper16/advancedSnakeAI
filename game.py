import numpy as np
import random as rand
import matplotlib.pyplot as plt
'''
dim = size of play field for the snake, must be greater than 2
view = size of view that shows the snake what is past the loop, size between 1 and dim
printing = how the field should be printed
	0: Just show the field
	1: Show the view as well
	not above: show nothing
player = What type of player is playing the game
	0: Human player using wasd
	1: NN using 1234
field_generator = What type of field should be made to play on
	-1: Random
	0: Default empty
	1: Walls all around
	2: Cross
	4: Random small Blocks
	8: Random small Holes
	OR together values wanted
		ex:  19: 3: 2|1 A walled off box with a Cross in the middle
Field values:
0: empty square
1: wall
2: snake
3: fruit
4: Snake head



'''



class Field:
	def __init__(self,dim=15,view=3,printing=0,player=0, field_gen=0,cut = -1):
		rand.seed()
		if dim < 2:
			print("Invalid field size! Default to 15")
			self.dim= 15
		else:
			self.dim=dim
		if view > self.dim:
			print("Invalid view size! Default to",self.dim)
			self.view = self.dim
		else:
			if view <= 0:
				self.view=1
				print("Invalid dim size! Default to 1")
			else:
				self.view=view
		self.body=np.zeros((self.dim+self.view*2,self.dim+self.view*2))
		self.print_type = printing #0 normal, 1 debug w/ view
		self.player_type = player #0 WASD, 1 1234
		self.gen_type = field_gen
		self.score = 0
		self.end = False
		self.steps = 0
		self.cut_off = cut
		self.fruit =[0,0]
		self.make_field()
		self.scores = []
		print(self.body.shape)

	def make_field(self):
		self.gen_field(self.gen_type)
		#Create corners of view 
		if self.view != 0:
			for i in range(0,self.view):
				for j in range(0,self.view):
					self.body[i][j] = 1
					self.body[i+self.view+self.dim][j] =1
					self.body[i][j+self.view+self.dim] =1
					self.body[i+self.view+self.dim][j+self.view+self.dim] = 1
		self.body[self.y[0]][self.x[0]]=4
		self.place_fruit()
		self.update_view()
		self.print_field(self.print_type)

	def env_reset(self):
		self.end = False
		self.y.clear()
		self.x.clear()
		self.steps = 0
		self.score=0
		for i in range(0,len(self.body)):
			for j in range(0,len(self.body)):
				self.body[i][j] = 0
		self.make_field()

	def gen_field(self,type=0):
		#Generate random case
		if type >=16:
			print("Invalid field type, defaulting to 0")
			type = 0
		if type == -1:
			type = rand.randint(0,15)
		#Generate cases that add blocks
		if type&1 == 1: #Walls
			for i in range(self.view,self.view+self.dim):
				self.body[i][self.view]=1
				self.body[i][self.view+self.dim-1]=1
				self.body[self.view][i]=1
				self.body[self.view+self.dim-1][i]=1
		if type&2 == 2: #Cross
			for i in range(self.view,self.view+self.dim):
				self.body[i][self.view+int(self.dim/2)] = 1
				self.body[self.view+int(self.dim/2)][i] = 1
		if type&4==4: #Random Small Blocks
			#Generates a random number of blocks between dim/2 and dim*2
			for i in range(int(self.dim/2),rand.randint(int(self.dim/2),self.dim*2)):
				self.body[rand.randint(self.view,self.view+self.dim-1)][rand.randint(self.view,self.view+self.dim-1)] = 1
				
		#Generate Cases that remove blocks
		if type&8==8: #Random Small holes
			#removes dim/2 to dim*2 random blocks
			for i in range(int(self.dim/2),rand.randint(int(self.dim),self.dim*2)):
				j = 0 #Check to handle if there are no blocks
				while j < self.dim*self.dim:
					j+=1
					rand_x = rand.randint(self.view,self.view+self.dim-1)
					rand_y = rand.randint(self.view,self.view+self.dim-1)
					if self.body[rand_y][rand_x] == 1:
						self.body[rand_y][rand_x] = 0
						break


		#Generate Other Checks

		#Place Snake and fill gaps
		while True: #Placing the sname is a valid location
			rand_x = rand.randint(self.view,self.view+self.dim-1)
			rand_y = rand.randint(self.view,self.view+self.dim-1)
			if self.body[rand_y][rand_x] == 0:
				self.body[rand_y][rand_x] = 1
				self.y = [rand_y]
				self.x = [rand_x]
				break
		return
	def update_view(self):
		if self.view == 0:
			return
		for i in range(self.view,self.view+self.dim):
			for j in range(0,self.view):
				self.body[i][j] = self.body[i][self.dim+j]
				self.body[j][i] = self.body[self.dim+j][i]
				self.body[i][j+self.view+self.dim] = self.body[i][self.view+j]
				self.body[j+self.view+self.dim][i] = self.body[self.view+j][i]
		#In the view the snake should not have a head
		
		if self.view != 0:
			if self.x[0] >= self.dim:
				self.body[self.y[0]][self.x[0]-self.dim] = 2
			if self.y[0] >= self.dim:
				self.body[self.y[0]-self.dim][self.x[0]] = 2
			if self.x[0] < self.view*2:
				self.body[self.y[0]][self.x[0]+self.dim]=2
			if self.y[0] < self.view*2:
				self.body[self.y[0]+self.dim][self.x[0]]=2

	def update(self,movement):
		#NEEDS UPDATE FOR SNEK ON VIEW
		#0 up, 1 right, 2 down, 3 left
		#Expand the snake
		if movement == 0:
			self.y.insert(0,self.y[0]-1)
			self.x.insert(0,self.x[0])
			if self.y[0] < self.view: #Wrap around movement
				self.y[0] = self.view+self.dim-1
		elif movement == 2:
			self.y.insert(0,self.y[0]+1)
			self.x.insert(0,self.x[0])
			if self.y[0] > self.dim+self.view-1: #Wrap around movement
				self.y[0] = self.view
		elif movement == 1:
			self.y.insert(0,self.y[0])
			self.x.insert(0,self.x[0]+1)
			if self.x[0] > self.dim+self.view-1: #Wrap around movement
				self.x[0] = self.view
		elif movement == 3:
			self.y.insert(0,self.y[0])
			self.x.insert(0,self.x[0]-1)
			if self.x[0] < self.view: #Wrap around movement
				self.x[0] = self.view+self.dim-1
		#Shrink the snake back down and remove tail from board
		pop_y = self.y.pop()
		pop_x = self.x.pop()
		self.body[pop_y][pop_x] = 0
		#Remove the previous head 
		if len(self.y) > 1:
			self.body[self.y[1]][self.x[1]] = 2
		if self.body[self.y[0]][self.x[0]] == 0: #Move into emptry square
			if pop_y == self.y[0] and pop_x == self.x[0] and len(self.y) == 2: #Edge case for 2 length snake
				return -5
			self.body[self.y[0]][self.x[0]] = 4
			self.update_view()
			return 0
		elif self.body[self.y[0]][self.x[0]] == 1: #Move into wall
			return -10
		elif self.body[self.y[0]][self.x[0]] == 2: #Move into snake
			return -5
		elif self.body[self.y[0]][self.x[0]] == 3: #Move into fruit
			self.body[self.y[0]][self.x[0]] = 4
			self.body[pop_y][pop_x]= 2 #Extend snake back
			self.x.insert(len(self.x),pop_x)
			self.y.insert(len(self.y),pop_y)
			self.score+=1
			self.steps = 0
			fruit = self.place_fruit()
			self.update_view()
			return fruit

	def place_fruit(self):
		check = 0
		#UPDATE WHEN DOING VIEW
		#Checking to see if they won the game 
		for i in self.body:
			for j in i:
				if j == 0:
					check+=1
		if check == 0:
			return 100
		#Placing Fruit
		while True:
			rand_x = rand.randint(self.view,self.view+self.dim-1)
			rand_y = rand.randint(self.view,self.view+self.dim-1)
			if self.body[rand_y][rand_x] == 0:
				self.body[rand_y][rand_x] = 3
				self.fruit = [rand_y,rand_x]
				return 10

	def print_field(self,type=0):
		if type == 0:
			for i in range(0,self.dim+2):
				print("*",sep='',end='')
			print()
			for print_y in range(self.view,self.view+self.dim):
				print("*",sep='',end='')
				for print_x in range(self.view,self.view+self.dim):
					if self.body[print_y][print_x] == 0:
						print(" ",sep='',end='')
					if self.body[print_y][print_x] == 1:
						print("W",sep='',end='')
					if self.body[print_y][print_x] == 2:
						print("S",sep='',end='')
					if self.body[print_y][print_x] == 3:
						print("F",sep='',end='')
					if self.body[print_y][print_x] == 4:
						print("H",sep='',end='')
				print("*",sep='',end='')
				print()
			for i in range(0,self.dim+2):
				print("*",sep='',end='')
			print()
		elif type == 1:
			for i in range(0,self.dim+2+self.view*2):
				print("*",sep='',end='')
			print()
			for print_y in range(0,self.view*2+self.dim):
				print("*",sep='',end='')
				for print_x in range(0,self.view*2+self.dim):
					if self.body[print_y][print_x] == 0:
						print(" ",sep='',end='')
					if self.body[print_y][print_x] == 1:
						print("W",sep='',end='')
					if self.body[print_y][print_x] == 2:
						print("S",sep='',end='')
					if self.body[print_y][print_x] == 3:
						print("F",sep='',end='')
					if self.body[print_y][print_x] == 4:
						print("H",sep='',end='')
				print("*",sep='',end='')
				print()
			for i in range(0,self.dim+2+self.view*2):
				print("*",sep='',end='')
			print()

	def player_movement(self):
		ret = 0
		while ret != -10 and ret != 100 and ret != -5:
			val = input(">")
			if val == 'w':
				ret = self.update(0)
			elif val == 'd':
				ret = self.update(1)
			elif val == 's':
				ret = self.update(2)
			elif val == 'a':
				ret = self.update(3)
			print(ret)
			self.print_field(self.print_type)

		if ret == -10:
			print("You loose! Final score:",self.score)
			self.scores.append(self.score)
		if ret == -5:
			print("You loose! Final score:",self.score)
			self.scores.append(self.score)
		if ret == 100:
			print("You win! Final score:",self.score)
			self.scores.append(self.score)
		return

	def nn_movement(self, next):
		ret = self.update(next)
		if ret == -10:
			print("You loose! Final score:",self.score)
		if ret == -5:
			print("You loose! Final score:",self.score)
		if ret == 100:
			print("You win! Final score:",self.score)
		return ret

	def start_game(self):
		if self.player_type == 0:
			return self.player_movement()

	def get_board(self):
		return np.copy(self.board)

	def show_scores(self, avg = 1):
		avg_score = []
		avg_cur = 0
		for i in range(0,len(self.scores)-avg+1):
			avg_cur = 0
			for j in range(i,i+avg):
				avg_cur+=self.scores[j]
			avg_score.append(avg_cur/avg)
		x_vals = [i for i in range(1,len(avg_score)+1)]
		plt.scatter(x_vals,avg_score)
		plt.xlim(0,None)
		plt.ylim(0,None)
		plt.ylabel("Score")
		plt.xlabel("Iteration")
		plt.show()
		print("Max score:",max(self.scores))

	def get_state(self):
		''' #Code to say distance from current pos to the next block off thing
		for i in range(1,self.dim):
			if self.body[self.y[0]][(self.x[0]+i)%self.dim+self.view] ==1 or self.body[self.y[0]][(self.x[0]+i)%self.dim+self.view] ==2: #Checking x to the right
				stat1 = i
			if self.body[(self.y[0]+i)%self.dim+self.view][self.x[0]] ==1 or self.body[(self.y[0]+i)%self.dim+self.view][self.x[0]]==2: #checking y up
				stat0 = i
		for i in range(self.dim-1,0,-1):
			if self.body[self.y[0]][(self.x[0]+i)%self.dim+self.view] ==1 or self.body[self.y[0]][(self.x[0]+i)%self.dim+self.view] ==2: #Checking x to the right
				stat3 = i
			if self.body[(self.y[0]+i)%self.dim+self.view][self.x[0]] ==1 or self.body[(self.y[0]+i)%self.dim+self.view][self.x[0]]==2: #checking y up
				stat2 = i
		
		#print((self.y[0],self.x[0],self.fruit[0]-self.y[0],self.fruit[1]-self.x[0],stat0,stat1,stat2,stat3))
		state = (self.y[0],self.x[0],self.fruit[0]-self.y[0],self.fruit[1]-self.x[0],stat0,stat1,stat2,stat3)
		'''
		#Code to return if there is a wall next to snake or not 
		state = (self.y[0],self.x[0],self.fruit[0]-self.y[0],self.fruit[1]-self.x[0],int(not(self.body[self.y[0]+1][self.x[0]]!=0 and self.body[self.y[0]+1][self.x[0]]!=3)),int(not(self.body[self.y[0]][self.x[0]+1]!=0 and self.body[self.y[0]][self.x[0]+1]!=3)),int(not(self.body[self.y[0]-1][self.x[0]]!=0 and self.body[self.y[0]-1][self.x[0]]!=3)),int(not(self.body[self.y[0]][self.x[0]-1]!=0 and self.body[self.y[0]][self.x[0]-1]!=3)))
		return state
		
	
	def step(self,action): #Wrapper function used for rl.keras
		#Attempt to update the reward system, where the snek gets a reward for just moving towards the fruit
		self.steps+=1
		pre_state = self.get_state()
		if self.end == False:
			ret = self.update(action)
		else:
			ret = 0
		if ret < 0:
			self.end = True
			print("Final score:",self.score)
			self.scores.append(self.score)
		if ret == 0: #empty
			ret = -10
			#Providing reward for moving towards the fruit
			y_fd = self.fruit[0]-self.y[0]
			x_fd = self.fruit[1]-self.x[0]
			if action == 0 and y_fd <= 0: #If fruit is above snake
				ret = 10
			elif action == 2 and y_fd >= 0: #if fruit bellow snake
				ret = 10
			elif action == 1 and x_fd >=0: #if fruit to the left
				ret = 10
			elif action == 3 and x_fd <=0: #if fruit to the right
				ret = 10
		if ret == -10: #wall
			ret = -400
		if ret == -5: #snake
			ret = -400
		if ret == 10: #fruit
			ret = 100
		if self.steps == self.cut_off and self.cut_off != -1: #if the snake makes X moves without getting a fruit end the game
			self.end = True
			ret = 0
			print("Final score:",self.score)
			self.scores.append(self.score)
			
		''' return entire body as state 
		return (self.body, ret, self.end, {})
		'''
		state = self.get_state()
		#Tests to allow the snake to move however it wants when its next to blocks
		if pre_state[4]+pre_state[5]+pre_state[6]+pre_state[7] >1 and ret == -10: #If the snake is next to 2 blocks/snakes (including itself)
			ret = 10
		
		
		#state = (self.y[0],self.x[0],self.fruit[0]-self.y[0],self.fruit[1]-self.x[0],int(not(self.body[self.y[0]+1][self.x[0]]!=0 and self.body[self.y[0]+1][self.x[0]]!=3)),int(not(self.body[self.y[0]][self.x[0]+1]!=0 and self.body[self.y[0]][self.x[0]+1]!=3)),int(not(self.body[self.y[0]-1][self.x[0]]!=0 and self.body[self.y[0]-1][self.x[0]]!=3)),int(not(self.body[self.y[0]][self.x[0]-1]!=0 and self.body[self.y[0]][self.x[0]-1]!=3)))
		#print(state)
		return (state,ret,self.end,{})
		
	def reset(self): #Wrapper function used for rl.keras
		self.env_reset()
		#return self.body
		return self.get_state()
		
	def render(self,mode='human',close=False): #Wrapper function used for rl.keras
		self.print_field(self.print_type)
		
if  __name__ == "__main__":
	input_field = int(input("Field size [2-X]: "))
	input_view = int(input("View size [0-Field Size]: "))
	input_print = int(input("Print type [0: Normal | 1: Show View]: "))
	game = Field(input_field,input_view,input_print,field_gen=4)
	
	while True:
		game.start_game()
		reset_input = input("Restart [y/n]: ")
		if reset_input == "n":
			break
		game.env_reset()
	game.show_scores()










