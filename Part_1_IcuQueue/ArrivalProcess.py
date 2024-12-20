import numpy as np
import random


time_horizon = 10 # If you want to modify this parameter, please simultaneously modify 'time_horizon' in Part_2_CareGiver/CareRequest.py
lambda_max = 4.0 
severity_levels = [1, 2, 3] # 1 - Mild; 2 - Moderate; 3 - Severe
probabilities = [0.2, 0.5, 0.3] 
average_length_of_stays = [3, 7, 15] # averagely, Mild - 3 days; Moderate - 7 days; Severe - 15 days.

# this function aims at characterizing the rate distribution of one day
# number of patients per hour
# 0 <= t <= 24
def rate_distribution_pdf(t, delta = 0.00):
    if t >= 9 and t < 12:
        return 3.0 + delta
    if t >= 12 and t < 17:
        return 1.5 + delta
    if t >= 17 and t < 20:
        return 2.5 + delta
    if t >= 20 or t < 4:
        return 0.7 + delta
    if t >= 4 and t < 9:
        return 1.0 + delta

#print(rate_distribution_pdf(1))

# randomly generate the severity levels of incoming patients.
def severity_level_list(size, severity_levels = severity_levels, probabilities = probabilities):
    return np.random.choice(severity_levels, size, p = probabilities).tolist()

#print(severity_level_list(20))

# This function intends to simulate the arrival process of given time horizon.
# time_horizon: total number of days that we want to simulate
# lambda_max: the maximal arriving rate (number of patients per hour) in a day
def simulate_arrival_process(time_horizon = time_horizon, lambda_max = lambda_max, rate_distribution_pdf = rate_distribution_pdf,  severity_level_list = severity_level_list, delta_arrival =0.00):
    t = 0 # in hours
    arrival_times = []

    while t < time_horizon * 24:
        t += random.expovariate(lambda_max)

        if t > time_horizon * 24:
            break

        # acceptance-rejection
        if random.uniform(0, 1) < rate_distribution_pdf(t % 24, delta_arrival) / lambda_max:
            arrival_times.append(t)

    severity_level_list = severity_level_list(len(arrival_times))
    
    return arrival_times, severity_level_list

# print(simulate_arrival_process())

#arrival_times, severity_level_list = simulate_arrival_process()

def generate_length_of_stays(severity_level_list, average_length_of_stays=average_length_of_stays):
    length_of_stays = []
    for severity in severity_level_list:
        avg_length = average_length_of_stays[severity - 1]  
        length_of_stay = np.random.exponential(avg_length)
        length_of_stays.append(length_of_stay)
    return length_of_stays

# length_of_stays = generate_length_of_stays(severity_level_list)
# print(length_of_stays[23])

