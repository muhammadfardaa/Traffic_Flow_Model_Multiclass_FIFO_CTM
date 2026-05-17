print('-------------------------------Step 3a---------------------------------')
#CTM for CAV step 4a - Additional Traffic Cohort Selection - 2nd batch

#%% required libraries
import numpy as np #for matrix operation

#%% Cohort selection based on the value of flow rate to the next cell

def step_3a_cohort_select_all(cell_traffic_cohorts_t1, r_nextcell, u_vehdt, selected_cohorts_1st_down_cell):
    """Select the traffic cohorts that will proceed to cell i + 1 based on the amount of extra flow rate (r_nextcell) for the 2nd batch

    Args:
        cell_traffic_cohorts_t2: traffic cohorts occupying the cell i at timestep t + 1
        r_nextcell: extra flow rate to cell i + 1 at timestep t
    
    Returns:
        selected_cohorts_2nd_down_cell: cohort that will proceed to cell i + 1 at timestep t for the 2nd batch


    Additional Info:   
    The cohort selection is based on 3 conditions, namely:
        a. if r_nextcell > accumulated_cohorts_whole
        Then the selection will continue to the next cohort
        
        b. elif r_nextcell == accumulated_cohorts_whole
        Then the selection will stop at the current cohort, and the current cohort will be chosen as a whole
        
        c. elif r_nextcell < accumulated_cohorts_whole
        Then the selection will stop at the current cohort, and the current cohort will be split

    """
            

    number_of_cohorts = len(cell_traffic_cohorts_t1)
    

    if number_of_cohorts != 0:
    #This operation is executed if there is at least one cohort in the cell
        accumulated_cohorts_whole = 0
        accumulated_cohorts_actual = 0
        selected_cohorts_all_down_cell = []
        
        total_u_vehdt = r_nextcell + u_vehdt
        
        for i in range(0, number_of_cohorts):
            accumulated_cohorts_whole += cell_traffic_cohorts_t1[i,2]
            
            if total_u_vehdt > accumulated_cohorts_whole:
                selected_cohorts_all_down_cell.append(cell_traffic_cohorts_t1[i,:])
                accumulated_cohorts_actual += cell_traffic_cohorts_t1[i,2]
                continue
            
            elif total_u_vehdt == accumulated_cohorts_whole and r_nextcell != 0:
                selected_cohorts_all_down_cell.append(cell_traffic_cohorts_t1[i,:])
                accumulated_cohorts_actual += cell_traffic_cohorts_t1[i,2]
                break
            
            elif 0 < total_u_vehdt < accumulated_cohorts_whole:
                cell_traffic_cohorts_t1_splitted = cell_traffic_cohorts_t1[i,:].copy()
                cell_traffic_cohorts_t1_splitted[2] = total_u_vehdt - accumulated_cohorts_actual
                selected_cohorts_all_down_cell.append(cell_traffic_cohorts_t1_splitted)
                accumulated_cohorts_actual += cell_traffic_cohorts_t1_splitted[2]
                break
            
            else:
                break

        selected_cohorts_all_down_cell = np.array(selected_cohorts_all_down_cell)

    else:
    #This operation is executed if there is no more cohort in the cell
        selected_cohorts_all_down_cell = np.array(selected_cohorts_1st_down_cell)
    
    print('traffic cohort in the cell at timestep t :\n', cell_traffic_cohorts_t1)
    print('all selected output flow cohorts to the next cell at timestep t:\n', selected_cohorts_all_down_cell) 

    return selected_cohorts_all_down_cell    

    
    
    
