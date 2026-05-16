# Title: Multiclass FIFO Cell Transmission Model Code - A Tool to Model Traffic Flow Propagation Consisting of Connected Autonomous Vehicles (CAV) and Normal Vehicles (NV)

## Programming Language Used: Python

## General Description and Goals of the Code
The Multiclass First-in-First-out Cell Transmission Model (MF-CTM) is a tool to model traffic flow propagation, consisting of connected autonomous vehicles (CAV) and normal vehicles (NV).

In the future, CAVs will likely coexist with NVs on the road; therefore, a model is needed to assess different CAV penetration levels. MF-CTM can be an alternative approach for this purpose, as it can explore the impact of CAVs on traffic flow propagation and congestion (measured by queue length, queue dissipation time, travel time, delay, and speed) across different CAV penetration levels, i.e., 0% to 100%. 

MF-CTM is particularly relevant for researchers and practitioners in the area of traffic flow theory and modelling.
A detailed description of MF-CTM can be seen in the following publication [Farda, et.al., 2026](https://www.sciencedirect.com/science/article/pii/S2352146526001456)

## Motivation for writing the code:
I wrote this code as part of my PhD study. This code is to fulfil the objective no.1 of my study, namely: Explore the propagation of cruising traffic in a single link in the presence of CAV   

## Description of the Approach:
The foundation of the M-CTM is the basic Cell Transmission Model (CTM) developed by [Daganzo, 1994](https://www.sciencedirect.com/science/article/abs/pii/0191261594900027)

Imagine there is a straight road in front of our home. To understand traffic propagation on that road, the Basic CTM represents such a road as a link, and discretises the link into several segments called cells. Such a discretised link is then simulated for a number of timesteps. In each timestep, the traffic enters the link and moves from one cell to the next until it finally exits the link. By using such a simulation, one can then see at which points (or cells) in the link a congestion occurs, the fluctuations of the link outflows, and the travel time of the traffic traversing the link. 

The Basic CTM, however, assumes that the traffic within a link is homogeneous and the road capacity is constant. To model the CAV impact on mixed traffic, which also contains NV, the Basic CTM needs to be modified. The MF-CTM is then a modification of the Basic CTM to accommodate the modelling of mixed traffic consisting of CAV and NV. The model has features, namely, multiclass traffic (CAV and NV), and dynamic road capacity and wave speed based on the share of CAV on the road. Moreover, the model also has a FIFO feature, which prevents the traffic inside the model from having unintended and unrealistic overtaking.

## Outputs:
1. Heatmap showing cell occupancy or the number of vehicles within a cell, for each cell at each timestep
2. Heatmap showing CAV proportion within a cell, for each cell at each timestep
3. Curve showing cumulative traffic inflows to and outflows from the road link model
4. Curve showing link outflow rate
5. Bubble plot showing link travel time of each traffic packet (cohort) as well as CAV proportion in each cohort
     
## Limitations:
The code is only for simulating a single one-lane link. More codes are needed to extend the model to represent merging, diverging, network, multiple lanes, and other road network components. 
