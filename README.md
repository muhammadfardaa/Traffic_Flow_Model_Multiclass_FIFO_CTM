# Title: Multiclass Cell Transmission Model Code - A Tool to Model Traffic Flow Propagation On the Road, Consisting of Connected Autonomous Vehicles (CAV) and Normal Vehicles (NV)

## Programming Language Used: Python and R

## General Description and Goals of the Code
The Multiclass Cell Transmission Model (M-CTM) is a tool for modelling traffic flow propagation, consisting of connected autonomous vehicles (CAVs) and normal vehicles (NVs).

In the future, CAVs will likely coexist with NVs on the road. Therefore, we need models to represent traffic flow propagation for a range of CAV penetration levels. M-CTM can be an alternative approach for this purpose, as it can examine the impact of CAVs on traffic flow propagation and congestion (measured by queue length, queue dissipation time, travel time, delay, and speed) across different CAV penetration levels (0% to 100%). MF-CTM is particularly relevant for researchers and practitioners in the area of traffic flow theory, modelling, and management.

The codes included in this repository are based on mathematical formulations in two academic publications, namely:

1. [Levin and Boyles, 2016](https://www.sciencedirect.com/science/article/pii/S0968090X1500354X)

2. [Qin and Wang, 2019](https://ascelibrary.org/doi/abs/10.1061/JTEPBS.0000238)

I have uploaded the publications above to this repository, in case you want to know more about them. 

## Motivation for writing the code:
I wrote this code during the 1st year of my PhD study. The purpose is to develop my programming skills and learn about how past studies model mixed traffic propagation, consisting of CAV and NV, using the Cell Transmission Model (CTM) approach

## Description of the Approach:
The basics of modelling traffic flow propagation using CTM are described by [Daganzo, 1994](https://www.sciencedirect.com/science/article/abs/pii/0191261594900027)

Imagine there is a straight road on a motorway. To understand traffic propagation on that road, the Basic CTM represents such a road as a link, and discretises the link into several segments called cells. Such a discretised link is then simulated for a number of timesteps. In each timestep, the traffic enters the link and moves from one cell to the next until it finally exits the link. By using such a simulation, one can then see where traffic congestion occurs, the fluctuations of the link outflows, the length of traffic queues, how long the queue dissipates, and the travel time of the traffic traversing the link. 

The Basic CTM, however, assumes that the traffic within a link is homogeneous and the road capacity is constant. To model the CAV impact on mixed traffic, which also contains NV, the Basic CTM needs to be modified. The M-CTM is then a modification of the Basic CTM to accommodate the modelling of mixed traffic. As its name implies, the model disaggregates the traffic within it into connected autonomous vehicles (CAV) and normal vehicles (NV). The model also adjusts the road capacity based on the CAV share in the mixed traffic. As CAV can communicate and travel closer together, a higher share of CAV also means higher road capacity. 

## Codes in the Repository:
The codes for each M-CTM model are listed below

### Model 1 (by Levin and Boyles, 2016)
Programming language: Python

Main simulation file:
1. CTM_Simulation_MClass_DynamicDemand.py 

Supporting functions:
1. ctm_step_0_function_MClass.py
2. ctm_step_1_function_MClass.py
3. ctm_step_2_function_MClass.py
4. ctm_step_3_function_MClass.py

### Model 2 (by Qin and Wang, 2019)
Programming language: R

Main simulation file:
1. Mixed_CTM_QinWang_Codes.R

## Outputs:
1. Heatmap showing traffic density within a cell, for each cell at each timestep
2. Heatmap showing CAV proportion within a cell, for each cell at each timestep
3. Line plot showing cumulative traffic inflows to and outflows from the road link model
4. Line plot showing link outflow rate
     
## Limitations:
The codes are only for simulating a single one-lane link. More codes are needed to extend the model to represent merging, diverging, network, multiple lanes, and other road network components. The models in the codes also do not consider the First-in-First-out (FIFO) principle. This creates potential bias in the simulation output, particularly in terms of unintended or unrealistic overtaking. I have been developing more code to solve such issues for my PhD study. Happy to discuss this further.

