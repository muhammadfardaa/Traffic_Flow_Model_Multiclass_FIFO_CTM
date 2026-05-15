# Title: Multiclass Cell Transmission Model Code - A Tool to Model Traffic Flow Propagation Consisting of Connected Autonomous Vehicles (CAV) and Normal Vehicles (NV)

# Programming Language Used: Python

# General Description and Goals of the Code
The Multiclass Cell Transmission Model (M-CTM) is a tool to model traffic flow propagation, consisting of connected autonomous vehicles (CAV) and normal vehicles (NV), based on the publication by [Levin and Boyles, 2016](https://www.sciencedirect.com/science/article/abs/pii/S0968090X1500354X) 

In the future, CAVs will likely coexist with NVs on the road; therefore, a model is needed to assess different CAV penetration levels. M-CTM can be an alternative approach for this purpose, as it can explore the impact of CAVs on traffic flow propagation and congestion (measured by queue length and queue dissipation time) across different CAV penetration levels, i.e., 0% to 100%. 

M-CTM is particularly relevant for researchers and practitioners in the area of traffic flow theory and modelling.

# Motivation for writing the code:
I wrote this code as a learning process during the 1st year of my PhD study. By writing the code and simulating the M-CTm for a range of scenarios, I tried to understand how the model behaved and identified aspects that can be improved in the model. The M-CTM is a main reference for my research during my PhD study

# Description of the Approach:
The foundation of the M-CTM is the basic Cell Transmission Model (CTM) developed by [Daganzo, 1994](https://www.sciencedirect.com/science/article/abs/pii/0191261594900027)

Imagine there is a straight road in front of our home. To understand traffic propagation on that road, the Basic CTM represents such a road as a link, and discretises the link into several segments called cells. Such a discretised link is then simulated for a number of timesteps. In each timestep, the traffic enters the link and moves from one cell to the next until it finally exits the link. By using such a simulation, one can then see at which points (or cells) in the link a congestion occurs, the fluctuations of the link outflows, and the travel time of the traffic traversing the link. 


# Outputs:

# Limitations:
