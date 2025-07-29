'''
Main Module of Stochastic Simulation
-------------------------------------------

Contains all the necessary tools to build a model and run models based on Gillespie Algorithm.

Classes:
- patch:        (Private) Simulates a single patch in the N x M space. Assume no spatial structure within a patch.
                All spatial movements are based on patches.
- model:        Stores input parameters and data generated during simulation.


Functions:
- find_nb_zero_flux:        (Private) Return pointers to a patch's neighbors under zero-flux (no-boundary) boundary condition.
- find_nb_periodical:       (Private) Return pointers to a patch's neighbors under periodical (with-booundary) boundary condition.
- find_event:               (Private) Pick a random event to happen.
- make_signal_zero_flux:    (Private) Expand event index (return value of find_event) to a detailed signal, under zero-flux boundary condition.
- make_signal_periodical:   (Private) Expand event index (return value of find_event) to a detailed signal, under periodical boundary condition.
- single_init:              (Private) Initialize a single model. Meaning of 'single': see single_test and run.
- single_test:              (Private) Run a single model.
                            'single' means a single round of model. You can run many single rounds and then take the average --- that's done by <run> function.
- run:                      Run multiple models and then take the average. All the model will use the same parameters.
                            Set a seed for reproducible results.
- demo_model:               Returns a demo model (a model object).

NOTE: Only model class and run function are intended for direct usages.
'''


import math
import numpy as np
from timeit import default_timer as timer


# data type used by model.U and model.V
UV_DTYPE = 'float64'

# data type used by model.Upi and V_pi
PI_DTYPE = 'float64'

# data type for storing rates in single_test an single_init
RATES_DTYPE = 'float64'


class patch:
    '''
    A single patch in the N x M space.
    Interacts with neighboring patches, assuming no spatial structure within a patch.
    Initialized in single_init function.

    Class Functions:

        __init__:
            Inputs:
                U, V:       initial value of U and V
                matrix:     payoff matrix for U and V. The canonical form is 2x2, here we ask for a flattened 1x4 form.
                patch_var:  np.array of [mu1, mu2, w1, w2, kappa1, kappa2]
        
        __str__:
            Print patch object in a nice way.

        set_nb_pointers:
            Set pointers to neighbors of this patch object.

        update_pi:
            Update Upi, V_pi and payoff rates (payoff rates are the first two numbers in self.pi_death_rates).
        
        update_k:
            Update natural death rates (the last two numbers in self.pi_death_rates).

        update_mig:
            Update migration rates.

        get_pi_death_rates, get_mig_rates:
            Return respective members.

        change_popu:
            Change U, V based on input signal.
    '''
    
    def __init__(self, U, V, matrix = [-0.1, 0.4, 0, 0.2], patch_var = [0.5, 0.5, 100, 100, 0.001, 0.001]):

        self.U = U                          # int, U population. Initialized upon creating object.
        self.V = V                          # int, V population
        self.Upi = 0                       # float, payoff
        self.Vpi = 0

        self.matrix = matrix                # np.array or list, len = 4, payoff matrix
        self.mu1 = patch_var[0]             # float, how much proportion of the population migrates (U) each time
        self.mu2 = patch_var[1]
        self.w1 = patch_var[2]              # float, strength of payoff-driven effect. Larger w <=> stronger payoff-driven motion
        self.w2 = patch_var[3]
        self.kappa1 = patch_var[4]          # float, carrying capacity, determines death rates
        self.kappa2 = patch_var[5]

        self.nb = None                                  # list of patch objects (pointers), point to neighbors, initialized seperatedly (after all patches are created)
        self.pi_death_rates = [0 for _ in range(4)]     # list, len = 4, rates of payoff & death
                                                        # first two are payoff rates, second two are death rates
        self.mig_rates = [0 for _ in range(8)]          # list, len = 8, migration rates, stored in an order: up, down, left, right, 
                                                        # first 4 are U's mig_rate, the last 4 are V's
        self.sum_pi_death_rates = 0                     # float, sum of pi_death_rates
        self.sum_mig_rates = 0                          # float, sum of mig_rates
        

    def __str__(self):
        self_str = ''
        self_str += 'U, V = ' + str(self.U) + ', ' + str(self.V) + '\n'
        self_str += 'pi = ' + str(self.Upi) + ', ' + str(self.Vpi) + '\n'
        self_str += 'matrix = ' + str(self.matrix) + '\n'
        self_str += 'mu1, mu2 = ' + str(self.mu1) + ', ' + str(self.mu2) + '\n'
        self_str += 'w1, w2 = ' + str(self.w1) + ', ' + str(self.w2) + '\n'
        self_str += 'kappa1, kappa2 = ' + str(self.kappa1) + ', ' + str(self.kappa2) + '\n'
        self_str += '\n'
        self_str += 'nb = ' + str(self.nb)
        self_str += 'pi_death_rates = ' + str(self.pi_death_rates) + '\n'
        self_str += 'mig_rates = ' + str(self.mig_rates) + '\n'
        self_str += 'sum_pi_death_rates = ' + str(self.sum_pi_death_rates) + '\n'
        self_str += 'sum_mig_rates = ' + str(self.sum_mig_rates) + '\n'

        return self_str
    
    
    def set_nb_pointers(self, nb):
        # nb is a list of pointers (point to patches)
        # nb is passed from the model class
        self.nb = nb
    
    
    def update_pi_k(self):
        # calculate payoff and natural death rates

        U = self.U  # bring the values to front
        V = self.V
        sum_minus_1 = U + V - 1  # this value is used several times
        
        if sum_minus_1 > 0:
            # interaction happens only if there is more than 1 individual
            
            if U != 0:
                # no payoff if U == 0
                self.Upi = (U - 1) / sum_minus_1 * self.matrix[0] + V / sum_minus_1 * self.matrix[1]
            else:
                self.Upi = 0
                
            if V != 0:
                self.Vpi = U / sum_minus_1 * self.matrix[2] + (V - 1) / sum_minus_1 * self.matrix[3]
            else:
                self.Vpi = 0
                
        else:
            # no interaction, hence no payoff, if only 1 individual
            self.Upi = 0
            self.Vpi = 0

        # update payoff rates
        self.pi_death_rates[0] = abs(U * self.Upi)
        self.pi_death_rates[1] = abs(V * self.Vpi)

        # update natural death rates
        self.pi_death_rates[2] = self.kappa1 * U * (sum_minus_1 + 1)
        self.pi_death_rates[3] = self.kappa2 * V * (sum_minus_1 + 1)

        # update sum of rates
        self.sum_pi_death_rates = sum(self.pi_death_rates)
    

    def update_mig(self):
        # calculate migration rates

        # store the 'weight' of migration, i.e. value of f/g functions for neighbors
        U_weight = [0, 0, 0, 0]
        V_weight = [0, 0, 0, 0]

        for i in range(4):
            if self.nb[i] != None:
                U_weight[i] = 1 + pow(math.e, self.w1 * self.nb[i].Upi)
                V_weight[i] = 1 + pow(math.e, self.w2 * self.nb[i].Vpi)

        mu1_U = self.mu1 * self.U
        mu2_V = self.mu2 * self.V

        mu1_U_divide_sum = mu1_U / sum(U_weight)
        mu2_V_divide_sum = mu2_V / sum(V_weight)
        
        for i in range(4):
            self.mig_rates[i] = mu1_U_divide_sum * U_weight[i]
            self.mig_rates[i + 4] = mu2_V_divide_sum * V_weight[i]

        # update sum of rates
        self.sum_mig_rates = mu1_U + mu2_V
    

    def get_sum_rates(self):
        # return sum of all 12 rates
        return self.sum_pi_death_rates + self.sum_mig_rates


    def find_event(self, expected_sum):
        # find the event within the 12 events based on expected sum-of-rates within this patch

        if expected_sum < self.sum_pi_death_rates:
            # in the first 4 events (payoff and death events)
            event = 0
            current_sum = 0
            while current_sum < expected_sum:
                current_sum += self.pi_death_rates[event]
                event += 1
            event -= 1

        else:
            # in the last 8 events (migration events):
            event = 0
            current_sum = self.sum_pi_death_rates
            while current_sum < expected_sum:
                current_sum += self.mig_rates[event]
                event += 1
            event += 3  # i.e., -= 1, then += 4 (to account for the first 4 payoff & death rates)

        return event

    
    def change_popu(self, s):
        # convert s (a signal, passed from model class) to a change in population
        
        # s = 0, 1, 2 are for U
        # s = 0 for migration IN, receive an immigrant
        if s == 0:
            self.U += 1       # receive an immigrant
        # s = 1 for migration OUT / death due to carrying capacity
        elif s == 1:
            if self.U > 0:
                self.U -= 1
        # s = 2 for natural birth / death, due to payoff
        elif s == 2:
            if self.Upi > 0:
                self.U += 1   # natural growth due to payoff
            elif self.U > 0:
                self.U -= 1   # natural death due to payoff
        
        # s = 3, 4, 5 are for V
        elif s == 3:
            self.V += 1
        elif s == 4:
            if self.V > 0:
                self.V -= 1
        else:
            if self.Vpi > 0:
                self.V += 1
            elif self.V > 0:
                self.V -= 1
                


class model:
    '''
    Store model data and input parameters.
    Initialize a model object to run models.

    Public Class Functions:

        __init__:
            Create a model object. Also initialize data storage.

        __str__:
            Print model object in a nice way.

        copy:
            Return a deep copy of self. Can choose whether to copy data as well. Default is to copy.

        clear_data:
            clear all data stored, set U, V, Upi, V_pi to zero arrays

        change_maxtime:
            Changes maxtime of self. Update data storage as well.

        set_seed:
            Set a new seed. 

        compress_data:
            compress data by only storing average values
    '''

    def __init__(self, N, M, maxtime, record_itv, sim_time, boundary, I, X, P, print_pct = 25, seed = None, UV_dtype = UV_DTYPE, pi_dtype = PI_DTYPE):

        self.check_valid_input(N, M, maxtime, record_itv, sim_time, boundary, I, X, P, print_pct)
        
        self.N = N                      # int, N x M is spatial dimension
        self.M = M                      # int, can't be 1. If want to make 1D space, use N = 1. And this model doesn't work for 1x1 space (causes NaN)
        self.maxtime = maxtime          # float or int, run model for how long time
        self.record_itv = record_itv        # float, record data every record_itv of time
        self.sim_time = sim_time        # int, run this many of rounds (of single_test)
        self.boundary = boundary        # bool, the N x M space have boundary or not (i.e., zero-flux (True) or periodical (False))
        self.I = np.array(I)            # N x M x 2 np.array, initial population. Two init-popu for every patch (U and V)
        self.X = np.array(X)            # N x M x 4 np.array, matrices. The '4' comes from 2x2 matrix flattened to 1D
        self.P = np.array(P)            # N x M x 6 np.array, 'patch variables', i.e., mu1&2, w1&2, kappa1&2
        self.print_pct = print_pct      # int, print how much percent is done, need to be non-zero
        self.seed = seed                # non-negative int, seed for random generator
        self.UV_dtype = UV_dtype        # what data type to store population, should be a float format. This value is passed to np.array. 
                                        # Default is 'float64', use lower accuracy to reduce data size.
        self.pi_dtype = pi_dtype        # what data type to store payoff, should be a float format. This value is passed to np.array. 
                                        # Default is 'float64'

        self.init_storage()                         # initialize storage bins. Put in a separate function because might want to change maxtime 
                                                    # and that doesn't need to initialze the whole object again


    def init_storage(self):
        # initialize storage bins
        self.data_empty = True                      # whether data storage bins are empty. model.run will refuse to run (raise error) if not empty.
        self.max_record = int(self.maxtime / self.record_itv)                         # int, how many data points to store sin total
        self.compress_itv = 1                       # int, intended to reduce size of data (if not 1). Updated by compress_data function
                                                    # if set to an int, say 20, mod will take average over every 20 data points and save them as new data.
                                                    # May be used over and over again to recursively reduce data size. 
                                                    # Default is 1, not to take average.
        self.U = np.zeros((self.N, self.M, self.max_record), dtype = self.UV_dtype)      # N x M x max_record np.array, float32, stores population of U in every patch over tiem
        self.V = np.zeros((self.N, self.M, self.max_record), dtype = self.UV_dtype)
        self.Upi = np.zeros((self.N, self.M, self.max_record), dtype = self.pi_dtype)   # similar to U, but for U's payoff and float 64
        self.Vpi = np.zeros((self.N, self.M, self.max_record), dtype = self.pi_dtype)


    def check_valid_input(self, N, M, maxtime, record_itv, sim_time, boundary, I, X, P, print_pct):
        # check whether the inputs are valid
        # seed, UV_dtype, pi_dtype is handled by numpy

        if (N < 1) or (M < 1):
            raise ValueError('N < 1 or M < 1')
        if (N == 1) and (M == 1):
            raise ValueError('Model fails for 1x1 space')
        if (M == 1):
            raise ValueError('Please set N = 1 for 1D space.')
        if maxtime <= 0:
            raise ValueError('Please set a positive number for maxtime')
        if record_itv <= 0:
            raise ValueError('Please set a positive number for record_itv')
        if sim_time <= 0:
            raise ValueError('Please set a positive number for sim_time')
        if type(boundary) != bool:
            raise TypeError('boundary not a bool. Please use True for zero-flux (with boundary) or False for periodical (no boundary)')
        
        if (type(I) != list) and (type(I) != np.ndarray):
            raise TypeError('Please set I as a list or np.ndarray')
        if np.array(I).shape != (N, M, 2):
            raise ValueError('Please set I as a N x M x 2 shape list or array. 2 is for init values of U, V at every patch')
        
        if (type(X) != list) and (type(X) != np.ndarray):
            raise TypeError('Please set X as a list or np.ndarray')
        if np.array(X).shape != (N, M, 4):
            raise ValueError('Please set X as a N x M x 4 shape list or array. 4 is for the flattened 2x2 payoff matrix')
        
        if (type(P) != list) and (type(P) != np.ndarray):
            raise TypeError('Please set P as a list or np.ndarray')
        if np.array(P).shape != (N, M, 6):
            raise ValueError('Please set P as a N x M x 6 shape list or array. 6 is for mu1, mu2, w1, w2, kappa1, kappa2')
        
        if print_pct <= 0:
            raise ValueError('Please use an int > 0 for print_pct or None for not printing progress.')
        

    def check_valid_data(self, data_empty, max_record, compress_itv):
        # check whether a set of data is valid, used when reading a saved model
        if type(data_empty) != bool:
            raise TypeError('data_empty not a bool')
        
        if type(max_record) != int:
            raise TypeError('max_record not an int')
        if max_record < 0:
            raise ValueError('max_record < 0')
        
        if type(compress_itv) != int:
            raise TypeError('compress_itv not an int')
        if compress_itv < 0:
            raise ValueError('compress_itv < 0')
   

    def __str__(self):
        # print this mod in a nice format

        self_str = ''
        self_str += 'N = ' + str(self.N) + '\n'
        self_str += 'M = ' + str(self.M) + '\n'
        self_str += 'maxtime = ' + str(self.maxtime) + '\n'
        self_str += 'record_itv = ' + str(self.record_itv) + '\n'
        self_str += 'sim_time = ' + str(self.sim_time) + '\n'
        self_str += 'boundary = ' + str(self.boundary) + '\n'
        self_str += 'print_pct = ' + str(self.print_pct) + '\n'
        self_str += 'seed = ' + str(self.seed) + '\n'
        self_str += 'UV_dtype = \'' + self.UV_dtype + '\'\n'
        self_str += 'pi_dtype = \'' + self.pi_dtype + '\'\n'
        self_str += 'compress_itv = ' + str(self.compress_itv) + '\n'
        self_str += '\n'

        # check whether I, X, P all same (compare all patches to (0, 0))
        I_same = True
        X_same = True
        P_same = True
        for i in range(self.N):
            for j in range(self.M):
                for k in range(2):
                    if self.I[i][j][k] != self.I[0][0][k]:
                        I_same = False
                for k in range(4):
                    if self.X[i][j][k] != self.X[0][0][k]:
                        X_same = False
                for k in range(6):
                    if self.P[i][j][k] != self.P[0][0][k]:
                        P_same = False
        
        if I_same:
            self_str += 'I all same: ' + str(self.I[0][0]) + '\n'
        else:
            self_str += 'I:\n'
            for i in range(self.N):
                for j in range(self.M):
                    self_str += str(self.I[i][j]) + ' '
                self_str += '\n'
            self_str += '\n'
        
        if X_same:
            self_str += 'X all same: ' + str(self.X[0][0]) + '\n'
        else:
            self_str += 'X:\n'
            for i in range(self.N):
                for j in range(self.M):
                    self_str += str(self.X[i][j]) + ' '
                self_str += '\n'
            self_str += '\n'

        if P_same:
            self_str += 'P all same: ' + str(self.P[0][0]) + '\n'
        else:
            self_str += 'P:\n'
            for i in range(self.N):
                for j in range(self.M):
                    self_str += str(self.P[i][j]) + ' '
                self_str += '\n'

        return self_str
    

    def copy(self, copy_data = True):
        # return deep copy of self
        # copy_data decides whether to copy data as well
        if type(copy_data) != bool:
            raise TypeError('Please give a bool as argument: whether to copy data or not')

        sim2 = model(N = self.N, M = self.M, maxtime = self.maxtime, record_itv = self.record_itv, sim_time = self.sim_time, boundary = self.boundary,
                          I = np.copy(self.I), X = np.copy(self.X), P = np.copy(self.P), 
                          print_pct = self.print_pct, seed = self.seed, UV_dtype = self.UV_dtype, pi_dtype = self.pi_dtype)

        if copy_data:
            # copy data as well
            sim2.set_data(self.data_empty, self.max_record, self.compress_itv, self.U, self.V, self.Upi, self.Vpi)

        return sim2


    def calculate_ave(self):
        # get the average value over sim_time many models
        if self.sim_time != 1:
            for i in range(self.N):
                for j in range(self.M):
                    for t in range(self.max_record):
                        self.U[i][j][t] /= self.sim_time
                        self.V[i][j][t] /= self.sim_time
                        self.Upi[i][j][t] /= self.sim_time
                        self.Vpi[i][j][t] /= self.sim_time


    def change_maxtime(self, maxtime):
        # change maxtime
        if (type(maxtime) != float) and (type(maxtime) != int):
            raise TypeError('Please pass in a float or int as the new maxtime.')
        if maxtime <= 0:
            raise ValueError('Please use a positive maxtime.')
        self.maxtime = maxtime
        self.init_storage()


    def set_seed(self, seed):
        # set seed
        self.seed = seed


    def clear_data(self):
        # clear all data stored, set all to 0
        self.init_storage()


    def set_data(self, data_empty, max_record, compress_itv, U, V, Upi, V_pi):
        # set data to the given data values
        # copies are made
        self.check_valid_data(data_empty, max_record, compress_itv)

        self.data_empty = data_empty
        self.max_record = max_record
        self.compress_itv = compress_itv
        self.U = np.copy(U)
        self.V = np.copy(V)
        self.Upi = np.copy(Upi)
        self.Vpi = np.copy(V_pi)


    def compress_data(self, compress_itv = 5):
        # compress data by only storing average values
        
        if type(compress_itv) != int:
            raise TypeError('Please use an int as compress_itv')
        if compress_itv < 1:
            raise ValueError('Please use record_itv >= 1')
        if compress_itv == 1:
            return
        
        self.compress_itv *= compress_itv  # may be reduced over and over again
        self.max_record = int(self.max_record / compress_itv)  # number of data points after reducing

        U_reduced = np.zeros((self.N, self.M, self.max_record), dtype = self.UV_dtype)
        V_reduced = np.zeros((self.N, self.M, self.max_record), dtype = self.UV_dtype)
        Upi_reduced = np.zeros((self.N, self.M, self.max_record), dtype = self.pi_dtype)
        V_pi_reduced = np.zeros((self.N, self.M, self.max_record), dtype = self.pi_dtype)

        for i in range(self.N):
            for j in range(self.M):
                for k in range(self.max_record):
                    lower = k * compress_itv  # upper and lower bound of current record_itv
                    upper = lower + compress_itv
                    U_reduced[i][j][k] = np.mean(self.U[i, j, lower : upper])
                    V_reduced[i][j][k] = np.mean(self.V[i, j, lower : upper])
                    Upi_reduced[i][j][k] = np.mean(self.Upi[i, j, lower : upper])
                    V_pi_reduced[i][j][k] = np.mean(self.Vpi[i, j, lower : upper])
        
        self.U = U_reduced
        self.V = V_reduced
        self.Upi = Upi_reduced
        self.Vpi = V_pi_reduced




def find_nb_zero_flux(N, M, i, j):
    '''
    Find neighbors of patch (i, j) in zero-flux boundary condition. i.e., the space is square with boundary.
    Return neighbors' indices in an order: up, down, left, right.
    Index will be None if no neighbor exists in that direction.
    '''
    nb_indices = []
    
    if i != 0: 
        nb_indices.append([i - 1, j])  # up
    else:
        nb_indices.append(None)    # neighbor doesn't exist
    
    if i != N - 1:
        nb_indices.append([i + 1, j])  # down
    else:
        nb_indices.append(None)
    
    if j != 0:
        nb_indices.append([i, j - 1])  # left
    else:
        nb_indices.append(None)
    
    if j != M - 1:
        nb_indices.append([i, j + 1])  # right
    else:
        nb_indices.append(None)
    
    return nb_indices




def find_nb_periodical(N, M, i, j):
    '''
    Find neighbors of patch (i, j) in periodical boundary condition. i.e., the space is a sphere.
    Return neighbors' indices in an order: up, down, left, right.
    If space not 1D, a neighbor always exists.
    If space is 1D, say N = 1, we don't allow (0, j) to migrate up & down (self-self migration is considered invalid)
    '''
    nb_indices = []
    
    # up
    if N != 1:
        if i != 0: 
            nb_indices.append([i - 1, j])
        else:
            nb_indices.append([N - 1, j])
    else:
        nb_indices.append(None)  # can't migrate to itself
    
    # down
    if N != 1:
        if i != N - 1:
            nb_indices.append([i + 1, j])
        else:
            nb_indices.append([0, j])
    else:
        nb_indices.append(None)
    
    # left
    # No need to check M == 1 because we explicitly asked for M > 1
    if j != 0:
        nb_indices.append([i, j - 1])
    else:
        nb_indices.append([i, M - 1])
    
    # right
    if j != M - 1:
        nb_indices.append([i, j + 1])
    else:
        nb_indices.append([i, 0])
        
    return nb_indices




def find_patch(expected_sum, patch_rates, sum_rates_by_row, sum_rates):
    '''
    Find which patch the event is in. Only patch index is found, patch.find_event find which event it is exactly.

    Inputs:
        expected_sum:       a random number * sum of all rates. Essentially points to a random event.
                            We want to find the patch that contains this pointer.
        patch_rates:        a N x M np.array. Stores sum of the 12 rates in every patch.
        sum_rates_by_row:   a 1D np.array with len = N. Stores the sum of the M x 12 rates in every row.
        sum_rates:          sum of all N x M x 12 rates.
    
    Returns:
        row, col:           row and column number of where the patch.
    '''
    
    # Find row first
    if expected_sum < sum_rates / 2:
        # search row forwards if in the first half of rows
        current_sum = 0
        row = 0
        while current_sum < expected_sum:
            current_sum += sum_rates_by_row[row]
            row += 1
        row -= 1
        current_sum -= sum_rates_by_row[row]  # need to subtract that row (which caused current sum to exceed expected_sum)
    else:
        # search row backwards if in the second half of rows
        current_sum = sum_rates
        row = len(patch_rates) - 1
        while current_sum > expected_sum:
            current_sum -= sum_rates_by_row[row]
            row -= 1
        row += 1
        # don't need subtraction here, as current_sum is already < expected same

    # Find col in that row
    if (expected_sum - current_sum) < sum_rates_by_row[row] / 2:
        # search col forwards if in the first half of that row
        col = 0
        while current_sum < expected_sum:
            current_sum += patch_rates[row][col]
            col += 1
        col -= 1
        current_sum -= patch_rates[row][col]  # need a subtraction
    else:
        # search col backwards if in the second half of that row
        current_sum += sum_rates_by_row[row]
        col = len(patch_rates[0]) - 1
        while current_sum > expected_sum:
            current_sum -= patch_rates[row][col]
            col -= 1
        col += 1
        # don't need subtraction

    return row, col, current_sum




def make_signal_zero_flux(i, j, e):
    '''
    Find which patch to change what based on i, j, e (event number) value, for the zero-flux boundary condition

    Inputs: 
        i, j is the position of the 'center' patch, e is which event to happen there.
        Another patch might be influenced as well if a migration event was picked.

        Possible values for e:
            e = 0 or 1: natural change of U/V due to payoff. 
                        Can be either brith or death (based on payoff is positive or negative).
                        Cooresponds to s = 2 or 5 in the patch class
            e = 2 or 3: death of U/V due to carrying capacity. 
                        Cooresponds to s = 1 or 4 in patch: make U/V -= 1
            e = 4 ~ 7:  migration events of U, patch (i, j) loses an individual, and another patch receives one.
                        we use the up-down-left-right rule for the direction. 4 means up, 5 means down, ...
                        Cooresponds to s = 0 for the mig-in patch (force U += 1), and s = 1 for the mig-out patch (force U -= 1)
            e = 8 ~ 11: migration events of V.
                        Cooresponds to s = 3 for the mig-in patch (force V += 1), and s = 4 for the mig-out patch (force V -= 1)
    '''
    if e < 6:
        if e == 0:
            return [[i, j, 2]]
        elif e == 1:
            return [[i, j, 5]]
        elif e == 2:
            return [[i, j, 1]]
        elif e == 3:
            return [[i, j, 4]]
        elif e == 4:
            return [[i, j, 1], [i - 1, j, 0]]
        else:
            return [[i, j, 1], [i + 1, j, 0]]
    else:
        if e == 6:
            return [[i, j, 1], [i, j - 1, 0]]
        elif e == 7:
            return [[i, j, 1], [i, j + 1, 0]]
        elif e == 8:
            return [[i, j, 4], [i - 1, j, 3]]
        elif e == 9:
            return [[i, j, 4], [i + 1, j, 3]]
        elif e == 10:
            return [[i, j, 4], [i, j - 1, 3]]
        elif e == 11:
            return [[i, j, 4], [i, j + 1, 3]]
        else:
            raise RuntimeError('A bug in code: invalid event number encountered:', e)  # debug line



def make_signal_periodical(N, M, i, j, e):
    '''
    Find which patch to change what based on i, j, e value, for the periodical boundary condition
    Similar to make_signal_zero_flux.
    '''
    
    if e < 6:
        if e == 0:
            return [[i, j, 2]]
        elif e == 1:
            return [[i, j, 5]]
        elif e == 2:
            return [[i, j, 1]]
        elif e == 3:
            return [[i, j, 4]]
        elif e == 4:
            if i != 0:
                return [[i, j, 1], [i - 1, j, 0]]
            else:
                return [[i, j, 1], [N - 1, j, 0]]
        else:
            if i != N - 1:
                return [[i, j, 1], [i + 1, j, 0]]
            else:
                return [[i, j, 1], [0, j, 0]]
    else:
        if e == 6:
            if j != 0:
                return [[i, j, 1], [i, j - 1, 0]]
            else:
                return [[i, j, 1], [i, M - 1, 0]]
        elif e == 7:
            if j != M - 1:
                return [[i, j, 1], [i, j + 1, 0]]
            else:
                return [[i, j, 1], [i, 0, 0]]
        elif e == 8:
            if i != 0:
                return [[i, j, 4], [i - 1, j, 3]]
            else:
                return [[i, j, 4], [N - 1, j, 3]]
        elif e == 9:
            if i != N - 1:
                return [[i, j, 4], [i + 1, j, 3]]
            else:
                return [[i, j, 4], [0, j, 3]]
        elif e == 10:
            if j != 0:
                return [[i, j, 4], [i, j - 1, 3]]
            else:
                return [[i, j, 4], [i, M - 1, 3]]
        elif e == 11:
            if j != M - 1:
                return [[i, j, 4], [i, j + 1, 3]]
            else:
                return [[i, j, 4], [i, 0, 3]]
        else:
            raise RuntimeError('A bug in code: invalid event number encountered:', e)  # debug line




def nb_need_change(ni, signal):
    '''
    Check whether a neighbor needs to change.
    Two cases don't need change: either ni is None (doesn't exist) or in signal (is a last-change patch and already updated)

    Inputs:
        ni:         index of a neighbor, might be None if patch doesn't exist.
        signal:     return value of make_signal_zero_flux or make_signal_periodical.
    
    Returns:
        True or False, whether the neighboring patch specified by ni needs change
    '''
    
    if ni == None:
        return False
    
    for si in signal:
        if ni[0] == si[0] and ni[1] == si[1]:
            return False
    
    return True




def single_init(mod, rng):
    '''
    The first major function for the model.
    Initialize all variables and run 1 round, then pass variables and results to single_test.

    Input:
        mod is a model object
        rng is random number generator (np.random.default_rng), initialized by model.run
    '''

    #### Initialize Data Storage ####

    world = [[patch(mod.I[i][j][0], mod.I[i][j][1], mod.X[i][j], mod.P[i][j]) for j in range(mod.M)] for i in range(mod.N)]  # N x M patches
    patch_rates = np.zeros((mod.N, mod.M), dtype = RATES_DTYPE)  # every patch's sum-of-12-srates
    sum_rates_by_row = np.zeros((mod.N), dtype = RATES_DTYPE)  # every row's sum-of-patch, i.e., sum of 12 * M rates in every row.
    sum_rates = 0  # sum of all N x M x 12 rates

    signal = None

    nb_indices = None
    if mod.boundary:
        nb_indices = [[find_nb_zero_flux(mod.N, mod.M, i, j) for j in range(mod.M)] for i in range(mod.N)]
    else:
        nb_indices = [[find_nb_periodical(mod.N, mod.M, i, j) for j in range(mod.M)] for i in range(mod.N)]
        
    for i in range(mod.N):
        for j in range(mod.M):
            nb = []
            for k in range(4):
                if nb_indices[i][j][k] != None:
                    # append a pointer to the patch
                    nb.append(world[nb_indices[i][j][k][0]][nb_indices[i][j][k][1]])
                else:
                    # nb doesn't exist
                    nb.append(None)
            # pass it to patch class and store
            world[i][j].set_nb_pointers(nb)
    

    #### Begin Running ####

    # initialize payoff & natural death rates
    for i in range(mod.N):
        for j in range(mod.M):
            world[i][j].update_pi_k()
    
    # initialize migration rates & the rates list
    for i in range(mod.N):
        for j in range(mod.M):
            world[i][j].update_mig()
            # store rates & sum of rates
            patch_rates[i][j] = world[i][j].get_sum_rates()
        sum_rates_by_row[i] = sum(patch_rates[i])

    sum_rates = sum(sum_rates_by_row)
    
    # pick the first random event
    expected_sum = rng.random() * sum_rates
    # find patch first
    i0, j0, current_sum = find_patch(expected_sum, patch_rates, sum_rates_by_row, sum_rates)
    # then find which event in that patch
    e0 = world[i0][j0].find_event(expected_sum - current_sum)

    # initialize signal
    if mod.boundary:
        signal = make_signal_zero_flux(i0, j0, e0)   # walls around world
    else:
        signal = make_signal_periodical(mod.N, mod.M, i0, j0, e0)  # no walls around world
    
    # change U&V based on signal
    for si in signal:
        world[si[0]][si[1]].change_popu(si[2])
        
    # time increment
    time = (1 / sum_rates) * math.log(1 / rng.random())
    
    # record
    if time > mod.record_itv:
        record_index = int(time / mod.record_itv)
        for i in range(mod.N):
            for j in range(mod.M):
                for k in range(record_index):
                    mod.U[i][j][k] += world[i][j].U
                    mod.V[i][j][k] += world[i][j].V
                    mod.Upi[i][j][k] += world[i][j].Upi
                    mod.Vpi[i][j][k] += world[i][j].Vpi
                    # we simply add to that entry, and later divide by sim_time to get the average (division in run function)
    
    return time, world, nb_indices, patch_rates, sum_rates_by_row, sum_rates, signal




def single_test(mod, front_info, end_info, update_sum_frequency, rng):
    '''
    Runs a single model, from time = 0 to mod.maxtime.
    run recursively calls single_test to get the average data. 

    Inputs:
        sim:                    a model object, created by user and carries all parameters & storage bins.
        front_info, end_info:   passed by run to show messages, like the current round number in run. Not intended for direct usages.
        update_sum_frequency:   re-calculate sums this many times in model. 
                                Our sums are gradually updated over time. So might have precision errors for large maxtime.
        rng:                    np.random.default_rng. Initialized by model.run
    '''

    # initialize helper variables
    # used to print progress, i.e., how much percent is done
    one_time = mod.maxtime / max(100, update_sum_frequency) 
    one_progress = 0
    if mod.print_pct != None:
        # print progress, x%
        print(front_info +  ' 0%' + end_info, end = '\r')
        one_progress = mod.maxtime * mod.print_pct / 100
    else:
        one_progress = 2 * mod.maxtime     # not printing

    # our sums (sum_rates_by_row and sum_rates) are gradually updated over time. This may have precision errors for large maxtime.
    # So re-sum everything every some percentage of maxtime.
    one_update_sum = mod.maxtime / update_sum_frequency

    current_time = one_time
    current_progress = one_progress
    current_update_sum = one_update_sum

    max_record = int(mod.maxtime / mod.record_itv)

    
    # initialize
    time, world, nb_indices, patch_rates, sum_rates_by_row, sum_rates, signal = single_init(mod, rng)
    record_index = int(time / mod.record_itv)
    # record_time is how much time has passed since the last record
    # if record_time > record_itv:
    #    we count how many record_itvs are there in record_time, denote the number by multi_records
    #    then store the current data in multi_records number of cells in the list
    #    and subtract record_time by the multiple of record_itv, so that record_time < record_itv
    record_time = time - record_index * mod.record_itv

    ### Large while loop ###
    
    while time < mod.maxtime:
    
        # print progress & correct error of sum_rates
        if time > current_time:
            # a new 1% of time
            current_time += one_time
            if time > current_progress:
                # print progress
                print(front_info +  ' ' + str(round(time / mod.maxtime * 100)) + '%' + end_info, end = '\r')
                current_progress += one_progress

            if time > current_update_sum:
                current_update_sum += one_update_sum
                for i in range(mod.N):
                    sum_rates_by_row[i] = sum(patch_rates[i])
                sum_rates = sum(sum_rates_by_row)

        
        # before updating last-changed patches, subtract old sum of rates (so as to update sum of rates by adding new rates later)
        for si in signal:
            # si[0] is row number, si[1] is col number
            old_patch_rate = world[si[0]][si[1]].get_sum_rates()
            sum_rates_by_row[si[0]] -= old_patch_rate
            sum_rates -= old_patch_rate

        # update last-changed patches
        # update payoff and death rates first
        for si in signal:
            world[si[0]][si[1]].update_pi_k()
        # then update migration rates, as mig_rates depend on neighbor's payoff
        for si in signal:
            world[si[0]][si[1]].update_mig()
            
            # update rates stored
            new_patch_rate = world[si[0]][si[1]].get_sum_rates()
            # update patch_rates
            patch_rates[si[0]][si[1]] = new_patch_rate
            # update sum_rate_by_row and sum_rates_by_row by adding new rates
            sum_rates_by_row[si[0]] += new_patch_rate
            sum_rates += new_patch_rate

        # update neighbors of last-changed patches
        for si in signal:
            for ni in nb_indices[si[0]][si[1]]:
                # don't need to update if the patch is a last-change patch itself or None
                # use helper function to check
                if nb_need_change(ni, signal):
                    # update migratino rates
                    world[ni[0]][ni[1]].update_mig()
                    # Note: no need to update patch_rates and sum of rates, as update_mig doesn't change total rates in a patch.
                    # sum_mig_rate is decided by mu1 * U + mu2 * V, and pi_death_rate is not changed.
               
        # pick the first random event
        expected_sum = rng.random() * sum_rates
        # find patch first
        i0, j0, current_sum = find_patch(expected_sum, patch_rates, sum_rates_by_row, sum_rates)
        # then find which event in that patch
        e0 = world[i0][j0].find_event(expected_sum - current_sum)

        # make signal
        if mod.boundary:
            signal = make_signal_zero_flux(i0, j0, e0)
        else:
            signal = make_signal_periodical(mod.N, mod.M, i0, j0, e0)

        # let the event happen
        for si in signal:
            world[si[0]][si[1]].change_popu(si[2])
        
        # increase time
        r1 = rng.random()
        dt = (1 / sum_rates) * math.log(1 / r1)
        time += dt
        record_time += dt
    
        if time < mod.maxtime:
            # if not exceeds maxtime
            if record_time > mod.record_itv:
                multi_records = int(record_time / mod.record_itv)
                record_time -= multi_records * mod.record_itv

                for i in range(mod.N):
                    for j in range(mod.M):
                        for k in range(record_index, record_index + multi_records):
                            mod.U[i][j][k] += world[i][j].U
                            mod.V[i][j][k] += world[i][j].V
                            mod.Upi[i][j][k] += world[i][j].Upi
                            mod.Vpi[i][j][k] += world[i][j].Vpi
                record_index += multi_records
        else:
            # if already exceeds maxtime
            for i in range(mod.N):
                for j in range(mod.M):
                    for k in range(record_index, max_record):
                        mod.U[i][j][k] += world[i][j].U
                        mod.V[i][j][k] += world[i][j].V
                        mod.Upi[i][j][k] += world[i][j].Upi
                        mod.Vpi[i][j][k] += world[i][j].Vpi

    ### Large while loop ends ###
    
    if mod.print_pct != None:
        print(front_info + ' 100%' + ' ' * 20, end = '\r')  # empty spaces to overwrite predicted runtime




def run(mod, predict_runtime = False, message = ''):
    '''
    Main function. Recursively calls single_test to run many models and then takes the average.

    Inputs:
    - mod is a model object.
    - predict_runtime = False will not predict how much time still needed, set to True if you want to see.
    - message is used by some functions in figures.py to print messages.
    '''

    if not mod.data_empty:
        raise RuntimeError('mod has non-empty data')
    
    start = timer()   # runtime

    mod.data_empty = False
    rng = np.random.default_rng(mod.seed)
    
    # passed to single_test to print progress
    if mod.print_pct == 0:
        mod.print_pct = 5    # default print_pct

    update_sum_frequency = 4   # re-calculate sums this many times. See input desciption of single_test
    
    ### models ###
    i = 0
    
    while i < mod.sim_time:
        # use while loop so that can go backwards if got numerical issues

        end_info = ''
        if predict_runtime:
            if i > 0:
                time_elapsed = timer() - start
                pred_runtime = time_elapsed / i * (mod.sim_time - i)
                end_info = ', ~' + str(round(pred_runtime, 2)) + 's left'
        
        front_info = ''
        if mod.print_pct != None:
            front_info = message + 'round ' + str(i) + ':'
            print(front_info + ' ' * 30, end = '\r')  # the blank spaces are to overwrite percentages, e.g. 36 %
        
        try:
            single_test(mod, front_info, end_info, update_sum_frequency, rng)
            i += 1
        except IndexError:
            update_sum_frequency *= 4
            print('Numerical issue at round ' + str(i) + '. Trying higher precision now. See doc if err repeats')
            # not increasing i: redo current round.
        
    ### models end ###

    mod.calculate_ave()
    
    stop = timer()
    print(' ' * 30, end = '\r')  # overwrite all previous prints
    print(message + 'runtime: ' + str(round(stop - start, 2)) + ' s')
    return




def demo_model():
    '''
    Returns a demo model.model object
    '''

    N = 10                  # Number of rows
    M = 10                  # Number of cols
    maxtime = 300           # how long you want the model to run
    record_itv = 0.1        # how often to record data.
    sim_time = 1            # repeat model to reduce randomness
    boundary = True         # boundary condition.

    # initial population for the N x M patches. 
    I = [[[44, 22] for _ in range(M)] for _ in range(N)]
    
    # flattened payoff matrices, total resource is 0.4, cost of fighting is 0.1
    X = [[[-0.1, 0.4, 0, 0.2] for _ in range(M)] for _ in range(N)]
    
    # patch variables
    P = [[[0.5, 0.5, 200, 200, 0.001, 0.001] for _ in range(M)] for _ in range(N)]

    print_pct = 5           # print progress
    seed = 36               # seed for random number generation
    UV_dtype = 'float32'    # data type for population
    pi_dyna = 'float64'    # data type for payoff

    # create a model object
    mod = model(N, M, maxtime, record_itv, sim_time, boundary, I, X, P, 
                            print_pct = print_pct, seed = seed, UV_dtype = UV_dtype, pi_dtype = pi_dyna)
    
    return mod


