print('-------------------------------Step 2----------------------------------')
#CTM for CAV step 2 - Traffic cohort selection - 1st batch
#%% required libraries
import numpy as np #for matrix operation

#%% Cohort selection based on the value of flow rate to the next cell

def step_2_cohort_select_1st (cell_traffic_cohorts_t1, u_vehdt):
    
    """Select the traffic cohorts that will proceed to cell i + 1 based on the amount of flow rate (u_vehdt) for the 1st batch

    Args:
        cell_traffic_cohorts_t1: traffic cohorts occupying the cell i at timestep t
        u_vehdt: flow rate to cell i + 1 at timestep t
    
    Returns:
        selected_cohorts_1st_down_cell: cohort that will proceed to cell i + 1 at timestep t for the 1st batch
        
    Additional Info:    
    The cohort selection is based on 3 conditions, namely:
    a. if u_vehdt > accumulated_cohorts_whole
    Then the selection will continue to the next cohort
    
    b. elif u_vehdt == accumulated_cohorts_whole
    Then the selection will stop at the current cohort, and the current cohort will be chosen as a whole
    
    c. elif u_vehdt < accumulated_cohorts_whole
    Then the selection will stop at the current cohort, and the current cohort will be split

"""
    number_of_cohorts = len(cell_traffic_cohorts_t1)
    selected_cohorts_1st_down_cell = []
    
    if number_of_cohorts != 0:
    #This operation is executed if there is at least one cohort in the cell
        accumulated_cohorts_whole = 0
        accumulated_cohorts_actual = 0
       
    
        for i in range(0, number_of_cohorts):
            accumulated_cohorts_whole += cell_traffic_cohorts_t1[i,2]
            
            if u_vehdt > accumulated_cohorts_whole:
                selected_cohorts_1st_down_cell.append(cell_traffic_cohorts_t1[i,:])
                accumulated_cohorts_actual += cell_traffic_cohorts_t1[i,2]
                continue
            
            elif u_vehdt == accumulated_cohorts_whole and u_vehdt != 0:
                selected_cohorts_1st_down_cell.append(cell_traffic_cohorts_t1[i,:])
                accumulated_cohorts_actual += cell_traffic_cohorts_t1[i,2]
                break
            
            elif 0 < u_vehdt < accumulated_cohorts_whole:
                #split_factor_f = (u_vehdt - accumulated_cohorts_actual)/cell_traffic_cohorts_t1[i,2]
                cell_traffic_cohorts_t1_splitted = cell_traffic_cohorts_t1[i,:].copy()
                cell_traffic_cohorts_t1_splitted[2] = u_vehdt - accumulated_cohorts_actual
                selected_cohorts_1st_down_cell.append(cell_traffic_cohorts_t1_splitted)
                accumulated_cohorts_actual += cell_traffic_cohorts_t1_splitted[2]
                break
            
            elif u_vehdt == 0:
                #This operation is for the condition where u_vehdt is 0, namely when the road is fully disrupted or no vehicle is present in the cell
                selected_cohorts_1st_down_cell.append(np.array([0, 0, 0, 0, 0]))
                accumulated_cohorts_actual += 0
                break
        
        selected_cohorts_1st_down_cell = np.array(selected_cohorts_1st_down_cell)
    
    else:
        #This operation is executed if there is no cohort in the cell
        selected_cohorts_1st_down_cell.append(np.array([0, 0, 0, 0, 0]))
        selected_cohorts_1st_down_cell = np.array(selected_cohorts_1st_down_cell)
        
    print('traffic cohort in the cell at timestep t:\n', cell_traffic_cohorts_t1)
    print('selected output flow cohorts to the next cell at timestep t for the 1st batch:\n', selected_cohorts_1st_down_cell) 
    
    return selected_cohorts_1st_down_cell


''' This is just a test on how to insert a matrix into a cell of a larger matrix
matrix = np.zeros((1,4), dtype = np.ndarray)
matrix[0,0] = selected_cohorts
'''