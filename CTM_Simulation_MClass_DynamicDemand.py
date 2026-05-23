#%%CTM Simulation for Mixed Traffic (CAV and NV) Based on Levin and Boyles 2016

print("Model Name: Multiclass Cell Transmission Model")

#%%Import the required library

import pandas as pd #for data manipulation particularly to create dataframe
import numpy as np #for matrix operation
import sys #for stopping the program
import math #for math functions like cell
import matplotlib.pyplot as plt
import seaborn as sns

#%%Import required functions

from ctm_step_0_function_MClass import step_0_total_traffic
from ctm_step_1_function_MClass import step_1_veh_char, step_1_Q_calc, step_1_N_calc, step_1_w_calc, step_1_E_calc, step_1_basic_flowrate
from ctm_step_2_function_MClass import step_2_veh_proportion
from ctm_step_3_function_MClass import step_3_flow_conserv

#%%Input Data - Basic Parameters
#Demand input (flow and speed)
q_vehhr = 1600 #input flow in veh/hr
vf_kmhr = 60 #free flow speed in km/hr

#Time and space parameter input 
dt_s = 30 #timestep in sec
dx_m = 500 #cell length in m
road_length = 20500 #in meters
simulation_length = 3600 # in s

#Demand input unit conversion 
q_vehdt = q_vehhr * dt_s / 3600 #input flow in veh/timestep
vf_ms = vf_kmhr * 1000 / 3600 #free flow speed in m per sec

#Condition check whether cell length is greater than timestep times free flow speed (to ensure that vehicle can only proceed)
if dx_m >= round(dt_s * vf_ms):
    print("condition fulfilled - vehicle will not travel for more than 1 cell length in one timestep")
else:
    print("condition not fulfilled - vehicle could travel for more than 1 cell length in one timestep")
    sys.exit()
    
#Road disruption input
td_s = 1200 #disruption duration in seconds
qd_vehdt = 0.25 #factors that reduce the outflow during disruption
xd_m = 10000 #disruption location in meter
start_td_s = 150 #disruption starting time in s

#Number of cells, timesteps, and disruption timing
cell_number = int(road_length / dx_m)
warmup_timestep_number = cell_number
timestep_number = int(round(simulation_length / dt_s, 0)) + warmup_timestep_number
disruption_start_timestep = math.ceil(start_td_s / dt_s) + warmup_timestep_number
disruption_end_timestep = math.ceil((start_td_s + td_s)/dt_s) + warmup_timestep_number
cell_disruption_location = round(xd_m/dx_m)

#Vehicle driving characteristics (reaction time and jam spacing)
#reaction time (rt in sec)
CACC_rt = 0.6
ACC_rt = 1.1
NV_rt = 1.5

#jam spacing (js in m)
CACC_js = 5
ACC_js = 6
NV_js = 7

veh_char = step_1_veh_char(CACC_rt, ACC_rt, NV_rt, CACC_js, ACC_js, NV_js)

#%%Input Data - Input Flow Table to Enable Dynamic Demand

#specify the amount of input flow for each timesteps
q_vehdt = float((q_vehhr/3600) * dt_s)
input_flow_t = q_vehdt

print('input flow at t for all timesteps:\n', input_flow_t)

#create the inflow table
inflow_matrix_colnames = ['CAV proportion', 'number of vehicles']
inflow_matrix_rownames = [i for i in range(0, timestep_number + 2)]

inflow_matrix = np.zeros((timestep_number + 2, 2))
inflow_matrix = pd.DataFrame(inflow_matrix, index = inflow_matrix_rownames, columns = inflow_matrix_colnames)
inflow_matrix.columns.name = 'timestep'

#specify the timestep when the inflows enter the link
inflow_start_timestep = 0
inflow_end_timestep = disruption_end_timestep

#assign the input flow value to the inflow table
inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 1] = input_flow_t

#generate random number for CAV proportion
np.random.seed(4250)
CAV_random_proportion = np.random.uniform(0, 1, inflow_end_timestep)

#assign the random number for CAV proportion into the inflow table
inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 0] = CAV_random_proportion

#CAV proportion in the input flow
CAV_proportion_input = np.mean(inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 0])
NV_proportion_input = float(1.0 - CAV_proportion_input)

print('input flow at t for all timesteps:\n', inflow_matrix)

#%%CTM matrix Initialization

#Create names for the CTM column
CTM_colnames = [x for x in range(0, cell_number)]

#Create matrix with one row and column with the amount of cell_number, and which each cell contains the input flow value
CTM_matrix = np.empty((1, cell_number), dtype = np.ndarray)

for i in range(0, cell_number):
    CTM_matrix[0, i] = np.array([[1.0, float(0.0)], 
                                 [2.0, float(0.0)]])

#Assign the rownames into the matrix
CTM_matrix = pd.DataFrame(CTM_matrix, columns=CTM_colnames)

print('CTM matrix at timestep 0:\n', CTM_matrix)

#%%Create Matrix for Inflow and Outflow
IO_matrix_colnames = ["Inflow", "Outflow", "Accumulative Inflow", "Accumulative Outflow"]

IO_matrix = np.zeros(((timestep_number + 2), 4))
IO_matrix = pd.DataFrame(IO_matrix, columns=IO_matrix_colnames)

#%%CTM basic and static parameter

N_veh = step_1_N_calc(veh_char, dx_m)

#%%Create a dictionary to store the value of CAV and NV flow rate
flowrate_CAV = {}
flowrate_NV = {}

#%%Simulation for the Warm Up Time
print("---------------------------------------Simulation for the Warm up Time--------------------------------------------")

for i in range(0, warmup_timestep_number):
    
#Simulation for cell 1
        
    #Create empty row and assign it to the existing CTM_matrix
    CTM_matrix_i1 = np.empty((1, cell_number), dtype = np.ndarray)
    
    for z in range(0, cell_number):
        CTM_matrix_i1[0, z] = np.array([[1.0, float(0)],
                                 [2.0, float(0)]])
    
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i1))
    
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, 0])
    
    print("traffic in cell 2:")
    total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, 1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, 0], vf_ms, veh_char, dt_s)
    w_ms = step_1_w_calc(veh_char, CTM_matrix[i, 1], vf_ms)
    E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, 0])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_0"
    flowrate_NV_varname = f"flowrate_NV_{i}_0"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
    
    #Step 3 - Flow Conservation Operation
    q_vehdt_CAV = inflow_matrix.iloc[i, 0] * inflow_matrix.iloc[i, 1]
    q_vehdt_NV = (1 - inflow_matrix.iloc[i, 0]) * inflow_matrix.iloc[i, 1]
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, 0], q_vehdt_CAV, q_vehdt_NV, u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, 0][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, 0][1][1] = CTM_cell_next_timestep_NV
   
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = q_vehdt
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
    
   #Simulation for cell 2 to cell n (cell_number - 1) 
   
    for j in range(1, (cell_number - 1)):
        #Step 1 - Flow Rate Calculations
        print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
        #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
        print("traffic in cell 1:")
        total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, j])
        
        print("traffic in cell 2:")
        total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, j + 1])
        
        #Calculate the flow rate that can proceed to cell 2 at the previous timestep
        Q_vehdt = step_1_Q_calc(CTM_matrix[i, j], vf_ms, veh_char, dt_s)
        w_ms = step_1_w_calc(veh_char, CTM_matrix[i, j + 1], vf_ms)
        E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
        u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
        
        #Step 2 - Flow Rate Differentiation
        #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
        cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, j])
        
        u_vehdt_CAV = u_vehdt * cell_CAV_proportion
        print("CAV output flow to the next cell at t:", u_vehdt_CAV)
        
        u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
        print("NV output flow to the next cell at t:", u_vehdt_NV)
        
        #store the flow rate result in two dictionary
        flowrate_CAV_varname = f"flowrate_CAV_{i}_{j}"
        flowrate_NV_varname = f"flowrate_NV_{i}_{j}"
        
        flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
        flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
        
        
        #Step 3 - Flow Conservation Operation
        CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, j], flowrate_CAV[f"flowrate_CAV_{i}_{j-1}"], flowrate_NV[f"flowrate_NV_{i}_{j-1}"], u_vehdt_CAV, u_vehdt_NV)
        CTM_matrix[i + 1, j][0][1] = CTM_cell_next_timestep_CAV
        CTM_matrix[i + 1, j][1][1] = CTM_cell_next_timestep_NV
        
    #Simulation for cell n (cell_number)
        
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, cell_number-1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, cell_number-1], vf_ms, veh_char, dt_s)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, float('inf'))
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, cell_number-1])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_{cell_number-1}"
    flowrate_NV_varname = f"flowrate_NV_{i}_{cell_number-1}"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
   
    
    #Step 3 - Flow Conservation Operation
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, cell_number-1], flowrate_CAV[f"flowrate_CAV_{i}_{cell_number-2}"], flowrate_NV[f"flowrate_NV_{i}_{cell_number-2}"], u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, cell_number-1][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, cell_number-1][1][1] = CTM_cell_next_timestep_NV
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = u_vehdt
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]


#%%Simulation for the Period Before the Disruption

print("---------------------------------------Simulation for the Period Before the Disruption--------------------------------------------")

for i in range(warmup_timestep_number, disruption_start_timestep):
    
#Simulation for cell 1
        
    #Create empty row and assign it to the existing CTM_matrix
    CTM_matrix_i1 = np.empty((1, cell_number), dtype = np.ndarray)
    
    for z in range(0, cell_number):
        CTM_matrix_i1[0, z] = np.array([[1.0, float(0)],
                                 [2.0, float(0)]])
    
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i1))
    
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, 0])
    
    print("traffic in cell 2:")
    total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, 1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, 0], vf_ms, veh_char, dt_s)
    w_ms = step_1_w_calc(veh_char, CTM_matrix[i, 1], vf_ms)
    E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, 0])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_0"
    flowrate_NV_varname = f"flowrate_NV_{i}_0"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
    
    #Step 3 - Flow Conservation Operation
    q_vehdt_CAV = inflow_matrix.iloc[i, 0] * inflow_matrix.iloc[i, 1]
    q_vehdt_NV = (1 - inflow_matrix.iloc[i, 0]) * inflow_matrix.iloc[i, 1]
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, 0], q_vehdt_CAV, q_vehdt_NV, u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, 0][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, 0][1][1] = CTM_cell_next_timestep_NV
    
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = q_vehdt
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
   
    
   #Simulation for cell 2 to cell n (cell_number - 1) 
   
    for j in range(1, (cell_number - 1)):
        #Step 1 - Flow Rate Calculations
        print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
        #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
        print("traffic in cell 1:")
        total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, j])
        
        print("traffic in cell 2:")
        total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, j + 1])
        
        #Calculate the flow rate that can proceed to cell 2 at the previous timestep
        Q_vehdt = step_1_Q_calc(CTM_matrix[i, j], vf_ms, veh_char, dt_s)
        w_ms = step_1_w_calc(veh_char, CTM_matrix[i, j + 1], vf_ms)
        E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
        u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
        
        #Step 2 - Flow Rate Differentiation
        #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
        cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, j])
        
        u_vehdt_CAV = u_vehdt * cell_CAV_proportion
        print("CAV output flow to the next cell at t:", u_vehdt_CAV)
        
        u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
        print("NV output flow to the next cell at t:", u_vehdt_NV)
        
        #store the flow rate result in two dictionary
        flowrate_CAV_varname = f"flowrate_CAV_{i}_{j}"
        flowrate_NV_varname = f"flowrate_NV_{i}_{j}"
        
        flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
        flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
        
        
        #Step 3 - Flow Conservation Operation
        CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, j], flowrate_CAV[f"flowrate_CAV_{i}_{j-1}"], flowrate_NV[f"flowrate_NV_{i}_{j-1}"], u_vehdt_CAV, u_vehdt_NV)
        CTM_matrix[i + 1, j][0][1] = CTM_cell_next_timestep_CAV
        CTM_matrix[i + 1, j][1][1] = CTM_cell_next_timestep_NV
        
    #Simulation for cell n (cell_number)
        
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, cell_number-1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, cell_number-1], vf_ms, veh_char, dt_s)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, float('inf'))
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, cell_number-1])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_{cell_number-1}"
    flowrate_NV_varname = f"flowrate_NV_{i}_{cell_number-1}"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
   
    
    #Step 3 - Flow Conservation Operation
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, cell_number-1], flowrate_CAV[f"flowrate_CAV_{i}_{cell_number-2}"], flowrate_NV[f"flowrate_NV_{i}_{cell_number-2}"], u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, cell_number-1][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, cell_number-1][1][1] = CTM_cell_next_timestep_NV
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = u_vehdt
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]
    
#%%Simulation for the Period During the Disruption

print("---------------------------------------Simulation for the Period During the Disruption--------------------------------------------")

for i in range(disruption_start_timestep, disruption_end_timestep):
    
#Simulation for cell 1
        
    #Create empty row and assign it to the existing CTM_matrix
    CTM_matrix_i1 = np.empty((1, cell_number), dtype = np.ndarray)
    
    for z in range(0, cell_number):
        CTM_matrix_i1[0, z] = np.array([[1.0, float(0)],
                                 [2.0, float(0)]])
    
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i1))
    
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, 0])
    
    print("traffic in cell 2:")
    total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, 1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, 0], vf_ms, veh_char, dt_s)
    w_ms = step_1_w_calc(veh_char, CTM_matrix[i, 1], vf_ms)
    E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, 0])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_0"
    flowrate_NV_varname = f"flowrate_NV_{i}_0"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
    
    #Step 3 - Flow Conservation Operation
    q_vehdt_CAV = inflow_matrix.iloc[i, 0] * inflow_matrix.iloc[i, 1]
    q_vehdt_NV = (1 - inflow_matrix.iloc[i, 0]) * inflow_matrix.iloc[i, 1]
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, 0], q_vehdt_CAV, q_vehdt_NV, u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, 0][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, 0][1][1] = CTM_cell_next_timestep_NV
    
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = q_vehdt
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
   
    
   #Simulation for cell 2 to cell n (cell_number - 1) 
   
    for j in range(1, (cell_number - 1)):
        #Step 1 - Flow Rate Calculations
        print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
        #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
        print("traffic in cell 1:")
        total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, j])
        
        print("traffic in cell 2:")
        total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, j + 1])
        
        #Calculate the flow rate that can proceed to cell 2 at the previous timestep
        if j == cell_disruption_location - 2:
            Q_vehdt = qd_vehdt * step_1_Q_calc(CTM_matrix[i, j], vf_ms, veh_char, dt_s)
            
        else:
            Q_vehdt = step_1_Q_calc(CTM_matrix[i, j], vf_ms, veh_char, dt_s)
        
        w_ms = step_1_w_calc(veh_char, CTM_matrix[i, j + 1], vf_ms)
        E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
        u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
        
        #Step 2 - Flow Rate Differentiation
        #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
        cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, j])
        
        u_vehdt_CAV = u_vehdt * cell_CAV_proportion
        print("CAV output flow to the next cell at t:", u_vehdt_CAV)
        
        u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
        print("NV output flow to the next cell at t:", u_vehdt_NV)
        
        #store the flow rate result in two dictionary
        flowrate_CAV_varname = f"flowrate_CAV_{i}_{j}"
        flowrate_NV_varname = f"flowrate_NV_{i}_{j}"
        
        flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
        flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
        
        
        #Step 3 - Flow Conservation Operation
        CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, j], flowrate_CAV[f"flowrate_CAV_{i}_{j-1}"], flowrate_NV[f"flowrate_NV_{i}_{j-1}"], u_vehdt_CAV, u_vehdt_NV)
        CTM_matrix[i + 1, j][0][1] = CTM_cell_next_timestep_CAV
        CTM_matrix[i + 1, j][1][1] = CTM_cell_next_timestep_NV
        
    #Simulation for cell n (cell_number)
        
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, cell_number-1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, cell_number-1], vf_ms, veh_char, dt_s)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, float('inf'))
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, cell_number-1])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_{cell_number-1}"
    flowrate_NV_varname = f"flowrate_NV_{i}_{cell_number-1}"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
   
    
    #Step 3 - Flow Conservation Operation
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, cell_number-1], flowrate_CAV[f"flowrate_CAV_{i}_{cell_number-2}"], flowrate_NV[f"flowrate_NV_{i}_{cell_number-2}"], u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, cell_number-1][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, cell_number-1][1][1] = CTM_cell_next_timestep_NV
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = u_vehdt
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]
    
#%%Simulation for the Period After the Disruption

print("---------------------------------------Simulation for the Period After the Disruption--------------------------------------------")

for i in range(disruption_end_timestep, (timestep_number + 1)):
    
#Simulation for cell 1
        
    #Create empty row and assign it to the existing CTM_matrix
    CTM_matrix_i1 = np.empty((1, cell_number), dtype = np.ndarray)
    
    for z in range(0, cell_number):
        CTM_matrix_i1[0, z] = np.array([[1.0, float(0)],
                                 [2.0, float(0)]])
    
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i1))
    
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Stop the inflow after the disruption is removed
    q_vehdt = 0
    q_vehdt_CAV = 0
    q_vehdt_NV = 0
    
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, 0])
    
    print("traffic in cell 2:")
    total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, 1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, 0], vf_ms, veh_char, dt_s)
    w_ms = step_1_w_calc(veh_char, CTM_matrix[i, 1], vf_ms)
    E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, 0])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_0"
    flowrate_NV_varname = f"flowrate_NV_{i}_0"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
    
    #Step 3 - Flow Conservation Operation
    q_vehdt_CAV = inflow_matrix.iloc[i, 0] * inflow_matrix.iloc[i, 1]
    q_vehdt_NV = (1 - inflow_matrix.iloc[i, 0]) * inflow_matrix.iloc[i, 1]
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, 0], q_vehdt_CAV, q_vehdt_NV, u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, 0][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, 0][1][1] = CTM_cell_next_timestep_NV
   
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = q_vehdt
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
    
   #Simulation for cell 2 to cell n (cell_number - 1) 
   
    for j in range(1, (cell_number - 1)):
        #Step 1 - Flow Rate Calculations
        print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
        #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
        print("traffic in cell 1:")
        total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, j])
        
        print("traffic in cell 2:")
        total_traffic_next_cell = step_0_total_traffic(CTM_matrix[i, j + 1])
        
        #Calculate the flow rate that can proceed to cell 2 at the previous timestep
        Q_vehdt = step_1_Q_calc(CTM_matrix[i, j], vf_ms, veh_char, dt_s)
        w_ms = step_1_w_calc(veh_char, CTM_matrix[i, j + 1], vf_ms)
        E_veh = step_1_E_calc(w_ms, vf_ms, N_veh, total_traffic_next_cell)
        u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, E_veh)
        
        #Step 2 - Flow Rate Differentiation
        #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
        cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, j])
        
        u_vehdt_CAV = u_vehdt * cell_CAV_proportion
        print("CAV output flow to the next cell at t:", u_vehdt_CAV)
        
        u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
        print("NV output flow to the next cell at t:", u_vehdt_NV)
        
        #store the flow rate result in two dictionary
        flowrate_CAV_varname = f"flowrate_CAV_{i}_{j}"
        flowrate_NV_varname = f"flowrate_NV_{i}_{j}"
        
        flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
        flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
        
        
        #Step 3 - Flow Conservation Operation
        CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, j], flowrate_CAV[f"flowrate_CAV_{i}_{j-1}"], flowrate_NV[f"flowrate_NV_{i}_{j-1}"], u_vehdt_CAV, u_vehdt_NV)
        CTM_matrix[i + 1, j][0][1] = CTM_cell_next_timestep_CAV
        CTM_matrix[i + 1, j][1][1] = CTM_cell_next_timestep_NV
        
    #Simulation for cell n (cell_number)
        
    #Step 1 - Flow Rate Calculations
    print("--------------Step 1 - Flow Rate Calculations--------------------------------------------------------------")
    #Calculate the sum of traffic cohorts contained cell 1 and cell 2 at the previous timestep
    print("traffic in cell 1:")
    total_traffic_current_cell = step_0_total_traffic(CTM_matrix[i, cell_number-1])
    
    #Calculate the flow rate that can proceed to cell 2 at the previous timestep
    Q_vehdt = step_1_Q_calc(CTM_matrix[i, cell_number-1], vf_ms, veh_char, dt_s)
    u_vehdt = step_1_basic_flowrate(total_traffic_current_cell, Q_vehdt, float('inf'))
    
    #Step 2 - Flow Rate Differentiation
    #Calculate the flow rate that can proceed to cell 2 differentiated by CAV and NV
    cell_CAV_proportion, cell_NV_proportion = step_2_veh_proportion(CTM_matrix[i, cell_number-1])
    
    u_vehdt_CAV = u_vehdt * cell_CAV_proportion
    print("CAV output flow to the next cell at t:", u_vehdt_CAV)
    
    u_vehdt_NV = u_vehdt * (1 - cell_CAV_proportion)
    print("NV output flow to the next cell at t:", u_vehdt_NV)
    
    #store the flow rate result in two dictionary
    flowrate_CAV_varname = f"flowrate_CAV_{i}_{cell_number-1}"
    flowrate_NV_varname = f"flowrate_NV_{i}_{cell_number-1}"
    
    flowrate_CAV[flowrate_CAV_varname] = u_vehdt_CAV
    flowrate_NV[flowrate_NV_varname] = u_vehdt_NV
   
    
    #Step 3 - Flow Conservation Operation
    CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV = step_3_flow_conserv(CTM_matrix[i, cell_number-1], flowrate_CAV[f"flowrate_CAV_{i}_{cell_number-2}"], flowrate_NV[f"flowrate_NV_{i}_{cell_number-2}"], u_vehdt_CAV, u_vehdt_NV)
    CTM_matrix[i + 1, cell_number-1][0][1] = CTM_cell_next_timestep_CAV
    CTM_matrix[i + 1, cell_number-1][1][1] = CTM_cell_next_timestep_NV
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = u_vehdt
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]

#%%Store the IO_matrix for execution later with other model and scenario
IO_matrix_MClassCTM_random = IO_matrix

#%%CTM recap matrix Initialization

#Create names for the CTM recap matrix column and rows
CTM_colnames_recap = [x for x in range(0, cell_number)]

CTM_rownames_recap = []
for i in range(0, (timestep_number + 2)):
    CTM_rownames_recap.append(i)

#%%Create empty recap matrix with rows and number of timesteps + 1, and colums as the number of cells
CTM_matrix_recap = np.zeros((timestep_number + 2, cell_number))
print("Matrix Size: ", CTM_matrix_recap.shape)

#%%Assign the CTM_colnames_recap into the CTM_matrix_recap

CTM_matrix_recap = pd.DataFrame(CTM_matrix_recap, index = CTM_rownames_recap, columns=CTM_colnames_recap)
CTM_matrix_recap_nrow = CTM_matrix_recap.shape[0]
CTM_matrix_recap_ncol = CTM_matrix_recap.shape[1]

#%%Assign the total traffic in each cell of the CTM_matrix into the CTM_matrix_recap
for i in range(0, CTM_matrix_recap_nrow):
    for j in range(0, (CTM_matrix_recap_ncol)):
        CTM_matrix_recap.iloc[i, j] = step_0_total_traffic(CTM_matrix[i, j])
        
#%%Print the result
print(CTM_matrix_recap)

#%%Visualize the result
#CTM_matrix_recap_reverse = CTM_matrix_recap[::-1]
#CTM_rownames_recap_reverse = CTM_rownames_recap[::-1]

CTM_matrix_recap_transpose = np.transpose(CTM_matrix_recap)
CTM_matrix_recap_transpose_reverse = CTM_matrix_recap_transpose[::-1]
sns.heatmap(CTM_matrix_recap_transpose_reverse, cmap="coolwarm", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=100)

plt.title(f"Multiclass CTM\nCell Occupancies\nRandom CAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
plt.xlabel("Timesteps")
plt.ylabel("Cells")

plt.show()

#%%Visualize the result - Accumulative Inflow Outflow Curve
x_values = IO_matrix.index
y1 = IO_matrix["Accumulative Inflow"]
y2 = IO_matrix["Accumulative Outflow"]

sns.lineplot(x = x_values, y = y1, label = "Inflow", color='green' )
sns.lineplot(x = x_values, y = y2, label = "Outflow", color='red')

plt.fill_between(x_values, y1, y2, color="blue", alpha=0.1, label = "Total Travel Time")

#Calculate the area between the curve to find the total travel time
total_travel_time = np.trapz(np.abs(y1 - y2), x=x_values) * dt_s
print(f"Total travel time: {total_travel_time} sec or {total_travel_time/3600} hr ")

total_vehicle = IO_matrix.iloc[-1, 2]
average_travel_time = round(total_travel_time/total_vehicle,0)
print(f"Average travel time: {average_travel_time} sec or {average_travel_time/3600} hr")

freeflow_travel_time = round(cell_number * dt_s,0)
print(f"Travel time during free flow condition: {freeflow_travel_time} sec or {freeflow_travel_time/3600} hr")

plt.text(60, 150, f"total travel time: {round(total_travel_time, 0)} sec or {round(total_travel_time/3600, 2)} hr", fontsize=9, color="black")
plt.text(60, 100, f"average travel time: {round(average_travel_time, 0)} sec or {round(average_travel_time/3600, 2)} hr", fontsize=9, color="black")
plt.text(60, 50, f"free flow travel time: {round(freeflow_travel_time, 0)} sec or {round(freeflow_travel_time/3600, 2)} hr", fontsize=9, color="black")
plt.text(60, 0, f"average delay: {round(average_travel_time - freeflow_travel_time, 2)} sec or {round((average_travel_time - freeflow_travel_time)/3600, 2)} hr", fontsize=9, color="red")

plt.xlabel('Timesteps')
plt.ylabel('Accumulation (veh)')
plt.title(f'Multiclass CTM\nCummulative Inflow Outflow Curve\nRandom CAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.legend()
plt.show()

#%%Visualize the result - Outflow Rate Curve

sns.lineplot(IO_matrix.index, IO_matrix["Outflow"], color='red')

plt.xlabel('Timesteps')
plt.ylabel('Outflow per Timestep (veh)')
plt.title(f'Multiclass CTM\nOutflow Rate Curve\nRandom CAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.xlim(0, 30)
plt.xlim(0, timestep_number)
plt.legend()
plt.show()

#%%CTM recap matrix for CAV and NV Initialization

CTM_colnames_recap
CTM_rownames_recap

#%%Create empty recap matrix with rows and number of timesteps + 1, and colums as the number of cells
CTM_matrix_recap_CAV = np.zeros((timestep_number + 2, cell_number))
CTM_matrix_recap_NV = np.zeros((timestep_number + 2, cell_number))

#%%Assign the CTM_colnames_recap into the CTM_matrix_recap for CAV and NV

CTM_matrix_recap_CAV = pd.DataFrame(CTM_matrix_recap_CAV, index = CTM_rownames_recap, columns=CTM_colnames_recap)
CTM_matrix_recap_NV = pd.DataFrame(CTM_matrix_recap_NV, index = CTM_rownames_recap, columns=CTM_colnames_recap)

CTM_matrix_recap_nrow
CTM_matrix_recap_ncol

#%%Assign the total traffic in each cell of the CTM_matrix into the CTM_matrix_recap for CAV and NV
for i in range(0, CTM_matrix_recap_nrow):
    for j in range(0, (CTM_matrix_recap_ncol)):
        CTM_matrix_recap_CAV.iloc[i, j] = CTM_matrix[i, j][0][1]

for i in range(0, CTM_matrix_recap_nrow):
    for j in range(0, (CTM_matrix_recap_ncol)):
        CTM_matrix_recap_NV.iloc[i, j] = CTM_matrix[i, j][1][1]

#%%Print the result
print(CTM_matrix_recap_CAV)
print(CTM_matrix_recap_NV)

#%%Visualize the result for the CAV recap matrix

CTM_matrix_CAV_recap_transpose = np.transpose(CTM_matrix_recap_CAV)
CTM_matrix_CAV_recap_transpose_reverse = CTM_matrix_CAV_recap_transpose[::-1]
sns.heatmap(CTM_matrix_CAV_recap_transpose_reverse, cmap="Greens", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=50)

plt.title(f"Multiclass CTM\nCAV Cell Occupancies\nRandom CAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
plt.xlabel("Timesteps")
plt.ylabel("Cells")

plt.show()

#%%Visualize the result for the NV recap matrix

CTM_matrix_NV_recap_transpose = np.transpose(CTM_matrix_recap_NV)
CTM_matrix_NV_recap_transpose_reverse = CTM_matrix_NV_recap_transpose[::-1]
sns.heatmap(CTM_matrix_NV_recap_transpose_reverse, cmap="Blues", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=50)

plt.title(f"Multiclass CTM\nNV Cell Occupancies\nRandom CAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
plt.xlabel("Timesteps")
plt.ylabel("Cells")

plt.show()

#%%Visualize the percentage of CAV in each cell of the CTM matrix

#Create empty percentage recap matrix with rows and number of timesteps + 1, and colums as the number of cells
CTM_matrix_recap_perc = np.zeros((timestep_number + 2, cell_number))
print("Matrix Size: ", CTM_matrix_recap_perc.shape)

#Assign the rownames and colnames of the recap matrix
CTM_matrix_recap_perc = pd.DataFrame(CTM_matrix_recap_perc, index = CTM_rownames_recap, columns=CTM_colnames_recap)
CTM_matrix_recap_perc_nrow = CTM_matrix_recap_perc.shape[0]
CTM_matrix_recap_perc_ncol = CTM_matrix_recap_perc.shape[1]

#Assign the CAV percentage in each cell of the CTM_matrix into the CTM_matrix_recap_perc

for i in range(0, CTM_matrix_recap_nrow):
    for j in range(0, (CTM_matrix_recap_ncol)):
        
        CAV_number = CTM_matrix[i,j][0][1]
        NV_number = CTM_matrix[i,j][1][1]
        
        total_vehicle = CAV_number + NV_number

        if total_vehicle > 0:
        #condition if vehicles are present in the cell
            CAV_proportion = CAV_number/total_vehicle
            
        else:
        #this condition applies if there is no traffic present in the cell, as it will generate NaN for the CAV_proportion value    
            CAV_proportion = 0.0
            
        CTM_matrix_recap_perc.iloc[i, j] = CAV_proportion
        
print(CTM_matrix_recap_perc)
        
#%%Visualize the result of CAV percentage in each cells

CTM_matrix_recap_perc_transpose = np.transpose(CTM_matrix_recap_perc)
CTM_matrix_recap_perc_transpose_reverse = CTM_matrix_recap_perc_transpose[::-1]
sns.heatmap(CTM_matrix_recap_perc_transpose_reverse, cmap="coolwarm", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=1)

plt.title(f"Multiclass CTM\nCAV proportion within cells\nRandom CAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
plt.xlabel("Timesteps")
plt.ylabel("Cells")

plt.show()