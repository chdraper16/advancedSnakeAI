from game import *
import numpy as np
from keras import Input, Model
from keras.layers import Dense, Flatten, Conv2D, Reshape
from keras.optimizers import Adam
from keras.initializers import Constant
#Using keras-rl2
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy, LinearAnnealedPolicy 
from rl.agents.dqn import DQNAgent
from rl.callbacks import ModelIntervalCheckpoint, FileLogger
num_actions = 4
field_size = 10
view_size = 1

#Chance to take random path
epsilon = .3
#How much to value future rewards
gamma = .7
x = 0

if  __name__ == "__main__":
	print("Field gen rules:")
	print("-1: Random")
	print("0: Default empty")
	print("1: Walls all around")
	print("2: Cross")
	print("4: Random small Blocks")
	print("8: Random small Holes")
	print("OR together values wanted")
	x = int(input("Field gen: "))
	#For empty fields I found it best when epsilon is very small
	if x == 0 or x == 1:
		epsilon = .3
		gamma = .3
	#for fields that used a large number of blocks I found a higher gamma of .8 to bebetter
	elif x&4==4 or x&2==2:
		epsilon = .3
		gamma = .8 

env = Field(field_size,view_size,1,field_gen=x,cut=1000)



def model(states,actions):
	
	input_m = Input(shape=states)
	'''
	#Conv version
	x = Reshape((1,state_size,state_size,1))(input_m)
	x = Conv2D(32,(3,3))(x)
	x = Conv2D(32,(3,3))(x)
	x = Flatten()(x)
	x = Dense(16,activation='relu')(x)
	'''
	x = Flatten()(input_m)
	x = Dense(32,activation='relu',bias_initializer=Constant(0.1))(x)
	x = Dense(32,activation='relu',bias_initializer=Constant(0.1))(x)
	x = Dense(32,activation='relu',bias_initializer=Constant(0.1))(x)
	output = Dense(actions,activation='softmax')(x)
	model = Model(inputs=input_m,outputs=output)
	print(model.summary())
	return model


memory = SequentialMemory(limit = 10000,window_length=1)
policy = LinearAnnealedPolicy(EpsGreedyQPolicy(eps=epsilon), attr='eps', value_max=3, value_min=0, value_test=.5, nb_steps=500)
model = model((1,8),num_actions)

dqn = DQNAgent(model=model, gamma=gamma, nb_actions=num_actions, memory=memory, nb_steps_warmup=10,target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

def build_callbacks(env_name):
	checkpoint_weights_filename = 'dqn_' + env_name + '_weights_{step}.h5f'
	log_filename = 'dqn_{}_log.json'.format(env_name)
	callbacks = [ModelIntervalCheckpoint(checkpoint_weights_filename, interval=5000)]
	callbacks += [FileLogger(log_filename, interval=100)]
	return callbacks

callbacks = build_callbacks("SNEK")
dqn.fit(env, nb_steps=80000,visualize=False,verbose=2,callbacks=callbacks)
dqn.test(env, nb_episodes=100, visualize=True)

env.show_scores(100)
