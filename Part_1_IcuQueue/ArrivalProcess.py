import numpy as np
import random

time_horizon = 10 # If you want to modify this parameter, please simultaneously modify 'time_horizon' in Part_2_CareGiver/CareRequest.py
lambda_max = 3.0 
severity_levels = [1, 2, 3] # 1 - Mild; 2 - Moderate; 3 - Severe
probabilities = [0.2, 0.5, 0.3] 

# this function aims at characterizing the rate distribution of one day
# number of patients per hour
# 0 <= t <= 24
def rate_distribution_pdf(t):
    if t >= 9 and t < 12:
        return 3.0
    if t >= 12 and t < 17:
        return 1.5
    if t >= 17 and t < 20:
        return 2.5
    if t >= 20 or t < 4:
        return 0.7
    if t >= 4 and t < 9:
        return 1.0

#print(rate_distribution_pdf(1))

# randomly generate the severity levels of incoming patients.
def severity_level_list(size, severity_levels = severity_levels, probabilities = probabilities):
    return np.random.choice(severity_levels, size, p = probabilities).tolist()

#print(severity_level_list(20))

# This function intends to simulate the arrival process of given time horizon.
# time_horizon: total number of days that we want to simulate
# lambda_max: the maximal arriving rate (number of patients per hour) in a day
def simulate_arrival_process(time_horizon = time_horizon, lambda_max = lambda_max, rate_distribution_pdf = rate_distribution_pdf,  severity_level_list = severity_level_list):
    t = 0 # in hours
    arrival_times = []

    while t < time_horizon * 24:
        t += random.expovariate(lambda_max)

        if t > time_horizon * 24:
            break

        # acceptance-rejection
        if random.uniform(0, 1) < rate_distribution_pdf(t % 24) / lambda_max:
            arrival_times.append(t)

    severity_level_list = severity_level_list(len(arrival_times))
    
    return arrival_times, severity_level_list

#print(simulate_arrival_process())

#arrival_times, severity_level_list = simulate_arrival_process()

"""
total_1 = 0
total_2 = 0
total_3 = 0
for i in severity_level_list:
    if i == 1:
        total_1 += 1
    elif i == 2:
        total_2 += 1
    else:
        total_3 += 1
print(total_1 / len(severity_level_list))
print(total_2 / len(severity_level_list))
print(total_3 / len(severity_level_list))
"""