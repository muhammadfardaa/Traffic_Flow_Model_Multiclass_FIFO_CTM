print('-------------------------------Step 2----------------------------------')
#Step 2 - Multiclass CTM Levin and Boyles 2016 - function for CAV proportion calculation

def step_2_veh_proportion(CTM_matrix_current_cell):
    CAV_number = CTM_matrix_current_cell[0][1]
    NV_number = CTM_matrix_current_cell[1][1]
    
    total_vehicle = CAV_number + NV_number
    
    if total_vehicle > 0:
        cell_CAV_proportion = CAV_number/total_vehicle
        cell_NV_proportion = 1 - cell_CAV_proportion
        
    else:
        cell_CAV_proportion = 0
        cell_NV_proportion = 0
        
    return cell_CAV_proportion, cell_NV_proportion