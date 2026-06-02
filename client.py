import connection as env
import numpy as np
import os
#Utils Functions
def decay_schedule(init_value,min_value,
                    decay_ratio, max_steps,
                    log_start = -2, log_base =10):
    decay_steps = int(max_steps*decay_ratio)
    rem_steps = max_steps-decay_steps

    values = np.logspace(log_start, 0, decay_steps,
                         base = log_base, endpoint =True)
    values = (values-values.min())/(values.max() - values.min())
    values = values[::-1]
    values = (init_value-min_value)*values +min_value

    values = np.pad(values,(0, rem_steps), 'edge')

    return values

def select_action(Q,state, epsilon):
        if np.random.random() > epsilon:
            return np.argmax(Q[state])
        else:
            return np.random.randint(len(Q[state]))


arquivo_qtable = "resultado.txt"
arquivo_rewards = "recompensas.txt"


#Hyperaments
gamma = 0.95                  
init_alpha = 0.5
min_alpha = 0.01
alpha_decay_ratio = 0.5       
init_epsilon = 1.0
min_epsilon = 0.1
epsilon_decay_ratio = 0.8     
n_episodes = 10000              
max_steps = 30
state_size = 24 * 4
action_size = 3

actions = ["left","right","jump"]

Q = np.zeros((state_size,action_size))

alphas = decay_schedule(init_alpha,min_alpha,alpha_decay_ratio,n_episodes)
epsilons = decay_schedule(init_epsilon,min_epsilon,epsilon_decay_ratio,n_episodes)


if os.path.exists(arquivo_qtable):
    Q = np.loadtxt(arquivo_qtable)
    
    if os.path.exists(arquivo_rewards):
        rewards_history = np.loadtxt(arquivo_rewards).tolist()
        if type(rewards_history) is not list:
            rewards_history = [rewards_history]
    else:
        rewards_history = []
else:

    Q = np.zeros((state_size, action_size))
    rewards_history = []

episodio_inicial = len(rewards_history)
for e in range(episodio_inicial, n_episodes):
    state_d = 0
    reward_ep = 0
    while True:

        state = env.connect(2037)

        action  = select_action(Q,state_d,epsilons[e])
        action_s = actions[action]

        new_state, reward = env.get_state_reward(state, action_s)

        new_state_d = int(new_state,2) 

        reward_ep += reward
        #Acabou o Episodio 
        if(reward==-100 or reward == 300):
            Q[state_d][action] = Q[state_d][action] + alphas[e] * (reward - Q[state_d][action])
            break   
             
        Q[state_d][action] = Q[state_d][action] + alphas[e]*(reward + gamma*(np.max(Q[new_state_d]) - Q[state_d][action]))

        state_d = new_state_d
    rewards_history.append(reward_ep)
    print(f"Episode: {e}, Reward: {reward_ep}, Epsilon: {epsilons[e]}, Alpha: {alphas[e]}")

    if e % 10 == 0:
        np.savetxt(arquivo_qtable, Q, fmt="%.4f")
        np.savetxt(arquivo_rewards, rewards_history, fmt="%d")

np.savetxt(arquivo_qtable, Q, fmt="%.4f")
np.savetxt(arquivo_rewards, rewards_history, fmt="%d")



