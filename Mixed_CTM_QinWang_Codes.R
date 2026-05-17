#Cell Transmission Model - Mixed Traffic
#PART 1 - MIXED FUNDAMENTAL DIAGRAM CALCULATION --------------------------------
#Developed Based on Yanyan Qin and Hao Wang (2019) - Cell Transmission Model for Mixed Traffic Flow with Connected and Autonomous Vehicles

#Check and set the working directory
getwd()

#import calculation and visualization package
library(ggplot2)
library(dplyr)

#INPUT DATA
#GENERAL INPUT
q_vehhr <- 1500 #input flow in veh/hr
vf_kmhr <- 120 #free flow speed in km/hr 
dt_s <- 3 #timestep in sec
dx_m <- 100 #cell length in m

#General Input conversion
q_vehdt <- q_vehhr * dt_s / 3600 #input flow in veh/timestep
vf_ms <- vf_kmhr * 1000 / 3600 #free flow speed in m per sec

#CTM condition check
if (dx_m >= dt_s * vf_ms){print("condition fulfilled - vehicle will not travel for more than 1 cell length in one timestep")
} else{print("condition not fulfilled - vehicle can travel for more than 1 cell in a timestep - DO NOT PROCEED!!")
  break
}

#ROAD DISRUPTION INPUT
td_s <- 15 * 60 #disruption duration in second
qd_vehdt <- 0 #maximum flow during disruption 
xd_m <- 20 * 1000 #disruption location in meter
start_td_s <- 1000 #disruption starting time in s

#VEHICLE SPECIFIC INPUT
vehicle_type <- c("CACC", "ACC", "human") #vehicle type analyzed
vehicle_time_gap_s <- c(0.6, 1.1, 1.5) #time gap of each vehicle type
vehicle_jam_spacing_m <- c(7, 7, 7) #jam spacing of each vehicle type

#MIXED TRAFFIC SCENARIO DEVELOPMENT
CAV_proportion <- c(0, 0.5, 1)
CAV_proportion <- matrix(unlist(CAV_proportion), nrow = 1, ncol = length(CAV_proportion))

CAV_proportion_colnames <- c()
N <- 1
for (i in CAV_proportion){
  CAV_proportion_colnames <- append(CAV_proportion_colnames, sprintf("scenario_%s", N))
  N <- N + 1
}

colnames(CAV_proportion) <- CAV_proportion_colnames

#Matrix creation for CACC, ACC, and Human proportion 
scenario_proportion <- matrix( , nrow = length(vehicle_type), ncol = length(CAV_proportion))

scenario_proportion_rowname <- c()
for(i in vehicle_type){
  row_type <- sprintf("p_%s", i)
  scenario_proportion_rowname <- append(scenario_proportion_rowname, row_type)
}

scenario_proportion_colname <- c()
for(i in CAV_proportion){
  col_proportion <- sprintf("p_CAV_%s", i)
  scenario_proportion_colname <- append(scenario_proportion_colname, col_proportion)
}

rownames(scenario_proportion) <- scenario_proportion_rowname
colnames(scenario_proportion) <- scenario_proportion_colname

scenario_proportion

#filling in the scenario_proportion matrix
a <- 1
for (i in CAV_proportion){
  p <- c(i^2, i*(1-i), 1 - i)
  scenario_proportion[,a] <- p
  a <- a + 1
}

scenario_proportion

#MIXED FUNDAMENTAL DIAGRAM DEVELOPMENT
#create empty matrix for flow density matrix

mixed_kq_matrix <- matrix(, nrow = 3 , ncol = length(CAV_proportion) * 2)
mixed_kq_matrix_rowname <- c("0", "crit", "jam")
mixed_kq_matrix_colname <- c()

for (i in CAV_proportion){
  col_k <- sprintf("k_p_%s", i)
  col_q <- sprintf("q_p_%s", i)
  mixed_kq_matrix_colname <- append(mixed_kq_matrix_colname, col_k)
  mixed_kq_matrix_colname <- append(mixed_kq_matrix_colname, col_q)
}

rownames(mixed_kq_matrix) <- mixed_kq_matrix_rowname
colnames(mixed_kq_matrix) <- mixed_kq_matrix_colname

mixed_kq_matrix

#fill in the flow density matrix with proper value
b <- 1 #numbering reference for CAV_proportion and scenario_proportion
j <- 1 #numbering reference for mixed_kq_matrix
for (i in CAV_proportion){
  #calculate kc value
  kc_divisor <- 0
  c <- 1
  for (z in scenario_proportion[,b]){
    kc_divisor <- kc_divisor + (z * (vf_ms * vehicle_time_gap_s[c] + vehicle_jam_spacing_m[c]))
    c <- c + 1
  }
  kc <- (1 / kc_divisor) * 1000 #kc value converted from veh/m to veh/km
  
  #calculate kj value
  kj_divisor <- 0
  d <- 1
  for (y in scenario_proportion[,b]){
    kj_divisor <- kj_divisor + y * vehicle_jam_spacing_m[d]
    d <- d + 1
  }
  kj <- (1 / kj_divisor) * 1000 #kj value converted from veh/m to veh/km
  
  k <- c(0, kc, kj) # k value for initial, critical, and jam condition 
  mixed_kq_matrix[,j] <- k #assign the value to the mixed_kq_matrix
  
  #calculate q max value
  qmax_divisor <- 0
  e <- 1
  for (x in scenario_proportion[,b]){
    qmax_divisor <- qmax_divisor + (x * (vf_ms * vehicle_time_gap_s[e] + vehicle_jam_spacing_m[e]))
    e <- e + 1
  }
  qmax <- (vf_ms/qmax_divisor) * 3600
  
  q <- c(0, qmax, 0) #q value for initial, critical, and jam condition 
  mixed_kq_matrix[,j+1] <- q
  
  b <- b + 1
  j <- j + 2
  
}

mixed_kq_matrix

#MIXED FUNDAMENTAL DIAGRAM VISUALIZATION
vis_FD_mixed <- ggplot(as.data.frame(mixed_kq_matrix)) +
  xlab("k (veh/km)") +
  ylab("q (veh/hr)") +
  ggtitle("Mixed Triangular Fundamental Diagram For All Cells") +  
  geom_line(aes(x = mixed_kq_matrix[,1], y=mixed_kq_matrix[,2], colour = "red")) +
  geom_line(aes(x = mixed_kq_matrix[,3], y=mixed_kq_matrix[,4], colour = "blue")) +
  geom_line(aes(x = mixed_kq_matrix[,5], y=mixed_kq_matrix[,6], colour = "black")) +
  scale_color_identity(name = "CAV market penetration", 
                       breaks = c("red", "blue", "black"),
                       labels = c("0", "0.5", "1"),
                       guide = "legend")


vis_FD_mixed

#PART 2 - CTM REQUIRED PARAMETER CALCULATION------------------------------------ 
#Developed Based on Yanyan Qin and Hao Wang (2019) - Cell Transmission Model for Mixed Traffic Flow with Connected and Autonomous Vehicles


#Recall the inputs
CAV_proportion
vehicle_type
vehicle_time_gap_s
vehicle_jam_spacing_m

#Recall developed table in Part 1
mixed_kq_matrix
scenario_proportion

#create qmax and kj table to develop CTM formulation 
mixed_qmaxkj_matrix <- matrix(, nrow = 2, ncol = length(CAV_proportion))
mixed_qmaxkj_matrix_rowname <- c("q_max_vehhr", "kj_vehkm")
mixed_qmaxkj_matrix_colname <- c()

for (i in CAV_proportion){
  p_col <- sprintf("p_%s", i)
  mixed_qmaxkj_matrix_colname <- append(mixed_qmaxkj_matrix_colname, p_col)
}

rownames(mixed_qmaxkj_matrix) <- mixed_qmaxkj_matrix_rowname
colnames(mixed_qmaxkj_matrix) <- mixed_qmaxkj_matrix_colname

for (i in 1:ncol(mixed_qmaxkj_matrix)){
  mixed_qmaxkj_matrix[,i] <- c(mixed_kq_matrix[2,i*2], mixed_kq_matrix[3,i+(i-1)])
}

mixed_summary_matrix <- rbind(mixed_qmaxkj_matrix, scenario_proportion)
mixed_summary_matrix

#create table for CTM parameter (qmax, N, w, and kj)
CTM_param_matrix <- matrix(, nrow = 5, ncol = length(CAV_proportion))
CTM_param_matrix_rowname<- c("qmax_vehdt", "N_vehx", "w_ms", "qmax_veht", "kj_veht")
CTM_param_matrix_colname<- c()

for (i in CAV_proportion){
  CTM_param_matrix_colname <- append(CTM_param_matrix_colname, sprintf("p_%s",i))
}

rownames(CTM_param_matrix) <- CTM_param_matrix_rowname
colnames(CTM_param_matrix) <- CTM_param_matrix_colname

for (i in 1:ncol(CTM_param_matrix)){
  w_numerator <- 0
  w_denominator <- 0
  
  for (z in 3:length(mixed_summary_matrix[,i])){
    w_numerator <- w_numerator + mixed_summary_matrix[z,i] * vehicle_jam_spacing_m [z-2]
    w_denominator <- w_denominator + mixed_summary_matrix[z,i] * vehicle_time_gap_s [z-2]
  } 
  
  w <- -(w_numerator)/w_denominator
  
  CTM_param_matrix[,i] <- c(mixed_summary_matrix[1,i] * dt_s / 3600, mixed_summary_matrix[2,i] * dx_m / 1000, w, mixed_summary_matrix[1,i]/3600, mixed_summary_matrix[2,i]/1000)
}

CTM_param_matrix

#PART 3 - BASIC CTM FUNCTION----------------------------------------------------
#Developed based on the on-going research by Farda

library("writexl") #library to export data frame to excel
library("reshape") #library to melt the matrix so it can be visualized by ggplot2
library("ggplot2") #library to create heatmap

#Recall the required input
#BASIC INPUT AND NORMAL ROAD CONDITION
dt_s #timestep in seconds
dx_m #cell length in meter
CTM_param_matrix #maximum flow and jam density
CAV_proportion #scenario included in the simulation
q_vehdt #input flow in veh/timestep
vf_ms #free flow speed in m per sec

#DISRUPTION INPUT
td_s  #disruption duration in second
qd_vehdt #maximum flow during disruption 
xd_m  #disruption location in meter
start_td_s  #disruption starting time in s

#OTHER INPUT
road_length <- 40000 # in meters
cell_number <- road_length / dx_m
simulation_length <- 5000 # in s
timestep_number <- round(simulation_length / dt_s, 0)
disruption_start_timestep <- ceiling(start_td_s / dt_s)
disruption_end_timestep <- ceiling((start_td_s + td_s) / dt_s)

#CALCULATION PROCESS

options(max.print = 9999999)

#Creating CTM Colnames
CTM_colnames <- c()
for (i in 1:cell_number){
  CTM_colnames <- append(CTM_colnames, sprintf("cell_%s",i))
}

CTM_timesteps <- c(0)
for (i in 1:timestep_number){
  CTM_timesteps <- append(CTM_timesteps, i * dt_s)
}


#FUNCTION TO DEVELOP CELL CAPACITY - NORMAL AND DISRUPTED CONDITION
CTM_cell_capacity <- function(cell_number, CTM_colnames, dx_m, CTM_param_matrix, xd_m, qd_vehdt){
  #CREATING DISTANCE AND CAPACITY MATRIX - input = cell_number, CTM_colnames, dx_m, CTM_param_matrix[x,y]
  dist_and_cap_matrix <- matrix( ,nrow = 3, ncol = cell_number)
  dist_and_cap_rownames <- c("Distance", "Capacity_Normal", "Capacity_Disrupted")
  
  colnames(dist_and_cap_matrix) <- CTM_colnames
  rownames(dist_and_cap_matrix) <- dist_and_cap_rownames
  
  ## distance input
  cell_distance <- c()
  for (i in 1:cell_number){
    cell_distance <- append(cell_distance, i * dx_m)
  }
  
  ## normal capacity input
  cell_normal_capacity <- c()
  for (i in 1:cell_number){
    cell_normal_capacity <- append(cell_normal_capacity,CTM_param_matrix[1,scenario_no])
  }
  
  ## disrupted capacity input
  cell_disruption_location <- round(xd_m/dx_m)
  cell_disrupted_capacity <- cell_normal_capacity
  cell_disrupted_capacity[cell_disruption_location] <- qd_vehdt
  
  dist_and_cap_matrix[1,] <- cell_distance
  dist_and_cap_matrix[2,] <- cell_normal_capacity
  dist_and_cap_matrix[3,] <- cell_disrupted_capacity
  
  return(dist_and_cap_matrix)
}


#FUNCTION TO RUN CTM SIMULATION - VEHICLE OCCUPANCY
CTM_occupancy_simulation <- function(dist_and_cap_matrix, cell_number, CTM_colnames, scenario_no, q_vehdt, CTM_param_matrix, vf_ms){
  
  
  #SIMULATION BY USING CTM - NUMBER OF VEHICLE IN EACH CELL FOR ALL TIMESTEP
  #create empty matrix
  CTM_occupancy_matrix <- matrix(,nrow = 1, ncol = cell_number)
  colnames(CTM_occupancy_matrix) <- CTM_colnames
  rownames(CTM_occupancy_matrix) <- c("timestep_0")
  
  #calculation for timestep 0
  n_timestep_0 <- c()
  for (i in 1:(length(CTM_colnames)-1)){
    n_veh <- 0 + min(q_vehdt, dist_and_cap_matrix[2,i], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0)) - min(0, dist_and_cap_matrix[2,i+1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0))
    
    n_timestep_0 <- append(n_timestep_0, n_veh)
  }
  
  n_veh_last <- 0 + min(q_vehdt, dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0)) - min(0, dist_and_cap_matrix[2,cell_number])
  n_timestep_0 <- append(n_timestep_0, n_veh_last)
  
  CTM_occupancy_matrix[1,] <- n_timestep_0
  
  #calculation for timestep 1 until the start of disruption period
  for (i in 1:(disruption_start_timestep - 1)){
    calc_timestep <- c(0)
    CTM_occupancy_matrix <- rbind(CTM_occupancy_matrix, calc_timestep)
    rownames(CTM_occupancy_matrix)[rownames(CTM_occupancy_matrix) == "calc_timestep"] <- sprintf("timestep_%s",i)
    
    #calculation for cell no 1 at timestep i
    CTM_occupancy_matrix[i+1,1] <- CTM_occupancy_matrix[i,1] + min(q_vehdt, dist_and_cap_matrix[2,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[2,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #calculation for cell no 2 to n-1 at timestep i
    cell_2n <- c()
    for (j in 2:(cell_number - 1)){
      n_cell <- CTM_occupancy_matrix[i,j] + min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[2,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[2,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n <- append(cell_2n, n_cell)
    }
    
    CTM_occupancy_matrix[i+1,2:(cell_number-1)] <- cell_2n
    
    #calculation for the last cell at timestep i
    CTM_occupancy_matrix[i+1,cell_number] <- CTM_occupancy_matrix[i,cell_number] + min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[2,cell_number])
  }
  
  #calculation during the disruption period
  for (i in disruption_start_timestep:(disruption_end_timestep - 1)){
    calc_timestep <- c(0)
    CTM_occupancy_matrix <- rbind(CTM_occupancy_matrix, calc_timestep)
    rownames(CTM_occupancy_matrix)[rownames(CTM_occupancy_matrix) == "calc_timestep"] <- sprintf("timestep_%s",i)
    
    #calculation for cell no 1 at timestep i
    CTM_occupancy_matrix[i+1,1] <- CTM_occupancy_matrix[i,1] + min(q_vehdt, dist_and_cap_matrix[3,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[3,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #calculation for cell no 2 to n-1 at timestep i
    cell_2n <- c()
    for (j in 2:(cell_number - 1)){
      n_cell <- CTM_occupancy_matrix[i,j] + min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[3,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[3,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n <- append(cell_2n, n_cell)
    }
    
    CTM_occupancy_matrix[i+1,2:(cell_number-1)] <- cell_2n
    
    #calculation for the last cell at timestep i
    CTM_occupancy_matrix[i+1,cell_number] <- CTM_occupancy_matrix[i,cell_number] + min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[3,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[3,cell_number])
  }
  
  #calculation after the disruption is removed
  for (i in disruption_end_timestep:timestep_number){
    calc_timestep <- c(0)
    CTM_occupancy_matrix <- rbind(CTM_occupancy_matrix, calc_timestep)
    rownames(CTM_occupancy_matrix)[rownames(CTM_occupancy_matrix) == "calc_timestep"] <- sprintf("timestep_%s",i)
    
    #calculation for cell no 1 at timestep i
    CTM_occupancy_matrix[i+1,1] <- CTM_occupancy_matrix[i,1] + min(q_vehdt, dist_and_cap_matrix[2,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[2,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #calculation for cell no 2 to n-1 at timestep i
    cell_2n <- c()
    for (j in 2:(cell_number - 1)){
      n_cell <- CTM_occupancy_matrix[i,j] + min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[2,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[2,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n <- append(cell_2n, n_cell)
    }
    
    CTM_occupancy_matrix[i+1,2:(cell_number-1)] <- cell_2n
    
    #calculation for the last cell at timestep i
    CTM_occupancy_matrix[i+1,cell_number] <- CTM_occupancy_matrix[i,cell_number] + min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[2,cell_number])
  }
  
  return(CTM_occupancy_matrix)
}


#FUNCTION TO RUN CTM SIMULATION - SPEED
CTM_speed_simulation <- function(CTM_occupancy_matrix, cell_number, CTM_colnames,dx_m, vf_ms, CTM_param_matrix, scenario_no, timestep_number){
  CTM_speed_matrix <- matrix(,nrow = 1, ncol = cell_number)
  colnames(CTM_speed_matrix) <- CTM_colnames
  rownames(CTM_speed_matrix) <- c("timestep_0")
  
  #calculation for timestep 0
  v_timestep_0 <- c()
  for (i in 1:cell_number){
    if(CTM_occupancy_matrix[1,i]/dx_m > 0){
      v_timestep <- min(vf_ms, CTM_param_matrix[4,scenario_no]/(CTM_occupancy_matrix[1,i]/dx_m),-CTM_param_matrix[3,scenario_no]*(CTM_param_matrix[5,scenario_no] - (CTM_occupancy_matrix[1,i]/dx_m))/(CTM_occupancy_matrix[1,i]/dx_m))
      v_timestep_0 <- append(v_timestep_0, v_timestep)
    } else {
      v_timestep_0 <- vf_ms
    }
  }
  
  CTM_speed_matrix[1,] <- v_timestep_0
  
  #calculation for timestep 1 until the end of simulation 
  speed_calc_timestep <- c(0)
  for (i in 1:timestep_number){
    CTM_speed_matrix <- rbind(CTM_speed_matrix, speed_calc_timestep)
    rownames(CTM_speed_matrix)[rownames(CTM_speed_matrix) == "speed_calc_timestep"] <- sprintf("timestep_%s",i)
    
    v_timestep_n <- c()
    for (j in 1: cell_number){
      if(CTM_occupancy_matrix[i+1,j]/dx_m > 0){
        v_timestep <- min(vf_ms, CTM_param_matrix[4,scenario_no]/(CTM_occupancy_matrix[i+1,j]/dx_m),-CTM_param_matrix[3,scenario_no]*(CTM_param_matrix[5,scenario_no] - (CTM_occupancy_matrix[i+1,j]/dx_m))/(CTM_occupancy_matrix[i+1,j]/dx_m))
        v_timestep_n <- append(v_timestep_n, v_timestep)
      } else {
        v_timestep_n <- append(v_timestep_n, vf_ms)
      }
    }
    
    CTM_speed_matrix[i+1,] <- v_timestep_n
  }
  
  return(CTM_speed_matrix)
}


#FUNCTION TO RUN CTM SIMULATION - VISUALIZATION
#can be used to visualize CTM_occupancy_matrix or CTM_speed matrix
CTM_occupancy_visualization <- function(CTM_occupancy_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no){
  rownames(CTM_occupancy_matrix) <- c((0:timestep_number)*dt_s)
  colnames(CTM_occupancy_matrix) <- c((1:cell_number)*dx_m)
  
  CTM_occupancy_matrix_melt <- melt(CTM_occupancy_matrix)
  colnames(CTM_occupancy_matrix_melt) <- c("time_s", "distance_m", "number_of_vehicles")
  scenario_name <- sprintf("Scenario %s", scenario_no)
  
  veh_number_plot <- ggplot(CTM_occupancy_matrix_melt, aes(x = time_s, y = distance_m, fill = number_of_vehicles)) +
    geom_tile() + 
    ggtitle(sprintf("Vehicle Distribution Along Road Segments (Cells) - %s", scenario_name)) + 
    scale_fill_gradient(low = "white", high = "blue") +
    labs(x = "time(s)",
         y = "distance(m)")
  
  return(veh_number_plot)
}

CTM_speed_visualization <- function(CTM_speed_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no){
  rownames(CTM_speed_matrix) <- c((0:timestep_number)*dt_s)
  colnames(CTM_speed_matrix) <- c((1:cell_number)*dx_m)
  
  CTM_speed_matrix_melt <- melt(CTM_speed_matrix)
  colnames(CTM_speed_matrix_melt) <- c("time_s", "distance_m", "vehicle_speed")
  scenario_name <- sprintf("Scenario %s", scenario_no)
  
  veh_speed_plot <- ggplot(CTM_speed_matrix_melt, aes(x = time_s, y = distance_m, fill = vehicle_speed)) +
    geom_tile() +
    ggtitle(sprintf("Speed Distribution Along Road Segments (Cells) - %s ", scenario_name)) +
    scale_fill_gradient(low = "red", high = "white") +
    labs(x = "time(s)",
         y = "distance(m)")
  
  return(veh_speed_plot)
}

#PART 4 - VEHICLE DIFFERENTIATION INTO CAV AND NV-------------------------------
#Developed based on the on-going research by Farda

#Recall the required input
CTM_param_matrix
CAV_proportion

#Function to split the CTM Matrix into CAV and NV-------------------------------
CTM_matrix_CAV_NV <- function(CTM_occupancy_matrix, cell_number, CTM_colnames, CAV_proportion, scenario_no, q_vehdt, dist_and_cap_matrix, CTM_param_matrix, vf_ms, disruption_start_timestep, disruption_end_timestep){
  
  #Develop 3 matrices with rows created simultaneously
  #matrix 1 - matrix for CAV occupancy
  #matrix 2 - matrix for NV occupancy
  #matrix 3 - matrix for CAV proportion 
  
  #Create matrix for CAV
  CTM_matrix_CAV <- matrix(,nrow = 1, ncol = cell_number)
  colnames(CTM_matrix_CAV) <- CTM_colnames
  rownames(CTM_matrix_CAV) <- c("timestep_0")
  
  #Create matrix for NV
  CTM_matrix_NV <- matrix(,nrow = 1, ncol = cell_number)
  colnames(CTM_matrix_NV) <- CTM_colnames
  rownames(CTM_matrix_NV) <- c("timestep_0")
  
  #Create matrix for CAV proportion 
  CTM_matrix_CAV_proportion <- matrix(,nrow = 1, ncol = cell_number)
  colnames(CTM_matrix_CAV_proportion) <- CTM_colnames
  rownames(CTM_matrix_CAV_proportion) <- c("timestep_0")
  
  #Calculation for timestep 0-----------------------------------------------------
  #Initialize the rows for CAV and NV
  n_timestep_0_CAV <- c()
  n_timestep_0_NV <- c()
  
  for (i in 1:(cell_number-1)){
    # Calculation (filling in the rows) for the 1st and the n-1 CAV cell
    n_veh_CAV <- 0 + CAV_proportion[1, scenario_no] * min(q_vehdt, dist_and_cap_matrix[2,i], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0)) - CAV_proportion[1, scenario_no] * min(0, dist_and_cap_matrix[2, i+1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0))
    
    n_timestep_0_CAV <- append(n_timestep_0_CAV, n_veh_CAV)
    
    # Calculation (filling in the rows) for the 1st and the n-1 NV cell
    n_veh_NV <- 0 + (1 - CAV_proportion[1, scenario_no]) * min(q_vehdt, dist_and_cap_matrix[2,i], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0)) - (1 - CAV_proportion[1, scenario_no]) * min(0, dist_and_cap_matrix[2, i+1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0))
    
    n_timestep_0_NV <- append(n_timestep_0_NV, n_veh_NV)
    
  }
  
  # Calculation (filling in the rows) for the n (last) CAV cell
  n_veh_last_CAV <- 0 + CAV_proportion[1, scenario_no] * min(q_vehdt, dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0)) - CAV_proportion[1, scenario_no] * min(0, dist_and_cap_matrix[2,cell_number])
  n_timestep_0_CAV <- append(n_timestep_0_CAV, n_veh_last_CAV)
  
  # Calculation (filling in the rows) for the n (last) NV cell
  n_veh_last_NV <- 0 + (1 - CAV_proportion[1, scenario_no]) * min(q_vehdt, dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - 0)) - (1 - CAV_proportion[1, scenario_no]) * min(0, dist_and_cap_matrix[2,cell_number])
  n_timestep_0_NV <- append(n_timestep_0_NV, n_veh_last_NV)
  
  #Append the calculation result to CAV and NV matrix
  CTM_matrix_CAV[1,] <- n_timestep_0_CAV
  CTM_matrix_NV[1,] <- n_timestep_0_NV
  
  #Calculation for CAV proportion matrix
  CTM_matrix_CAV_proportion[1,] <- CTM_matrix_CAV[1,] / (CTM_matrix_CAV[1,] + CTM_matrix_NV[1,])
  
  
  #Calculation for timestep 1 until the start of disruption period----------------
  
  for (i in 1:(disruption_start_timestep - 1)){
    #initialize the rows for timestep 1 and timestep before the disruption occurs
    calc_timestep <- c(0)
    CTM_matrix_CAV <- rbind(CTM_matrix_CAV, calc_timestep)
    CTM_matrix_NV <- rbind(CTM_matrix_NV, calc_timestep)
    CTM_matrix_CAV_proportion <- rbind(CTM_matrix_CAV_proportion, calc_timestep)
    
    rownames(CTM_matrix_CAV)[rownames(CTM_matrix_CAV) == "calc_timestep"] <- sprintf("timestep_%s", i)
    rownames(CTM_matrix_NV)[rownames(CTM_matrix_NV) == "calc_timestep"] <- sprintf("timestep_%s", i)
    rownames(CTM_matrix_CAV_proportion)[rownames(CTM_matrix_CAV_proportion) == "calc_timestep"] <- sprintf("timestep_%s", i)
    
    #fill in the rows with number of vehicles (for CAV and NV matrix) as well as the proportion (for CAV proportion matrix)
    #calculation for cell no 1 at timestep i 
    #Calculation for CAV
    CTM_matrix_CAV[i + 1, 1] <- CTM_matrix_CAV[i,1] + CAV_proportion[1, scenario_no] * min(q_vehdt, dist_and_cap_matrix[2,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - CTM_matrix_CAV_proportion[i, 1] * min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[2,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #Calculation for NV
    CTM_matrix_NV[i + 1, 1] <- CTM_matrix_NV[i,1] + (1 - CAV_proportion[1, scenario_no]) * min(q_vehdt, dist_and_cap_matrix[2,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - (1 - CTM_matrix_CAV_proportion[i, 1]) * min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[2,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #Calculation for CAV Proportion 
    CTM_matrix_CAV_proportion[i + 1, 1] <- CTM_matrix_CAV[i + 1, 1]/(CTM_matrix_CAV[i + 1, 1] +  CTM_matrix_NV[i + 1, 1])
    CTM_matrix_CAV_proportion[i + 1, 1] <- replace(CTM_matrix_CAV_proportion[i + 1, 1], is.na(CTM_matrix_CAV_proportion[i + 1, 1]), 0)
    
    #calculation for cell no 2 to n-1 at timestep i
    
    cell_2n_CAV <- c()
    cell_2n_NV <- c()
    for (j in 2: (cell_number - 1)){
      
      #Calculation for CAV
      n_cell_CAV <- CTM_matrix_CAV[i,j] + CTM_matrix_CAV_proportion[i, j-1] * min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[2,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - CTM_matrix_CAV_proportion[i, j] * min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[2,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n_CAV <- append(cell_2n_CAV, n_cell_CAV)
      
      #Calculation for NV
      n_cell_NV <- CTM_matrix_NV[i,j] + (1 - CTM_matrix_CAV_proportion[i, j-1]) * min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[2,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - (1 - CTM_matrix_CAV_proportion[i, j]) * min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[2,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n_NV <- append(cell_2n_NV, n_cell_NV)
      
    }
    
    CTM_matrix_CAV[i+1,2:(cell_number-1)] <- cell_2n_CAV
    CTM_matrix_NV[i+1,2:(cell_number-1)] <- cell_2n_NV
    
    #Calculation for CAV proportion 
    CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)] <- CTM_matrix_CAV[i+1,2:(cell_number-1)]/(CTM_matrix_CAV[i+1,2:(cell_number-1)] + CTM_matrix_NV[i+1,2:(cell_number-1)])
    CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)] <- replace(CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)], is.na(CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)]), 0)
    
    #calculation for the last cell at timestep i
    #Calculation for CAV
    CTM_matrix_CAV[i+1,cell_number] <- CTM_matrix_CAV[i,cell_number] + CTM_matrix_CAV_proportion[i, cell_number-1] * min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - CTM_matrix_CAV_proportion[i, cell_number] * min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[2,cell_number])
    
    #Calculation for NV
    CTM_matrix_NV[i+1,cell_number] <- CTM_matrix_NV[i,cell_number] + (1 - CTM_matrix_CAV_proportion[i, cell_number-1]) * min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - (1 - CTM_matrix_CAV_proportion[i, cell_number]) * min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[2,cell_number])
    
    #Calculation for CAV proportion 
    CTM_matrix_CAV_proportion[i+1,cell_number] <- CTM_matrix_CAV[i+1,cell_number] / (CTM_matrix_CAV[i+1,cell_number] + CTM_matrix_NV[i+1,cell_number])
    CTM_matrix_CAV_proportion[i+1,cell_number] <- replace(CTM_matrix_CAV_proportion[i+1,cell_number], is.na(CTM_matrix_CAV_proportion[i+1,cell_number]), 0)
  }
  
  
  #Calculation during the disruption period--------------------------------------
  
  for (i in disruption_start_timestep:(disruption_end_timestep - 1)){
    #initialize the rows for timestep 1 and timestep before the disruption occurs
    calc_timestep <- c(0)
    CTM_matrix_CAV <- rbind(CTM_matrix_CAV, calc_timestep)
    CTM_matrix_NV <- rbind(CTM_matrix_NV, calc_timestep)
    CTM_matrix_CAV_proportion <- rbind(CTM_matrix_CAV_proportion, calc_timestep)
    
    rownames(CTM_matrix_CAV)[rownames(CTM_matrix_CAV) == "calc_timestep"] <- sprintf("timestep_%s", i)
    rownames(CTM_matrix_NV)[rownames(CTM_matrix_NV) == "calc_timestep"] <- sprintf("timestep_%s", i)
    rownames(CTM_matrix_CAV_proportion)[rownames(CTM_matrix_CAV_proportion) == "calc_timestep"] <- sprintf("timestep_%s", i)
    
    #fill in the rows with number of vehicles (for CAV and NV matrix) as well as the proportion (for CAV proportion matrix)
    #calculation for cell no 1 at timestep i 
    #Calculation for CAV
    CTM_matrix_CAV[i + 1, 1] <- CTM_matrix_CAV[i,1] + CAV_proportion[1, scenario_no] * min(q_vehdt, dist_and_cap_matrix[3,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - CTM_matrix_CAV_proportion[i, 1] * min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[3,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #Calculation for NV
    CTM_matrix_NV[i + 1, 1] <- CTM_matrix_NV[i,1] + (1 - CAV_proportion[1, scenario_no]) * min(q_vehdt, dist_and_cap_matrix[3,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - (1 - CTM_matrix_CAV_proportion[i, 1]) * min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[3,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #Calculation for CAV Proportion 
    CTM_matrix_CAV_proportion[i + 1, 1] <- CTM_matrix_CAV[i + 1, 1]/(CTM_matrix_CAV[i + 1, 1] +  CTM_matrix_NV[i + 1, 1])
    CTM_matrix_CAV_proportion[i + 1, 1] <- replace(CTM_matrix_CAV_proportion[i + 1, 1], is.na(CTM_matrix_CAV_proportion[i + 1, 1]), 0)
    
    #calculation for cell no 2 to n-1 at timestep i
    
    cell_2n_CAV <- c()
    cell_2n_NV <- c()
    for (j in 2: (cell_number - 1)){
      
      #Calculation for CAV
      n_cell_CAV <- CTM_matrix_CAV[i,j] + CTM_matrix_CAV_proportion[i, j-1] * min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[3,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - CTM_matrix_CAV_proportion[i, j] * min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[3,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n_CAV <- append(cell_2n_CAV, n_cell_CAV)
      
      #Calculation for NV
      n_cell_NV <- CTM_matrix_NV[i,j] + (1 - CTM_matrix_CAV_proportion[i, j-1]) * min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[3,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - (1 - CTM_matrix_CAV_proportion[i, j]) * min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[3,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n_NV <- append(cell_2n_NV, n_cell_NV)
      
    }
    
    CTM_matrix_CAV[i+1,2:(cell_number-1)] <- cell_2n_CAV
    CTM_matrix_NV[i+1,2:(cell_number-1)] <- cell_2n_NV
    
    #Calculation for CAV proportion 
    CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)] <- CTM_matrix_CAV[i+1,2:(cell_number-1)]/(CTM_matrix_CAV[i+1,2:(cell_number-1)] + CTM_matrix_NV[i+1,2:(cell_number-1)])
    CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)] <- replace(CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)], is.na(CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)]), 0)
    
    
    #calculation for the last cell at timestep i
    #Calculation for CAV
    CTM_matrix_CAV[i+1,cell_number] <- CTM_matrix_CAV[i,cell_number] + CTM_matrix_CAV_proportion[i, cell_number-1] * min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[3,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - CTM_matrix_CAV_proportion[i, cell_number] * min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[3,cell_number])
    
    #Calculation for NV
    CTM_matrix_NV[i+1,cell_number] <- CTM_matrix_NV[i,cell_number] + (1 - CTM_matrix_CAV_proportion[i, cell_number-1]) * min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[3,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - (1 - CTM_matrix_CAV_proportion[i, cell_number]) * min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[3,cell_number])
    
    #Calculation for CAV proportion 
    CTM_matrix_CAV_proportion[i+1,cell_number] <- CTM_matrix_CAV[i+1,cell_number] / (CTM_matrix_CAV[i+1,cell_number] + CTM_matrix_NV[i+1,cell_number])
    CTM_matrix_CAV_proportion[i+1,cell_number] <- replace(CTM_matrix_CAV_proportion[i+1,cell_number], is.na(CTM_matrix_CAV_proportion[i+1,cell_number]), 0)
    
  }
  
  #Calculation after the disruption is removed------------------------------------
  for (i in disruption_end_timestep:timestep_number){
    #initialize the rows for timestep 1 and timestep before the disruption occurs
    calc_timestep <- c(0)
    CTM_matrix_CAV <- rbind(CTM_matrix_CAV, calc_timestep)
    CTM_matrix_NV <- rbind(CTM_matrix_NV, calc_timestep)
    CTM_matrix_CAV_proportion <- rbind(CTM_matrix_CAV_proportion, calc_timestep)
    
    rownames(CTM_matrix_CAV)[rownames(CTM_matrix_CAV) == "calc_timestep"] <- sprintf("timestep_%s", i)
    rownames(CTM_matrix_NV)[rownames(CTM_matrix_NV) == "calc_timestep"] <- sprintf("timestep_%s", i)
    rownames(CTM_matrix_CAV_proportion)[rownames(CTM_matrix_CAV_proportion) == "calc_timestep"] <- sprintf("timestep_%s", i)
    
    #fill in the rows with number of vehicles (for CAV and NV matrix) as well as the proportion (for CAV proportion matrix)
    #calculation for cell no 1 at timestep i 
    #Calculation for CAV
    CTM_matrix_CAV[i + 1, 1] <- CTM_matrix_CAV[i,1] + CAV_proportion[1, scenario_no] * min(q_vehdt, dist_and_cap_matrix[2,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - CTM_matrix_CAV_proportion[i, 1] * min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[2,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #Calculation for NV
    CTM_matrix_NV[i + 1, 1] <- CTM_matrix_NV[i,1] + (1 - CAV_proportion[1, scenario_no]) * min(q_vehdt, dist_and_cap_matrix[2,1], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,1])) - (1 - CTM_matrix_CAV_proportion[i, 1]) * min(CTM_occupancy_matrix[i,1], dist_and_cap_matrix[2,2],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,2]))
    
    #Calculation for CAV Proportion 
    CTM_matrix_CAV_proportion[i + 1, 1] <- CTM_matrix_CAV[i + 1, 1]/(CTM_matrix_CAV[i + 1, 1] +  CTM_matrix_NV[i + 1, 1])
    CTM_matrix_CAV_proportion[i + 1, 1] <- replace(CTM_matrix_CAV_proportion[i + 1, 1], is.na(CTM_matrix_CAV_proportion[i + 1, 1]), 0)
    
    #calculation for cell no 2 to n-1 at timestep i
    
    cell_2n_CAV <- c()
    cell_2n_NV <- c()
    for (j in 2: (cell_number - 1)){
      
      #Calculation for CAV
      n_cell_CAV <- CTM_matrix_CAV[i,j] + CTM_matrix_CAV_proportion[i, j-1] * min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[2,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - CTM_matrix_CAV_proportion[i, j] * min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[2,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n_CAV <- append(cell_2n_CAV, n_cell_CAV)
      
      #Calculation for NV
      n_cell_NV <- CTM_matrix_NV[i,j] + (1 - CTM_matrix_CAV_proportion[i, j-1]) * min(CTM_occupancy_matrix[i,j-1], dist_and_cap_matrix[2,j], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j])) - (1 - CTM_matrix_CAV_proportion[i, j]) * min(CTM_occupancy_matrix[i,j], dist_and_cap_matrix[2,j+1],-(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,j+1]))
      cell_2n_NV <- append(cell_2n_NV, n_cell_NV)
      
    }
    
    CTM_matrix_CAV[i+1,2:(cell_number-1)] <- cell_2n_CAV
    CTM_matrix_NV[i+1,2:(cell_number-1)] <- cell_2n_NV
    
    #Calculation for CAV proportion 
    CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)] <- CTM_matrix_CAV[i+1,2:(cell_number-1)]/(CTM_matrix_CAV[i+1,2:(cell_number-1)] + CTM_matrix_NV[i+1,2:(cell_number-1)])
    CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)] <- replace(CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)], is.na(CTM_matrix_CAV_proportion[i+1,2:(cell_number-1)]), 0)
    
    #calculation for the last cell at timestep i
    #Calculation for CAV
    CTM_matrix_CAV[i+1,cell_number] <- CTM_matrix_CAV[i,cell_number] + CTM_matrix_CAV_proportion[i, cell_number-1] * min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - CTM_matrix_CAV_proportion[i, cell_number] * min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[2,cell_number])
    
    #Calculation for NV
    CTM_matrix_NV[i+1,cell_number] <- CTM_matrix_NV[i,cell_number] + (1 - CTM_matrix_CAV_proportion[i, cell_number-1]) * min(CTM_occupancy_matrix[i,cell_number-1], dist_and_cap_matrix[2,cell_number], -(CTM_param_matrix[3,scenario_no]/vf_ms) * (CTM_param_matrix[2,scenario_no] - CTM_occupancy_matrix[i,cell_number])) - (1 - CTM_matrix_CAV_proportion[i, cell_number]) * min(CTM_occupancy_matrix[i,cell_number], dist_and_cap_matrix[2,cell_number])
    
    #Calculation for CAV proportion 
    CTM_matrix_CAV_proportion[i+1,cell_number] <- CTM_matrix_CAV[i+1,cell_number] / (CTM_matrix_CAV[i+1,cell_number] + CTM_matrix_NV[i+1,cell_number])
    CTM_matrix_CAV_proportion[i+1,cell_number] <- replace(CTM_matrix_CAV_proportion[i+1,cell_number], is.na(CTM_matrix_CAV_proportion[i+1,cell_number]), 0)
  }
  
  this_function_output <- list(CTM_matrix_CAV, CTM_matrix_NV, CTM_matrix_CAV_proportion)
  return(this_function_output)
  
}

#FUNCTION TO RUN CTM SIMULATION - VISUALIZATION of CAV and NV------------------
#can be used to visualize CTM_occupancy_matrix or CTM_speed matrix
#Function to Visualize CAV
CTM_occupancy_visualization_CAV <- function(CTM_occupancy_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no){
  rownames(CTM_occupancy_matrix) <- c((0:timestep_number)*dt_s)
  colnames(CTM_occupancy_matrix) <- c((1:cell_number)*dx_m)
  
  CTM_occupancy_matrix_melt <- melt(CTM_occupancy_matrix)
  colnames(CTM_occupancy_matrix_melt) <- c("time_s", "distance_m", "number_of_vehicles")
  scenario_name <- sprintf("Scenario %s", scenario_no)
  
  veh_number_plot <- ggplot(CTM_occupancy_matrix_melt, aes(x = time_s, y = distance_m, fill = number_of_vehicles)) +
    geom_tile() + 
    ggtitle(sprintf("CAV Distribution Along Road Segments (Cells) - %s", scenario_name)) + 
    scale_fill_gradient(low = "white", high = "green") +
    labs(x = "time(s)",
         y = "distance(m)")
  
  return(veh_number_plot)
}

#Function to Visualize NV
CTM_occupancy_visualization_NV <- function(CTM_occupancy_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no){
  rownames(CTM_occupancy_matrix) <- c((0:timestep_number)*dt_s)
  colnames(CTM_occupancy_matrix) <- c((1:cell_number)*dx_m)
  
  CTM_occupancy_matrix_melt <- melt(CTM_occupancy_matrix)
  colnames(CTM_occupancy_matrix_melt) <- c("time_s", "distance_m", "number_of_vehicles")
  scenario_name <- sprintf("Scenario %s", scenario_no)
  
  veh_number_plot <- ggplot(CTM_occupancy_matrix_melt, aes(x = time_s, y = distance_m, fill = number_of_vehicles)) +
    geom_tile() + 
    ggtitle(sprintf("NV Distribution Along Road Segments (Cells) - %s", scenario_name)) + 
    scale_fill_gradient(low = "white", high = "yellow") +
    labs(x = "time(s)",
         y = "distance(m)")
  
  return(veh_number_plot)
}


#PART 5 - BASIC CTM VISUALIZATION-----------------------------------------------

library("ggplot2") #library to create heatmap
library("zeallot") #library to unpack the result from a function

#-------------------------------------------------------------------------------
scenario_no <- 1
#RUNNING FOR THE WHOLE CTM MATRIX
#THE 3 FUNCTIONS BELOW MUST BE SEQUENTIALLY RUN
cell_capacity_matrix <- CTM_cell_capacity(cell_number, CTM_colnames, dx_m, CTM_param_matrix, xd_m, qd_vehdt)
CTM_occupancy_matrix <- CTM_occupancy_simulation(cell_capacity_matrix, cell_number, CTM_colnames, scenario_no, q_vehdt, CTM_param_matrix, vf_ms)
CTM_speed_matrix <- CTM_speed_simulation(CTM_occupancy_matrix, cell_number, CTM_colnames,dx_m, vf_ms, CTM_param_matrix, scenario_no, timestep_number)

#THE 2 FUNCTIONS BELOW CAN BE RUN AFTER RUNNING THE 3 FUNCTIONS ABOVE
CTM_occupancy_visualization(CTM_occupancy_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no)
CTM_speed_visualization(CTM_speed_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no)

#RUNNING FOR CAV AND NV CTM MATRIX
c(CTM_matrix_CAV_output, CTM_matrix_NV_output, CTM_matrix_CAV_proportion_output) %<-% CTM_matrix_CAV_NV(CTM_occupancy_matrix, cell_number, CTM_colnames, CAV_proportion, scenario_no, q_vehdt, cell_capacity_matrix, CTM_param_matrix, vf_ms, disruption_start_timestep, disruption_end_timestep)

#VISUALIZE THE CAV AND NV MATRIX
CTM_occupancy_visualization_CAV(CTM_matrix_CAV_output, timestep_number, cell_number, dt_s, dx_m, scenario_no)
CTM_occupancy_visualization_NV(CTM_matrix_NV_output, timestep_number, cell_number, dt_s, dx_m, scenario_no)

#-------------------------------------------------------------------------------
scenario_no <- 2
#Can copy and paste the CTM calculation and visualisation function here
#THE 3 FUNCTIONS BELOW MUST BE SEQUENTIALLY RUN
cell_capacity_matrix <- CTM_cell_capacity(cell_number, CTM_colnames, dx_m, CTM_param_matrix, xd_m, qd_vehdt)
CTM_occupancy_matrix <- CTM_occupancy_simulation(cell_capacity_matrix, cell_number, CTM_colnames, scenario_no, q_vehdt, CTM_param_matrix, vf_ms)
CTM_speed_matrix <- CTM_speed_simulation(CTM_occupancy_matrix, cell_number, CTM_colnames,dx_m, vf_ms, CTM_param_matrix, scenario_no, timestep_number)

#THE 2 FUNCTIONS BELOW CAN BE RUN AFTER RUNNING THE 3 FUNCTIONS ABOVE
CTM_occupancy_visualization(CTM_occupancy_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no)
CTM_speed_visualization(CTM_speed_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no)

#RUNNING FOR CAV AND NV CTM MATRIX
c(CTM_matrix_CAV_output, CTM_matrix_NV_output, CTM_matrix_CAV_proportion_output) %<-% CTM_matrix_CAV_NV(CTM_occupancy_matrix, cell_number, CTM_colnames, CAV_proportion, scenario_no, q_vehdt, cell_capacity_matrix, CTM_param_matrix, vf_ms, disruption_start_timestep, disruption_end_timestep)

#VISUALIZE THE CAV AND NV MATRIX
CTM_occupancy_visualization_CAV(CTM_matrix_CAV_output, timestep_number, cell_number, dt_s, dx_m, scenario_no)
CTM_occupancy_visualization_NV(CTM_matrix_NV_output, timestep_number, cell_number, dt_s, dx_m, scenario_no)

#-------------------------------------------------------------------------------
scenario_no <- 3
#Can copy and paste the CTM calculation and visualisation function here
#THE 3 FUNCTIONS BELOW MUST BE SEQUENTIALLY RUN
cell_capacity_matrix <- CTM_cell_capacity(cell_number, CTM_colnames, dx_m, CTM_param_matrix, xd_m, qd_vehdt)
CTM_occupancy_matrix <- CTM_occupancy_simulation(cell_capacity_matrix, cell_number, CTM_colnames, scenario_no, q_vehdt, CTM_param_matrix, vf_ms)
CTM_speed_matrix <- CTM_speed_simulation(CTM_occupancy_matrix, cell_number, CTM_colnames,dx_m, vf_ms, CTM_param_matrix, scenario_no, timestep_number)

#THE 2 FUNCTIONS BELOW CAN BE RUN AFTER RUNNING THE 3 FUNCTIONS ABOVE
CTM_occupancy_visualization(CTM_occupancy_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no)
CTM_speed_visualization(CTM_speed_matrix, timestep_number, cell_number, dt_s, dx_m, scenario_no)

#RUNNING FOR CAV AND NV CTM MATRIX
c(CTM_matrix_CAV_output, CTM_matrix_NV_output, CTM_matrix_CAV_proportion_output) %<-% CTM_matrix_CAV_NV(CTM_occupancy_matrix, cell_number, CTM_colnames, CAV_proportion, scenario_no, q_vehdt, cell_capacity_matrix, CTM_param_matrix, vf_ms, disruption_start_timestep, disruption_end_timestep)

#VISUALIZE THE CAV AND NV MATRIX
CTM_occupancy_visualization_CAV(CTM_matrix_CAV_output, timestep_number, cell_number, dt_s, dx_m, scenario_no)
CTM_occupancy_visualization_NV(CTM_matrix_NV_output, timestep_number, cell_number, dt_s, dx_m, scenario_no)


