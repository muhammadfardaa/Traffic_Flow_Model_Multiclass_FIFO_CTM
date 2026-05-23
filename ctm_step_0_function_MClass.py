print('-------------------------------Step 0----------------------------------')
#Step 0 - Multiclass CTM Levin and Boyles 2016 - function for total traffic

#%% Importing required libraries
import numpy as np #for matrix operation
import math #for converting nan value into 0

#%% Sum of all traffic within the traffic cohort
def step_0_total_traffic(cell_traffic_cohorts_t1):
    """Calculate the total number of vehicle in a cell, consisting of vehicle cohorts at timestep t
    
    Args:
        cell_traffic_cohorts_t1: traffic cohorts occupying the cell i at timestep t
        
    Return:
        total_traffic_t1: total number of vehicle by summing all cohorts
        
    """
    total_traffic_t1 = np.sum(cell_traffic_cohorts_t1[:, -1])
    
    if math.isnan(total_traffic_t1):
        #This condition applies if there is no traffic within the cell
        total_traffic_t1 = 0
        
    print("total traffic:\n", total_traffic_t1)
    return total_traffic_t1
    

