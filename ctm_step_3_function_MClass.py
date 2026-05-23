print('-------------------------------Step 3----------------------------------')
#Step 3 - Multiclass CTM Levin and Boyles 2016 - function for flow conservation formulation

def step_3_flow_conserv(CTM_matrix_current_cell, in_flowrate_CAV, in_flowrate_NV, out_flowrate_CAV, out_flowrate_NV):
    CTM_cell_next_timestep_CAV = CTM_matrix_current_cell[0][1] + in_flowrate_CAV - out_flowrate_CAV
    CTM_cell_next_timestep_NV = CTM_matrix_current_cell[1][1] + in_flowrate_NV - out_flowrate_NV
    
    return CTM_cell_next_timestep_CAV, CTM_cell_next_timestep_NV