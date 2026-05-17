print('-------------------------------Step 4---------------------------------')
#CTM for CAV step 4b - Traffic cohort updating - 2nd batch

#%% required libraries
import numpy as np #for matrix operation


'''
Maybe the code below is not needed
#Downstream cohort formation

#function to combine matrices

def step_4_downstream_cohort_combine(selected_cohorts_1st_down_cell, selected_cohorts_2nd_down_cell):
    """Combine the 1st and 2nd batch of traffic cohorts going downstream from cell i to cell i + 1, at timestep t. 
    The combined cohort will be used to carry out flow conservation equation in the next function
    
    Args:
    selected_cohorts_1st_down_cell: cohort that will proceed to cell i + 1 at timestep t for the 1st batch
    selected_cohorts_2nd_down_cell: cohort that will proceed to cell i + 1 at timestep t for the 2nd batch
        
    Returns:
        selected_cohorts_down_cell: combined traffic cohort that will proceed from cell i to cell i + 1 at timestep 1
    
    """
    
    #Initiate the matrix containing all cohorts going dowstream (selected_cohorts_down_cell)
    selected_cohorts_down_cell = []
 
    #Add the matrix going downstream for the 1st batch (selected_cohorts_1st_down_cell) - if there is any
    if len(selected_cohorts_1st_down_cell) > 0 or not math.isnan(len(selected_cohorts_1st_down_cell)):
        selected_cohorts_down_cell.append(selected_cohorts_1st_down_cell)

    #Add the matrix going downstream for the 2nd batch (selected_cohorts_2nd_down_cell) - if there is any
    if len(selected_cohorts_2nd_down_cell) > 0 or not math.isnan(len(selected_cohorts_2nd_down_cell)):
        #if the index index number of the last cohort in "selected cohort down_cell" is the same as teh first cohort of the 
        #selected_cohorts_down_cell, then they originates from the same cohort and hence should be combined 
        if selected_cohorts_down_cell [-1,0] == selected_cohorts_2nd_down_cell[0,0]:
            selected_cohorts_down_cell [-1,2] = selected_cohorts_down_cell [-1,2] + selected_cohorts_2nd_down_cell[0,2]
            selected_cohorts_2nd_down_cell = np.delete(selected_cohorts_2nd_down_cell, 0, axis = 0)
        
        selected_cohorts_down_cell.append(selected_cohorts_2nd_down_cell)
    
    #Return the combined cohorts going downstream
    return selected_cohorts_down_cell

'''

#%% Cohort update
#Cohort update consist of subtracting outflow traffic cohorts and adding inflow traffic cohorts

def step_4_cohort_update(cell_traffic_cohorts_t1, selected_cohorts_all_down_cell, selected_cohorts_all_up_cell):
    """Update the traffic cohort in cell i at timestep t + 1 by subtracting the selected cohorts that moves \n
    to the downstream cell (selected_cohorts_1st_down_cell & selected_cohorts_2nd_down_cell) and adding the selected cohorts that come from \n
    the upstream cell (selected_cohorts_2nd_down_cell & selected_cohorts_2nd_up_cell). Note that this operation is for the 1st and 2nd batch cohort that have been combined
    
    
    Args:
        cell_traffic_cohorts_t1: traffic cohorts occupying the cell i at timestep t
        selected_cohorts_down_cell: cohort that will proceed to cell i + 1 at timestep t (the 1st and 2nd batch have been combined)
        selected_cohorts_up_cell: cohort that will proceed to cell i at timestep t (the 1st and 2nd batch have been combined)
            
    Returns:
        cell_traffic_cohorts_t2: updated traffic cohort in cell i at timestep t + 1 
        
    """
   
    #Initiate the cell in the next timestep
    cell_traffic_cohorts_t2 = cell_traffic_cohorts_t1.copy()
    print(" Traffic cohort in the cell: ", cell_traffic_cohorts_t1 )
    
    #This operation will only be executed if there are some traffic in the cell_traffic_cohorts_t2
    #If not, then there will be no cohort going to the downstream cell
    
    #The if statement below is for 2 conditions, namely:
        #1)if the number of cohorts within cell_traffic_cohorts_t2 is not 0
        #2)the selected_cohorts_1st_down_cell can be 0 or more
   
    #Subtracting outflow traffic cohorts
    if selected_cohorts_all_down_cell.any() == True:
        for i in range(0,len(selected_cohorts_all_down_cell)):
            cell_traffic_cohorts_t2[i,2] = cell_traffic_cohorts_t2[i,2] - selected_cohorts_all_down_cell[i,2]
                
        #Mark the cohorts that are empty
        no_of_empty_cohort = 0
        for i in range (0, len(cell_traffic_cohorts_t2)):
            if cell_traffic_cohorts_t2[i,2] == 0:
                no_of_empty_cohort += 1
            else:
                break
    
        #Remove the empty cohorts from the cell
        cohort_to_delete = list(range(0,no_of_empty_cohort))
        cell_traffic_cohorts_t2 = np.delete(cell_traffic_cohorts_t2, cohort_to_delete, axis = 0)
        print("Outflow from the cell: ", selected_cohorts_all_down_cell)
    
    else:
        print(("Outflow from the cell: ", 0))

    #Adding Inflow Traffic Cohorts
    if selected_cohorts_all_up_cell.any() == True:
        cell_traffic_cohorts_t2 = np.vstack([cell_traffic_cohorts_t2, selected_cohorts_all_up_cell])
        print("Inflow to the cell: ", selected_cohorts_all_up_cell)
    
    else:
        print("Inflow to the cell: ", 0)
    
    #Update the index number of each traffic cohort
    for i in range(0,len(cell_traffic_cohorts_t2)):
        cell_traffic_cohorts_t2[i,0] = i + 1
        
    #Update the link_travel time of each traffic cohort
    for i in range(0,len(cell_traffic_cohorts_t2)):
        cell_traffic_cohorts_t2[i,4] += 1
    
    #print('traffic cohort in the cell at t2 after the 2nd batch:\n', cell_traffic_cohorts_t2)
    return cell_traffic_cohorts_t2

