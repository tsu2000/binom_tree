from typing import Dict, List, Tuple
import numpy as np

# Get the up, down, up probability, and the full dictionary of prices and payoffs for each node
def binomial_tree(S0: float, K: float, T: float, N: int, r: float, v: float, opt_type: str = 'Call', deriv_type: str = 'European') -> Tuple[float, float, float, Dict[int, List[float]]]:
    '''
    Calculates the price of a European or American option using the Binomial Options Pricing Model.

    Parameters:
    - S0 (float): Initial stock price
    - K (float): Strike price
    - T (float): Time to maturity in years
    - N (int): Number of time steps
    - r (float): Annual discount rate (Continuous compounding)
    - v (float): Annual stock volatility
    - opt_type (str, optional): Option type ('Call' or 'Put'). Defaults to 'Call'.
    - deriv_type (str, optional): Derivative type ('European' or 'American'). Defaults to 'European'.

    Returns:
        - u (float): The up rate of the stock price, rounded to 4 decimal places.
        - d (float): The down rate of the stock price, rounded to 4 decimal places.
        - p (float): The probability of the up rate, rounded to 4 decimal places.
        - pp_dict (Dict{int: List[float]}): The node number as the key, with each price and payoff amount for each node in the binomial tree.
    '''
    # Pre-compute constants
    dt = T/N
    
    u = np.exp(v * np.sqrt(dt))
    d = np.exp(-v * np.sqrt(dt))
    p = (np.exp(r * dt) - d) / (u - d)

    disc = np.exp(-r * dt)

    # Initialise empty NumPy arrays to keep track of all prices and payoffs
    prices = np.array([])
    payoffs = np.array([]) 
    
    # Initialise asset prices at maturity - Time step N
    Pr = S0 * d ** (np.arange(N, -1, -1)) * u ** (np.arange(0, N+1, 1))

    # Initialise option values at maturity
    if opt_type == 'Call':
        Pa = np.maximum(Pr - K, np.zeros(N+1))
    else:
        Pa = np.maximum(K - Pr, np.zeros(N+1))

    prices = np.concatenate((prices, Pr))
    payoffs = np.concatenate((payoffs, Pa))
    
    # Step backwards through tree
    for i in np.arange(N-1, -1, -1):
        Pr = S0 * d ** (np.arange(i, -1, -1)) * u ** (np.arange(0, i+1, 1))
        Pa[:i+1] = disc * (p * Pa[1:i+2] + (1 - p) * Pa[0:i+1])
        Pa = Pa[:-1]

        if deriv_type == 'American':
            if opt_type == 'Call':
                Pa = np.maximum(Pa, Pr - K)
            else:
                Pa = np.maximum(Pa, K - Pr)
    
        prices = np.concatenate((prices, Pr))
        payoffs = np.concatenate((payoffs, Pa))

    pp_list = [[a, b] for a, b in zip(prices, payoffs)]
    pp_dict = {i: pp_list[prices.size - i] for i in np.arange(prices.size, 0, -1).tolist()}

    return u, d, p, pp_dict

# Generate the pairs of linked nodes
def generate_step_pairs(steps: int) -> List[List[int]]:
    result = {}
    current_number = 1
    for i in range(steps):
        row_numbers = [num for num in range(current_number, current_number + i + 1)]
        result[i] = row_numbers
        current_number += (i + 1)

    pairs = []
    for k, v in result.items():
        for i in v:
            pairs.append([i, i + k + 1])
            pairs.append([i, i + k + 2])
    
    return pairs

# Get final pairs as full string to be displayed in graphviz chart
def final_pairs_str(pp_dict: Dict[int, List[float]], all_pairs: List[List[int]]) -> str:
    pp_string = {i: f'"Price {i}: {np.round(pp_dict[i][0], 4)}\lPayoff {i}: {np.round(pp_dict[i][1], 4)}\l"' for i in pp_dict}
    return ''.join([f'{pp_string[a]} -> {pp_string[b]}' for a, b in all_pairs])
