# Title: Multiclass Cell Transmission Model Code - A Tool to Model Traffic Flow Propagation On the Road, Consisting of Connected Autonomous Vehicles (CAV) and Normal Vehicles (NV)

## Programming Language Used: Python and R

## General Description and Goals of the Code
The Multiclass Cell Transmission Model (M-CTM) is a tool for modelling traffic flow propagation, comprising connected autonomous vehicles (CAVs) and normal vehicles (NVs).

In the future, CAVs will likely coexist with NVs on the road; therefore, a model is needed to assess different CAV penetration levels. M-CTM can be an alternative approach for this purpose, as it can examine the impact of CAVs on traffic flow propagation and congestion (measured by queue length, queue dissipation time, travel time, delay, and speed) across different CAV penetration levels (0% to 100%). MF-CTM is particularly relevant for researchers and practitioners in the area of traffic flow theory and modelling.

The codes included in this repository are based on two publications on M-CTM, namely:

1. [Levin and Boyles, 2016](https://www.sciencedirect.com/science/article/pii/S0968090X1500354X)

2. [Qin and Wang, 2019](https://ascelibrary.org/doi/abs/10.1061/JTEPBS.0000238)

I have uploaded the publications above to this repository, in case you want to know more about them. 

## Motivation for writing the code:
I wrote this code during the 1st year of my PhD study. The purpose is to develop my programming skills and learn about how past studies model mixed traffic propagation, consisting of CAV and NV, using the Cell Transmission Model (CTM) approach

## Description of the Approach:
The basics of modelling traffic flow propagation using CTM are described by [Daganzo, 1994](https://www.sciencedirect.com/science/article/abs/pii/0191261594900027)

Imagine there is a straight road in front of our home. To understand traffic propagation on that road, the Basic CTM represents such a road as a link, and discretises the link into several segments called cells. Such a discretised link is then simulated for a number of timesteps. In each timestep, the traffic enters the link and moves from one cell to the next until it finally exits the link. By using such a simulation, one can then see at which points (or cells) in the link a congestion occurs, the fluctuations of the link outflows, the length of traffic queues, how long the queue dissipates, and the travel time of the traffic traversing the link. 

The Basic CTM, however, assumes that the traffic within a link is homogeneous and the road capacity is constant. To model the CAV impact on mixed traffic, which also contains NV, the Basic CTM needs to be modified. The M-CTM is then a modification of the Basic CTM to accommodate the modelling of mixed traffic. As its name implies, the model disaggregates the traffic within it into connected autonomous vehicles (CAV) and normal vehicles (NV). The model also adjusts the road capacity based on the CAV share in the traffic. As CAV can communicate and travel closer together, a higher share of CAV also means higher road capacity. 

## Codes in the Repository:
The main Python code for adjusting the model parameter and running the simulation is the one named: CTM_Simulation_MClassFIFO_DynamicDemand.py

The other codes are functions to support the main code. These include:
1. ctm_step_0_function_FullFIFO.py
2. ctm_step_1_function_FullFIFO.py
3. ctm_step_2_function_FullFIFO.py
4. ctm_step_2_function_FullFIFO.py
5. ctm_step_3a_function_FullFIFO.py
6. ctm_step_3a_function_FullFIFO.py

## Bonus R Codes
This repository also contains the R code for the mixed cell transmission model. I developed this code during the 1st year of my PhD study, for learning purposes before I developed my own model. The code is based on the concept and mathematical formulas by [Qin and Wang, 2019](https://ascelibrary.org/doi/abs/10.1061/JTEPBS.0000238). The R file name is as follows:
- Mixed_CTM_QinWang_Codes.R

## Outputs:
1. Heatmap showing cell occupancy or the number of vehicles within a cell, for each cell at each timestep
2. Heatmap showing CAV proportion within a cell, for each cell at each timestep
3. Line plot showing cumulative traffic inflows to and outflows from the road link model
4. Line plot showing link outflow rate
5. Bubble plot showing link travel time of each traffic packet (cohort) as well as CAV proportion in each cohort
     
## Limitations:
The code is only for simulating a single one-lane link. More codes are needed to extend the model to represent merging, diverging, network, multiple lanes, and other road network components. 
I have been developing the codes for merging, diverging, and network to fulfil the 2nd and 3rd objectives of my PhD study. Let me know if you are interested in those codes :D
