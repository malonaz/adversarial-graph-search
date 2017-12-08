# MIT 6.034 Lab 3: Games
# Written by Dylan Holmes (dxh), Jessica Noss (jmn), and 6.034 staff

from game_api import *
from boards import *
INF = float('inf')

def is_game_over_connectfour(board) :
    "Returns True if game is over, otherwise False."

    if board.count_pieces() == 6*7:
        return True
    
    for chain in board.get_all_chains():
        if len(chain) >3:
            return True
        
    return False
            

    
def next_boards_connectfour(board) :
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    
    next_boards = []
    
    if is_game_over_connectfour(board):
        return next_boards
    
    for col in range(7):
        
        if not board.is_column_full(col):
            next_boards.append(board.add_piece(col))
            
    return next_boards

        
def endgame_score_connectfour(board, is_current_player_maximizer) :
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""

    if board.count_pieces() == 6*7:
        return 0

    if is_current_player_maximizer:
        return -1000

    return 1000

    
def endgame_score_connectfour_faster(board, is_current_player_maximizer) :
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""

    if board.count_pieces() == 6*7:
        return 0

    speed_bonus = (6*7 - board.count_pieces())* 10

    if is_current_player_maximizer:
        return -1000 - speed_bonus
    return 1000 + speed_bonus
    
    
def heuristic_connectfour(board, is_current_player_maximizer) :
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    if board.count_pieces() < 4:
        return 0
    
    p1_chains = board.get_all_chains(True)
    p2_chains = board.get_all_chains(False)
    p1_chains_f = [chain for chain in p1_chains if len(chain)>1]
    p2_chains_f = [chain for chain in p2_chains if len(chain)>1]

    chain_number = len(p1_chains_f) - len(p2_chains_f)
    max_length = len(max(p1_chains, key= lambda x: len(x))) - len(max(p2_chains,key = lambda x: len(x)))
    
    if max_length>0:
        if chain_number > 0:
            score = 500
            
        else:
            score = 10
            
    elif max_length == 0:
        if chain_number > 0:
            score = 10
        elif chain_number == 0:
            score = 0
        else:
            score = -10
            
    elif max_length < 0:
        if chain_number < 0:
            score = -500
        else:
            score = -10

    if is_current_player_maximizer:
        return score
    
    return -1*score
    
    

# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### PART 2 ###########################################
# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""

    if type(state) != list:
        state = [0,state]

    current_static_evals = state[0]
    path = state[1:]
    current_state = state[-1]
    
    if current_state.is_game_over():
        return (path, current_state.get_endgame_score(),current_static_evals+1)
    
    next_states_search_list = [state + [next_state] for next_state in current_state.generate_next_states()] 
    
    dfs_max_results = [dfs_maximizing(next_state_search) for next_state_search in next_states_search_list]
    
    dfs_max_results_static_evals = [dfs_max_result[2] - current_static_evals for dfs_max_result in dfs_max_results] 

    next_state_static_evals = sum(dfs_max_results_static_evals)

    dfs_max = max(dfs_max_results, key = lambda x: x[1])
    return (dfs_max[0], dfs_max[1], next_state_static_evals)


def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""

    if type(state) != list:
        state = [0,state]

    current_static_evals = state[0]
    path = state[1:]
    current_state = state[-1]
    
    if current_state.is_game_over():
        return (path, current_state.get_endgame_score(maximize),current_static_evals+1)
    
    next_states_search_list = [state + [next_state] for next_state in current_state.generate_next_states()] 
    
    minimax_results = [minimax_endgame_search(next_state_search, not maximize) for next_state_search in next_states_search_list]
    
    minimax_results_static_evals = [minimax_result[2] - current_static_evals for minimax_result in minimax_results] 

    next_state_static_evals = sum(minimax_results_static_evals)
    
    if maximize:
        minimax = max(minimax_results, key = lambda x: x[1])

    else:
        minimax = min(minimax_results, key = lambda x: x[1])

    return (minimax[0], minimax[1],next_state_static_evals)
    
    
# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

#pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))


def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    "Performs standard minimax search.  Same return type as dfs_maximizing."
    if type(state) != list:
        state = [0,state]

    current_static_evals = state[0]
    path = state[1:]
    current_state = state[-1]
    current_depth = len(path) -1
    
    if current_state.is_game_over():
        return (path, current_state.get_endgame_score(maximize), current_static_evals + 1)

    if current_depth == depth_limit: #current_depth = (length of path -1)
        return(path, heuristic_fn(current_state.get_snapshot(),maximize),current_static_evals +1)
    
    next_states_search_list = [state + [next_state] for next_state in current_state.generate_next_states()] 
    
    minimax_results = [minimax_search(next_state_search, heuristic_fn, depth_limit, not maximize) for next_state_search in next_states_search_list]
    
    minimax_results_static_evals = [minimax_result[2] - current_static_evals for minimax_result in minimax_results] 

    next_state_static_evals = sum(minimax_results_static_evals)
    
    if maximize:
        minimax = max(minimax_results, key = lambda x: x[1])

    else:
        minimax = min(minimax_results, key = lambda x: x[1])

    return (minimax[0], minimax[1],next_state_static_evals)

# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1.  Try increasing the value of depth_limit to see what happens:

#pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=1))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    "Performs minimax with alpha-beta pruning.  Same return type as dfs_maximizing."

    if type(state) != list:
        state = [0,state]

    current_static_evals = state[0]
    path = state[1:]
    current_state = state[-1]
    current_depth = len(path) -1
    
    if current_state.is_game_over():
        return (path, current_state.get_endgame_score(maximize), current_static_evals + 1)

    if current_depth == depth_limit: #current_depth = ( length of path -1)
        return(path, heuristic_fn(current_state.get_snapshot(),maximize),current_static_evals +1)
    
    next_states_search_list = [state + [next_state] for next_state in current_state.generate_next_states()] 
    
    minimax_results = []

    if maximize:
        for next_state_search in next_states_search_list:
            if alpha >= beta:
                break
            result = minimax_search_alphabeta(next_state_search, alpha, beta, heuristic_fn, depth_limit, not maximize)
            if result[1] > alpha:
                alpha = result[1]
            minimax_results.append(result)

        minimax = max(minimax_results, key = lambda x: x[1])

    else:
        for next_state_search in next_states_search_list:
            if alpha >= beta:
                break
            result = minimax_search_alphabeta(next_state_search, alpha, beta, heuristic_fn, depth_limit, not maximize)
            if result[1] < beta:
                beta = result[1]
            minimax_results.append(result)

        minimax = min(minimax_results, key = lambda x: x[1])  
    
    minimax_results_static_evals = [minimax_result[2] - current_static_evals for minimax_result in minimax_results] 
    next_state_static_evals = sum(minimax_results_static_evals)

    return (minimax[0], minimax[1],next_state_static_evals)


# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4.  Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

#pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    anytime_value = AnytimeValue()   # TA Note: Use this to store values.
    i =1 
    while i != depth_limit +1:
        minimax = minimax_search_alphabeta(state,-INF,INF, heuristic_fn,i,maximize)
        anytime_value.set_value(minimax)
        i +=1
    return anytime_value

# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4.  Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

#print progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4)


##### PART 3: Multiple Choice ##################################################

ANSWER_1 = '4'

ANSWER_2 = '1'

ANSWER_3 = '4'

ANSWER_4 = '5'


#### SURVEY ###################################################

NAME = None
COLLABORATORS = None
HOW_MANY_HOURS_THIS_LAB_TOOK = None
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None
