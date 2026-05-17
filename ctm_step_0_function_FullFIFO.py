print('-------------------------------Step 0----------------------------------')
#CTM for CAV step 0 - Flow Conservation Operation

#%% Importing required libraries
import numpy as np #for matrix operation
import math #for converting nan value into 0

#%% Flow Conservation Operation
def step_0_flow_consv(cell_traffic_cohorts_t0, input_flow_t0, output_flow_t0):
    """Carry out flow conservation operation (cell occupancy + inflow - outflow) for a CTM\n
    with traffic cohorts in cell i at the current timestep (t0)
    
    Args:
        cell_traffic_cohorts_t0: traffic cohorts occupying the cell i 
        input_flow_t0: input flow cohorts going to cell i
        output_flow_t0: output flow cohorts going from cell i
    
    Return:
        cell_traffic_cohorts_t1: traffic cohorts present in cell i at the next timestep (t1) 
    
    """
    #calculating traffic cohorts contained in cell i at timestep t + 1
    cell_traffic_cohorts_t1 = np.vstack([cell_traffic_cohorts_t0, input_flow_t0])
    cell_traffic_cohorts_t1 = np.delete(cell_traffic_cohorts_t1, range(0,len(output_flow_t0)), axis = 0)

    #relabeling the cohort index number based on their order
    for i in range(len(cell_traffic_cohorts_t1)):
        cell_traffic_cohorts_t1[i,0] = i + 1
        
    print("trafic cohorts in cell i at t1:\n", cell_traffic_cohorts_t1)
    return cell_traffic_cohorts_t1
#%% Sum of all traffic within the traffic cohort
def step_0_total_traffic(cell_traffic_cohorts_t1):
    """Calculate the total number of vehicle in a cell, consisting of vehicle cohorts at timestep t
    
    Args:
        cell_traffic_cohorts_t1: traffic cohorts occupying the cell i at timestep t
        
    Return:
        total_traffic_t1: total number of vehicle by summing all cohorts
        
    """
    total_traffic_t1 = np.sum(cell_traffic_cohorts_t1[:, 2])
    
    if math.isnan(total_traffic_t1):
        #This condition applies if there is no traffic within the cell
        total_traffic_t1 = 0
        
    print("total number of traffic in cell i at timestep t:\n", total_traffic_t1)
    return total_traffic_t1
    

