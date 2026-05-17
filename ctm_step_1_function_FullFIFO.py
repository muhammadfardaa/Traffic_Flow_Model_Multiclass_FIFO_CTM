print('-------------------------------Step 1----------------------------------')
#CTM for CAV step 1 - Flow Rate Calculations

#%% required libraries
import pandas as pd #for data manipulation particularly to create dataframe

#%% Function for vehicle characteristics data

def step_1_veh_char(CACC_rt, ACC_rt, NV_rt, CACC_js, ACC_js, NV_js):
    """ Converts vehicle characteristic input, including reaction time and jam spacing \n
    for CACC, ACC, and NV into a dataframe
        
    Args:
        CACC_rt (int): reaction time of CACC in sec
        ACC_rt (int): reaction time of ACC in sec
        NV_rt (int): reaction time of NV in sec
        CACC_js (int): jam spacing of CACC in m
        ACC_js (int): jam spacing of ACC in m
        NV_js (int): jam spacing of NV in m
        
    Returns:
        veh_char: A table containing the reaction time and jam spacing of \n
        CACC, ACC, and NV
    
    """
    
    veh_char = pd.DataFrame([[CACC_rt, ACC_rt, NV_rt],
                        [CACC_js, ACC_js, NV_js]])

    veh_char.index = ['reaction time (s)', 'jam spacing (m)']
    veh_char.columns = ['CACC', 'ACC', 'NV']
    print("vehicle characteristics:\n", veh_char)
    return veh_char


#%% Function for calculating maximum flow rate, maximum cell occupancy, and remaining vehicle occupancy

def step_1_Q_calc(vf_ms, veh_char, dt_s):
    """Calculate the maximum flow rate to the next cell (cell i + 1 at timestep t)
    
    Args:
        vf_ms: free flow speed in m/s
        veh_char: reaction time (s) and jam spacing (m) for each vehicle type
    
    Returns:
        Q_vehdt: maximum flow rate to cell i + 1 (veh/timestep)
    
    """
    
    #calculation of flow rate (veh/sec)
    q_vehs = vf_ms / (vf_ms * veh_char.iloc[0,2] + veh_char.iloc[1,2])

    #calculation of flow rate (veh/timestep)
    Q_vehdt = q_vehs * dt_s
    print("maximum flow rate of cell i at t:", Q_vehdt)
    return Q_vehdt

def step_1_N_calc(veh_char, dx_m):
    """Calculate the maximum cell occupany of the next cell (cell i + 1 at timestep t)
    
    Args:
        veh_char: reaction time (s) and jam spacing (m) for each vehicle type
        dx_m: cell length (m)
    
    Returns:
        N_veh: maximum cell occupancy of cell i + 1 (veh)
    
    """
    #calculation of jam density (veh/m)
    kj_vehm = 1 / veh_char.iloc[1,2]

    #calculation of maximum cell occupancy (veh)
    N_veh = kj_vehm * dx_m
    print("maximum cell occupancy of cell i+1 at timestep t:", N_veh)
    return N_veh


def step_1_w_calc(veh_char, cell_traffic_cohorts_i1_t1, vf_ms):
    """Calculate the wave speed of the next cell (cell i + 1 at timestep t)
    
    Args:
        veh_char: A table containing the reaction time and jam spacing of CACC, ACC, and NV
        cell_traffic_cohorts_i1_t1: traffic cohorts occupying the cell i + 1 at timestep t
        
    Returns:
        w_ms: wave speed (m/s)
    
    """
    
    CAV_proportion_numerator = 0.0
    CAV_proportion_denominator = 0.0

    for i in cell_traffic_cohorts_i1_t1:
        CAV_proportion_numerator += i[1] * i[2]
        CAV_proportion_denominator += i[2]
    
    if CAV_proportion_denominator != 0:
        CAV_proportion = float(CAV_proportion_numerator/CAV_proportion_denominator) 
        CACC_proportion = float(CAV_proportion**2)
        ACC_proportion = float(CAV_proportion * (1.0 - CAV_proportion))
        NV_proportion = float(1.0 - CAV_proportion)
    
    else:
    #this condition applies if the corresponding cell is empty, as it will generate NaN for the CAV_proportion value
        CAV_proportion = 0.0
        CACC_proportion = 0.0
        ACC_proportion = 0.0
        NV_proportion = 0.0
    
    print("CAV_proportion_numerator", CAV_proportion_numerator)
    print("CAV_proportion_denominator", CAV_proportion_denominator)
    print("CAV_proportion:", CAV_proportion)
    print("CACC_proportion:", CACC_proportion)
    print("ACC_proportion:", ACC_proportion)
    print("NV_proportion:", NV_proportion)
    
    #Calculation of the remaining available space in cell i + 1
    #Note that the calculation of the remaining available space considers the proportion of CAV in cell i + 1
    #This is done by adjusting the value of veh_next_cell based on the proportion of CAV in cell i + 1 and the corresponding driving behaviour
    
    if CAV_proportion_denominator != 0.0:
     #this condition applies if the corresponding cell (the next cell) is not empty, as the CAV_proportion value will not be NaN
        w_ms = - (CACC_proportion * veh_char.iloc[1,0] + 
                  ACC_proportion * veh_char.iloc[1,1] +
                  NV_proportion * veh_char.iloc[1,2]) / (
                      CACC_proportion * veh_char.iloc[0,0] + 
                      ACC_proportion * veh_char.iloc[0,1] +
                      NV_proportion * veh_char.iloc[0,2])
    else:
    #this condition applies if the corresponding cell (the next cell) is empty
        w_ms = - vf_ms
    
    print("backward wave speed of cell i+1 at timestep t:", w_ms)
    return w_ms

def step_1_E_calc(veh_char, w_ms, vf_ms, N_veh, veh_next_cell, cell_traffic_cohorts_i1_t1):
    """Calculate the remaining cell occupancy of the next cell (cell i + 1 at timestep t)
    based on the proportion of CAV, and hence CACC, ACC and NV in the next cell (i + 1) at the same timestep (t)
    
    Args:
       veh_char: 
       w_ms: wave speed (m/s)
       vf_ms: free flow speed in m/s
       N_veh: maximum cell occupancy of cell i + 1 (veh)
       veh_next_cell: total vehicle in cell i + 1 at timestep t
       
       
    Returns:
       E_veh: remaining cell occupancy in cell i + 1 at timestep t 
       
    """
    
    CAV_proportion_numerator = 0.0
    CAV_proportion_denominator = 0.0

    for i in cell_traffic_cohorts_i1_t1:
        CAV_proportion_numerator += i[1] * i[2]
        CAV_proportion_denominator += i[2]
    
    if CAV_proportion_denominator != 0:
        CAV_proportion = float(CAV_proportion_numerator/CAV_proportion_denominator) 
        CACC_proportion = float(CAV_proportion**2)
        ACC_proportion = float(CAV_proportion * (1.0 - CAV_proportion))
        NV_proportion = float(1.0 - CAV_proportion)
    
    else:
    #this condition applies if the corresponding cell is empty, as it will generate NaN for the CAV_proportion value
        CAV_proportion = 0.0
        CACC_proportion = 0.0
        ACC_proportion = 0.0
        NV_proportion = 0.0

    veh_next_cell_adj = veh_next_cell * ((CACC_proportion * veh_char.iloc[1,0] + 
              ACC_proportion * veh_char.iloc[1,1] +
              NV_proportion * veh_char.iloc[1,2]) / veh_char.iloc[1,2])
    
    #Calculate the proportion of CAV, as well as CACC, ACC, and NV in the next cell (i + 1) at the same timestep (t)
    
    E_veh = (-w_ms/vf_ms) * (N_veh - veh_next_cell_adj)
    
    print("remaining cell occupancy of cell i+1 at timestep t:",E_veh)
    return E_veh

#%% Function for calculating basic flowrate
def step_1_basic_flowrate(total_traffic_t1, Q_vehdt, E_veh):
    """Calculate the amount of flow rate to the next cell (cell i + 1) at timestep t based on 100% normal vehicle
    
    Args:
        total_traffic_t1: total number of vehicle contained in cell i
        Q_vehdt: maximum flow rate to cell i + 1 (veh/timestep)
        E_veh: remaining cell occupancy in cell i + 1 at timestep t 
    
    Returns:
        u_vehdt: flow rate to cell i + 1 at timestep t
    
    """
    
    #Calculation of flow rate to the cell i + 1
    u_vehdt = min(total_traffic_t1, Q_vehdt, E_veh)

    print("output flow to the next cell at t:", u_vehdt)
    return u_vehdt

