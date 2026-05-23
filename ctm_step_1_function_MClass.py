print('-------------------------------Step 1----------------------------------')
#Step 1 - Multiclass CTM Levin and Boyles 2016 - function for flow rate calculation

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

def step_1_Q_calc(CTM_matrix_current_cell, vf_ms, veh_char, dt_s):
    """Calculate the maximum flow rate to the next cell (cell i + 1 at timestep t)
    
    Args:
        CTM_matrix_cell: matrix cell i which is used for CAV and NV proportion calculation
        vf_ms: free flow speed in m/s
        veh_char: reaction time (s) and jam spacing (m) for each vehicle type
    
    Returns:
        Q_vehdt: maximum flow rate to cell i + 1 (veh/timestep)
    
    """
    CAV_number = CTM_matrix_current_cell[0][1]
    NV_number = CTM_matrix_current_cell[1][1]
    
    total_vehicle = CAV_number + NV_number
    
    if total_vehicle > 0:
        cell_CAV_proportion = CAV_number/total_vehicle
        cell_NV_proportion = 1 - cell_CAV_proportion
        
        #calculation of flow rate (veh/sec)
        q_vehs = vf_ms / (vf_ms * 
                          (cell_CAV_proportion * veh_char.iloc[0,0] +
                          cell_NV_proportion * veh_char.iloc[0,2]) + veh_char.iloc[1,2])
        
        #Note - According to Levin and Boyles (2016) formulation, the value of vehicle length (maybe equal to jam spacing) is assumed to be the same
        
    else:
        q_vehs = 0
    
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


def step_1_w_calc(veh_char, CTM_matrix_next_cell, vf_ms):
    """Calculate the wave speed of the next cell (cell i + 1 at timestep t)
    
    Args:
        CTM_matrix_next_cell: matrix cell i + 1 which is used for CAV and NV proportion calculation
        veh_char: A table containing the reaction time and jam spacing of CACC, ACC, and NV
        cell_traffic_cohorts_i1_t1: traffic cohorts occupying the cell i + 1 at timestep t
        
    Returns:
        w_ms: wave speed (m/s)
    
    """
    
    CAV_number = CTM_matrix_next_cell[0][1]
    NV_number = CTM_matrix_next_cell[1][1]
    
    total_vehicle = CAV_number + NV_number
    
    if total_vehicle > 0:
    #condition if vehicles are present in the cell
        cell_CAV_proportion = CAV_number/total_vehicle
        cell_NV_proportion = 1 - cell_CAV_proportion
        
        w_ms = - (veh_char.iloc[1, 2] / (cell_CAV_proportion * veh_char.iloc[0,0] +
                                      cell_NV_proportion * veh_char.iloc[0,2]))
    
    else:
    #condition if no vehicle is present in the cell
    #this condition applies if the corresponding cell (the next cell) is empty
        w_ms = - vf_ms
    
    print("backward wave speed of cell i+1 at timestep t:", w_ms)
    return w_ms
        
def step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell):
    """Calculate the remaining cell occupancy of the next cell (cell i + 1 at timestep t)
    
    Args: 
       w_ms: wave speed (m/s)
       vf_ms: free flow speed in m/s
       N_veh: maximum cell occupancy of cell i + 1 (veh)
       total_traffic_next_cell: total vehicle in cell i + 1 at timestep t
       
       
    Returns:
       E_veh: remaining cell occupancy in cell i + 1 at timestep t 
       
    """
    
    E_veh = (-w_ms/vf_ms) * (N_veh - total_traffic_next_cell)
    
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

