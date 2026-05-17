print('-------------------------------Step 3----------------------------------')
#CTM for CAV step 4 - Extra Flow Rate Check

#%% required libraries

import numpy as np #for matrix operation

#%%calculate the proportion of CACC, ACC, NV in the selected traffic cohorts

def step_3_behaviour_proportion(selected_cohorts_1st_down_cell):
    """Calculate the proportion of CAV, as well as CACC, ACC, and NV driving behaviour in the selected traffic cohorts in cell i that \n
    will move to cell i + 1 
    
    Args:
        selected_cohorts_1st_down_cell: cohort that will proceed to cell i + 1 at timestep t for the 1st batch
        

    Returns:
        CAV_proportion: proportion of CAV vehicle in the traffic cohorts (selected_cohorts_1st_down_cell)
        CACC_proportion: proportion of CACC driving behaviour in the traffic cohorts (selected_cohorts_1st_down_cell)
        ACC_proportion: proportion of ACC driving behaviour in the traffic cohorts (selected_cohorts_1st_down_cell)
        NV_proportion: proportion of NV driving behaviour in the traffic cohorts (selected_cohorts_1st_down_cell)
            
    """
    
    CAV_proportion_numerator = 0.0
    CAV_proportion_denominator = 0.0

    for i in selected_cohorts_1st_down_cell:
        CAV_proportion_numerator += i[1] * i[2]
        CAV_proportion_denominator += i[2]
        
    if CAV_proportion_denominator != 0.0:
        CAV_proportion = float(CAV_proportion_numerator/CAV_proportion_denominator)
        CACC_proportion = float(CAV_proportion**2)
        ACC_proportion = float(CAV_proportion * (1.0 - CAV_proportion))
        NV_proportion = float(1.0 - CAV_proportion)
    
    else:
    #this condition applies if there is no traffic proceeding to the next cell, as it will generate NaN for the CAV_proportion value    
        CAV_proportion = 0.0
        CACC_proportion = 0.0
        ACC_proportion = 0.0
        NV_proportion = 0.0
    
    print("CAV_proportion:", CAV_proportion)
    print("CACC_proportion:", CACC_proportion)
    print("ACC_proportion:", ACC_proportion)
    print("NV_proportion:", NV_proportion)
    
    return CAV_proportion, CACC_proportion, ACC_proportion, NV_proportion

#%%calculate the extra traffic cohort in the next cell due to the presence of CAV

def step_3_extra_capacity_check(u_vehdt, total_traffic_t1, Q_vehdt, E_veh, vf_ms, veh_char, CACC_proportion, ACC_proportion,  NV_proportion, selected_cohorts_1st_down_cell, cell_traffic_cohorts_t1, w_ms):
    """Calculate whether there is any extra flow rate due to the presence of CAV in the selected traffic cohorts going to cell i + 1
    
    Args:
        u_vehdt: flow rate to cell i + 1 at timestep t
        total_traffic_t1: total number of vehicle contained in cell i
        Q_vehdt: maximum flow rate to cell i + 1 (veh/timestep)
        E_veh: remaining cell occupancy in cell i + 1 at timestep t 
        vf_ms: free flow speed in m/s
        veh_char: A table containing the reaction time and jam spacing of CACC, ACC, and NV
        CACC_proportion: proportion of CACC driving behaviour in the traffic cohorts (selected_cohorts_1st_down_cell)
        ACC_proportion: proportion of ACC driving behaviour in the traffic cohorts (selected_cohorts_1st_down_cell)
        NV_proportion: proportion of NV driving behaviour in the traffic cohorts (selected_cohorts_1st_down_cell)
        
    Returns:
        r_nextcell: extra flow rate due to the presence of CAV in the selected traffic cohorts going to cell i + 1
    """
    #note that r_nextcell is the extra capacity available in the next cell due to the presence of CAV

    if u_vehdt == 0:
        print("u_vehdt = 0")
        total_u_vehdt = 0
        r_nextcell = 0
        print("no extra flow rate as the amount of outflow is 0")

    elif u_vehdt == total_traffic_t1:
        print("u_vehdt = total_traffic_t1")
        total_u_vehdt = u_vehdt
        r_nextcell = 0
        print("no extra flow rate as all traffic in cell i has been covered by the outflow amount without CAV")
                
    elif u_vehdt == Q_vehdt:
        print("u_vehdt = Q_vehdt")
        Q_veh_adj = Q_vehdt * (vf_ms * veh_char.iloc[0,2] + veh_char.iloc[1,2]) / (
                            CACC_proportion * (vf_ms * veh_char.iloc[0,0] + veh_char.iloc[1,0]) +
                            ACC_proportion * (vf_ms * veh_char.iloc[0,1] + veh_char.iloc[1,1]) +
                            NV_proportion * (vf_ms * veh_char.iloc[0,2] + veh_char.iloc[1,2]))
        total_u_vehdt = Q_veh_adj
        r_nextcell = Q_veh_adj - u_vehdt
        

    elif u_vehdt == E_veh:
        print("u_vehdt = E_veh")
        #space_factor = veh_char.iloc[1,2] / (
         #           CACC_proportion * veh_char.iloc[1,0] + 
          #          ACC_proportion * veh_char.iloc[1,1] +
           #         NV_proportion * veh_char.iloc[1,2])
        
        #backward_wavespeed_factor = (((CACC_proportion * veh_char.iloc[1,0] + 
         #                             ACC_proportion * veh_char.iloc[1,1] + 
          #                            NV_proportion * veh_char.iloc[1,2]) / (CACC_proportion * veh_char.iloc[0,0] + 
           #                                                                  ACC_proportion * veh_char.iloc[0,1] + 
            #                                                                 NV_proportion * veh_char.iloc[0,2]))) / (-w_ms)
        #E_veh_adj = E_veh * space_factor * backward_wavespeed_factor
        
        total_u_vehdt = u_vehdt
        r_nextcell = 0
       
      
    #if r_nextcell > (np.sum(cell_traffic_cohorts_t1[:, -1]) - np.sum(selected_cohorts_1st_down_cell[:, -1])): 
        #r_nextcell = (np.sum(cell_traffic_cohorts_t1[:, -1]) - np.sum(selected_cohorts_1st_down_cell[:, -1]))
    
    #This if statement is to ensure that the value of r_nextcell does not exceed
    #the value of total traffic in the same cell at the previous timestep subtracted by the total traffic
    #of the selected traffic cohort going to the next cell
    #if this condition is not specified, then it is possible that the r_nextcell moves the traffic that 
    #just arrived in the cell in the current timestep, which make some traffic moves to more than one cell
    print("adjusted total flow rate due to the presence of CAV:", total_u_vehdt )
    print("extra flow rate due to the presence of CAV:", r_nextcell)
    return r_nextcell