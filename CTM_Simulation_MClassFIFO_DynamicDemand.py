#%%CTM Simulation for Mixed Traffic (CAV and NV) - Currently Developed

print("Model Name: Multiclass Full FIFO Cell Transmission Model")

#%%Import the required library

import pandas as pd #for data manipulation particularly to create dataframe
import numpy as np #for matrix operation
import sys #for stopping the program
import math #for math functions like cell
import matplotlib.pyplot as plt
import seaborn as sns

#%%Import required functions

from ctm_step_0_function_FullFIFO import step_0_total_traffic
from ctm_step_1_function_FullFIFO import step_1_veh_char, step_1_Q_calc, step_1_N_calc, step_1_w_calc, step_1_E_calc, step_1_basic_flowrate
from ctm_step_2_function_FullFIFO import step_2_cohort_select_1st
from ctm_step_3_function_FullFIFO import step_3_behaviour_proportion, step_3_extra_capacity_check
from ctm_step_3a_function_FullFIFO import step_3a_cohort_select_all
from ctm_step_4_function_FullFIFO import step_4_cohort_update
from outflow_cav_proportion_function import outflow_cav_average
from CTM_MClassFIFO_simulation_functions import cell_1_simulation, cell_mid_simulation, cell_end_simulation

#%%Import variables that define the scenario

from CTM_input_random import qd_vehdt, q_vehhr

#%%Input Data - Basic Parameters
#Demand input (flow and speed)
#q_vehhr = 1600 #input flow in veh/hr
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
#qd_vehdt = 0.25 #factors that reduce the outflow during disruption
xd_m = 10000 #disruption location in meter
start_td_s = 150 #disruption starting time in s

#Number of cells, timesteps, and disruption timing
cell_number = int(road_length / dx_m)
warmup_timestep_number = cell_number
timestep_number = int(round(simulation_length / dt_s, 0)) + warmup_timestep_number
disruption_start_timestep = math.ceil(start_td_s / dt_s) + warmup_timestep_number
disruption_end_timestep = math.ceil((start_td_s + td_s)/dt_s) + warmup_timestep_number
cell_disruption_location = round((xd_m+dx_m)/dx_m)

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
inflow_matrix_colnames = ['CAV proportion', 'number of vehicles', 'cohort_ID', 'link_traveltime']
inflow_matrix_rownames = [i for i in range(0, timestep_number + 2)]

inflow_matrix = np.zeros((timestep_number + 2, 4))
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
#activate this instead if wanting fixed CAV proportion
#CAV_random_proportion = 1.0

#assign the random number for CAV proportion into the inflow table
inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 0] = CAV_random_proportion

#assign the cohort ID into the inflow table
inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 2] = range(inflow_start_timestep+1, inflow_end_timestep+1)

#assign the link initial travel time, namely 0, into the inflow table
inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 3] = 0

#CAV proportion in the input flow
CAV_proportion_input = np.mean(inflow_matrix.iloc[inflow_start_timestep: inflow_end_timestep, 0])
NV_proportion_input = float(1.0 - CAV_proportion_input)

print('input flow at t for all timesteps:\n', inflow_matrix)

#%%Input Data - Input Flow Cohorts
input_flow_t = np.array([[1, CAV_proportion_input, q_vehdt]])

print('input flow at t for all timesteps:\n', input_flow_t)

#%%CTM matrix Initialization

#Create names for the CTM column
CTM_colnames = [x for x in range(0, cell_number)]

#Create matrix with one row and column with the amount of cell_number, and which each cell contains the input flow value
CTM_matrix = np.empty((1, cell_number), dtype = np.ndarray)

#fill in each cell with dummy cohorts - a cohort that contains nothing but required to make the program run
for i in range(0, cell_number):
    CTM_matrix[0, i] = np.array([[0, 0, 0, 0, 0]])

#Assign the rownames into the matrix
CTM_matrix = pd.DataFrame(CTM_matrix, columns=CTM_colnames)
CTM_matrix

#%%Create Matrix for Inflow and Outflow
IO_matrix_colnames = ["Inflow", "Outflow", "Accumulative Inflow", "Accumulative Outflow", "Outflows_CAV_proportion"]

IO_matrix = np.zeros(((timestep_number + 2), 5))
IO_matrix = pd.DataFrame(IO_matrix, columns=IO_matrix_colnames)
IO_matrix

#%%CTM simulation for undisrupted period

#Calculating the Q, N, w value for 100% NV
#Note that this calculation can be taken out from the loop among cells if the value of vf_ms is uniform
#Note also that the E_veh (remaining cell occupancy) value can only determined for a cell per cell basis)
#Hence, the E_veh calculation must be within the loop among cells

Q_vehdt = step_1_Q_calc(vf_ms, veh_char, dt_s)

N_veh = step_1_N_calc(veh_char, dx_m)

#%%Create a dictionary to store the value of the 1st and 2nd batch traffic flow cohorts
traffic_flowcohorts_1st = {}
traffic_flowcohorts_all = {}

#%%Simulation for the Warm Up Time
print("---------------------------------------Simulation for the Warm up Time--------------------------------------------")

for i in range(0, warmup_timestep_number):

#create new row in a CTM matrix to be filled by the simulation results

    CTM_matrix_i = np.empty((1, cell_number), dtype = np.ndarray)
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i))
    
#Simulation for cell 1
    
    CTM_matrix, traffic_flowcohorts_all, input_flow_t = cell_1_simulation(i, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = input_flow_t[0,2]
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
        
       
#Simulation for cell 2 to cell n (cell_number - 1) 
    for j in range(1, (cell_number - 1)):
        
      CTM_matrix, traffic_flowcohorts_all = cell_mid_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
         
#Simulation for cell n (cell_number)
    
    CTM_matrix, traffic_flowcohorts_all, selected_cohorts_all_i_i1 = cell_end_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = step_0_total_traffic(selected_cohorts_all_i_i1)
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]

    
#%%Simulation for the Period Before the Disruption

print("---------------------------------------Simulation for the Period Before the Disruption--------------------------------------------")

for i in range(warmup_timestep_number, disruption_start_timestep):
    
#create new row in a CTM matrix to be filled by the simulation results

    CTM_matrix_i = np.empty((1, cell_number), dtype = np.ndarray)
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i))
    
#Simulation for cell 1
    
    CTM_matrix, traffic_flowcohorts_all, input_flow_t = cell_1_simulation(i, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = input_flow_t[0,2]
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
        
       
#Simulation for cell 2 to cell n (cell_number - 1) 
    for j in range(1, (cell_number - 1)):
        
      CTM_matrix, traffic_flowcohorts_all = cell_mid_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
         
#Simulation for cell n (cell_number)
    
    CTM_matrix, traffic_flowcohorts_all, selected_cohorts_all_i_i1 = cell_end_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = step_0_total_traffic(selected_cohorts_all_i_i1)
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]
    
    
#%%Simulation during the Period During the Disruption

print("---------------------------------------Simulation during the Disruption-----------------------------------------------------------")

#Simulation for cell 1

for i in range(disruption_start_timestep, disruption_end_timestep):
    
#Create empty row and assign it to the existing CTM_matrix
    CTM_matrix_i = np.empty((1, cell_number), dtype = np.ndarray)
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i))
    
#Simulation for cell 1
    
    CTM_matrix, traffic_flowcohorts_all, input_flow_t = cell_1_simulation(i, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = input_flow_t[0,2]
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]        
       
#Simulation for cell 2 to cell n (cell_number - 1) 
    for j in range(1, (cell_number - 1)):
        
        if j == cell_disruption_location - 2:
            Q_vehdt = qd_vehdt * step_1_Q_calc(vf_ms, veh_char, dt_s)
            
        else:
            Q_vehdt = step_1_Q_calc(vf_ms, veh_char, dt_s)
       
        CTM_matrix, traffic_flowcohorts_all = cell_mid_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
         
#Simulation for cell n (cell_number)
    
    CTM_matrix, traffic_flowcohorts_all, selected_cohorts_all_i_i1 = cell_end_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = step_0_total_traffic(selected_cohorts_all_i_i1)
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]
    
    
#%%Simulation during the Period After the Disruption

print("---------------------------------------Simulation after the Disruption ends-------------------------------------------------------")

#Simulation for cell 1

Q_vehdt = step_1_Q_calc(vf_ms, veh_char, dt_s)

for i in range(disruption_end_timestep, (timestep_number + 1)):   
    #Create empty row and assign it to the existing CTM_matrix
    CTM_matrix_i = np.empty((1, cell_number), dtype = np.ndarray)
    CTM_matrix = np.vstack((CTM_matrix, CTM_matrix_i))
    
    #Simulation for cell 1
    CTM_matrix, traffic_flowcohorts_all, input_flow_t = cell_1_simulation(i, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the inflow matrix
    IO_matrix.iloc[i + 1, 0] = input_flow_t[0, 2]
    IO_matrix.iloc[i + 1, 2] = IO_matrix.iloc[i , 2] +  IO_matrix.iloc[i + 1, 0]
        
       
#Simulation for cell 2 to cell n (cell_number - 1) 
    for j in range(1, (cell_number - 1)):
        
        CTM_matrix, traffic_flowcohorts_all = cell_mid_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
         
        
#Simulation for cell n (cell_number)
    
    CTM_matrix, traffic_flowcohorts_all, selected_cohorts_all_i_i1 = cell_end_simulation(i,j, cell_number, CTM_matrix, veh_char, vf_ms, N_veh, Q_vehdt, inflow_matrix, traffic_flowcohorts_all)
    
    #Update the outflow matrix
    IO_matrix.iloc[i + 1, 1] = step_0_total_traffic(selected_cohorts_all_i_i1)
    IO_matrix.iloc[i + 1, 3] = IO_matrix.iloc[i , 3] +  IO_matrix.iloc[i + 1, 1]
    

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
sns.heatmap(CTM_matrix_recap_transpose_reverse, cmap="coolwarm", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=100, cbar_kws={'label': 'cell occupancy'})

plt.title(f"Multiclass FIFO CTM\nCell Occupancies\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
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
plt.title(f'Multiclass FIFO CTM\nCummulative Inflow Outflow Curve\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.legend()
plt.show()


#%%Visualize the result of CAV percentage in the link outflow

#obtain traffic cohorts in the link outflows
filtered_items = {
    key: value
    for key, value in traffic_flowcohorts_all.items()
    if key.endswith('_40')
}

#transform the dictionary into an array with values only
CAV_outflows_array = np.array(list(filtered_items.values()), dtype=object)

#calculate the average CAV proportion in each outflow and assign it to the IO matrix
CAV_outflows_list = []

#append value during initialisation - zero outflow
CAV_outflows_list.append(0)

for e in CAV_outflows_array:
    CAV_outflows_list.append(outflow_cav_average(e))

IO_matrix['Outflows_CAV_proportion'] = CAV_outflows_list

IO_matrix

#visualisation of CAV percentage in the link outflow + the link iutflow itself

#continuous version
sns.lineplot(x = IO_matrix.index, y = IO_matrix.iloc[:,-1], color='blue')

plt.xlabel('Timesteps')
plt.ylabel('CAV Proportion')
plt.title(f'Multiclass FIFO CTM\nCAV Proportion in the Link Outflows\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.xlim(0, 30)
plt.xlim(0, (timestep_number + 2))
plt.legend()
plt.show()

#discrete version
sns.scatterplot(x = IO_matrix.index, y = IO_matrix.iloc[:,-1], color='blue')

plt.xlabel('Timesteps')
plt.ylabel('CAV Proportion')
plt.title(f'Multiclass FIFO CTM\nCAV Proportion in the Link Outflows\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.xlim(0, 30)
plt.xlim(0, (timestep_number + 2))
plt.legend()
plt.show()


#%%Visualize the result - Outflow Rate Curve

#continuous
sns.lineplot(x = IO_matrix.index,y = IO_matrix["Outflow"], color='red')

plt.xlabel('Timesteps')
plt.ylabel('Outflow per Timestep (veh)')
plt.title(f'Multiclass FIFO CTM\nLink Outflow Rate Curve\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.xlim(0, 30)
plt.xlim(0, (timestep_number + 2))
plt.legend()
plt.show()

#discrete
sns.scatterplot(x = IO_matrix.index,y = IO_matrix["Outflow"], 
                data = IO_matrix, 
                hue = "Outflows_CAV_proportion",
                palette = "coolwarm")

plt.xlabel('Timesteps')
plt.ylabel('Outflow per Timestep (veh)')
plt.title(f'Multiclass FIFO CTM\nLink Outflow Rate Curve\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.xlim(0, 30)
plt.xlim(0, (timestep_number + 2))
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
        total_CAV = 0
        for k in CTM_matrix[i, j]:
            total_CAV += k[1] * k[2]
            CTM_matrix_recap_CAV.iloc[i, j] = total_CAV

for i in range(0, CTM_matrix_recap_nrow):
    for j in range(0, (CTM_matrix_recap_ncol)):
        total_NV = 0
        for k in CTM_matrix[i, j]:
            total_NV += (1 - k[1]) * k[2]
            CTM_matrix_recap_NV.iloc[i, j] = total_NV
        
#%%Print the result
print(CTM_matrix_recap_CAV)
print(CTM_matrix_recap_NV)

#%%Visualize the result for the CAV recap matrix

CTM_matrix_CAV_recap_transpose = np.transpose(CTM_matrix_recap_CAV)
CTM_matrix_CAV_recap_transpose_reverse = CTM_matrix_CAV_recap_transpose[::-1]
sns.heatmap(CTM_matrix_CAV_recap_transpose_reverse, cmap="Greens", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=50)

plt.title(f"Multiclass FIFO CTM\nCAV Cell Occupancies\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
plt.xlabel("Timesteps")
plt.ylabel("Cells")

plt.show()

#%%Visualize the result for the NV recap matrix

CTM_matrix_NV_recap_transpose = np.transpose(CTM_matrix_recap_NV)
CTM_matrix_NV_recap_transpose_reverse = CTM_matrix_NV_recap_transpose[::-1]
sns.heatmap(CTM_matrix_NV_recap_transpose_reverse, cmap="Blues", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=50)

plt.title(f"Multiclass FIFO CTM\nNV Cell Occupancies\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
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
        
        CAV_proportion_numerator = 0.0
        CAV_proportion_denominator = 0.0

        for k in CTM_matrix[i, j]:
            CAV_proportion_numerator += k[1] * k[2]
            CAV_proportion_denominator += k[2]
            
        if CAV_proportion_denominator != 0.0:
            CAV_proportion = float(CAV_proportion_numerator/CAV_proportion_denominator)
            
        else:
        #this condition applies if there is no traffic present in the cell, as it will generate NaN for the CAV_proportion value    
            CAV_proportion = 0.0
            
        CTM_matrix_recap_perc.iloc[i, j] = CAV_proportion
        
print(CTM_matrix_recap_perc)
        
#%%Visualize the result of CAV percentage in each cells

CTM_matrix_recap_perc_transpose = np.transpose(CTM_matrix_recap_perc)
CTM_matrix_recap_perc_transpose_reverse = CTM_matrix_recap_perc_transpose[::-1]
sns.heatmap(CTM_matrix_recap_perc_transpose_reverse, cmap="coolwarm", annot = False, fmt = ".2f", linewidths =.5, vmin=0, vmax=1, cbar_kws={'label': 'cell CAV proportion'})

plt.title(f"Multiclass FIFO CTM\nCAV proportion within cells\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}")
plt.xlabel("Timesteps")
plt.ylabel("Cells")

plt.show()

#%%Visualize the result of CAV percentage in the last cell

sns.lineplot(x = CTM_matrix_recap_perc.index, y = CTM_matrix_recap_perc.iloc[:,-1], color='green')

plt.xlabel('Timesteps')
plt.ylabel('CAV Proportion')
plt.title(f'Multiclass FIFO CTM\nCAV Proportion in the Last Cell\nCAV Proportion: Uniform Distribution\nDisruption Factor: {qd_vehdt}')

plt.xlim(0, 30)
plt.xlim(0, (timestep_number + 2))
plt.legend()
plt.show()



#%%visualisation of link travel time for each cohort
#recall the traffic cohorts in the outflow
CAV_outflows_array

# Create an empty list containing all cohorts that have exited the link
CAV_outflows_cohort_list = []

# Get the cohorts in the CAV_outflow_array one by one and include that into the list
for c in CAV_outflows_array:
    for d in c:
        if d[3] != 0:
            CAV_outflows_cohort_list.append(d)
        else:
            continue

# Transform the list into a dataframe for easier manipulation
CAV_outflows_cohort_df = pd.DataFrame(CAV_outflows_cohort_list, columns = ['cohort_order','CAV proportion', 'number of vehicles', 'cohort_ID', 'link_traveltime'] )

# =================================================================================
# METRIC CALCULATIONS
# =================================================================================

# 1. Base network variables
free_flow_travel_time = cell_number
link_length = cell_number * dx_m

# 2. Vehicle and travel time totals
total_vehicles = CAV_outflows_cohort_df['number of vehicles'].sum()
total_link_travel_time = (CAV_outflows_cohort_df['link_traveltime'] * CAV_outflows_cohort_df['number of vehicles']).sum()
avg_vehicle_traveltime = total_link_travel_time / total_vehicles if total_vehicles > 0 else 0

# 3. Performance metrics
total_delay = total_link_travel_time - (total_vehicles * free_flow_travel_time)
avg_delay_per_vehicle = total_delay / total_vehicles if total_vehicles > 0 else 0
avg_speed_per_vehicle = link_length / avg_vehicle_traveltime if avg_vehicle_traveltime > 0 else 0

# Print performance summary to terminal
print("--- LINK PERFORMANCE METRICS ---")
print(f"Total Vehicles Exited:      {total_vehicles:.0f}")
print(f"Total Link Delay (TD):      {total_delay:.2f} veh.timesteps")
print(f"Average Delay (AD):         {avg_delay_per_vehicle:.2f} timesteps")
print(f"Average Speed (AS):         {avg_speed_per_vehicle:.2f} m/timestep")
print("--------------------------------")

# =================================================================================
# VISUALISATION
# =================================================================================
plt.figure(figsize=(10, 6))

scatter = plt.scatter(
    x=CAV_outflows_cohort_df['cohort_ID'],
    y=CAV_outflows_cohort_df['link_traveltime'],
    s=CAV_outflows_cohort_df['number of vehicles'] * 10,
    c=CAV_outflows_cohort_df['CAV proportion'],
    cmap='viridis',
    alpha=0.7,
    vmin=0, vmax=1, 
    edgecolors='w'
)

# Add the average travel time line to the plot 
avg_line = plt.axhline(
    y=avg_vehicle_traveltime, 
    color='firebrick', 
    linestyle='--', 
    linewidth=2
)

plt.xlabel('cohort ID')
plt.ylabel('number of timesteps')
plt.title('MF-CTM: Link Travel Time (timesteps)\nfor each cohort')
plt.colorbar(scatter, label='cohort CAV proportion')
plt.ylim(30, 75) 
plt.grid(True)

# --- REVISED: Updated labels and specific unit strings ---
metrics_text = (
    f"TD: {total_delay:.1f} veh.timesteps   |   "
    f"AD: {avg_delay_per_vehicle:.2f} timesteps   |   "
    f"AS: {avg_speed_per_vehicle:.2f} m/timestep"
)

# Place text centered underneath the x-axis label
plt.text(
    0.5, -0.18, 
    metrics_text, 
    ha='center', va='top', 
    transform=plt.gca().transAxes, 
    fontsize=11, 
    fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.8)
)

# Build legend components
legend_sizes = [5, 10, 15]
legend_labels = [f'{s} vehicles' for s in legend_sizes]
legend_handles = [
    plt.scatter([], [], s=s * 10, color='gray', alpha=0.6, edgecolors='w') for s in legend_sizes
]

# Append ATT to the legend handles
legend_handles.append(avg_line)
legend_labels.append(f'ATT: {avg_vehicle_traveltime:.1f}')

plt.legend(
    legend_handles,
    legend_labels,
    title='Metrics',
    labelspacing=1.5,
    loc='upper left',
    borderpad=1,
    alignment='left'
)

# Adjust the bottom window spacing so the text box has room to display cleanly
plt.subplots_adjust(bottom=0.18)

plt.show()

#%%Export the data to excel
CTM_matrix_transpose = np.transpose(CTM_matrix)
CTM_matrix_transpose_reverse = CTM_matrix_transpose[::-1]

df1 = pd.DataFrame(CTM_matrix_transpose_reverse)
df2 = pd.DataFrame(CTM_matrix_recap_transpose_reverse)
df3 = pd.DataFrame(CTM_matrix_CAV_recap_transpose_reverse)
df4 = pd.DataFrame(CTM_matrix_NV_recap_transpose_reverse)
df5 = pd.DataFrame(CTM_matrix_recap_perc_transpose_reverse)
df6 = pd.DataFrame(IO_matrix)

df1.to_excel('CTM_matrix_MClassFIFO.xlsx', index = True, header = True)
df2.to_excel('CTM_matrix_recap_MClassFIFO.xlsx', index = True, header = True)
df3.to_excel('CTM_matrix_recap_CAV_MClassFIFO.xlsx', index = True, header = True)
df4.to_excel('CTM_matrix_recap_NV_MClassFIFO.xlsx', index = True, header = True)
df5.to_excel('CTM_matrix_recap_perc_MClassFIFO.xlsx', index = True, header = True)
df6.to_excel('IO_matrix_MClassFIFO.xlsx', index = True, header = True)


#%%Store the IO_matrix for execution later with other model and scenario
IO_matrix_MClassFIFOCTM_random = IO_matrix
