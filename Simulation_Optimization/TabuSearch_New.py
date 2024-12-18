import sys

project_root = '/Users/sizheli/Desktop/INDENG_174/IND-ENG-174'
sys.path.append(project_root)

import numpy as np
import time
import math
import itertools
import matplotlib.pyplot as plt
from Part_2_CareGiver.CareRequest import simulate_service_process
from Part_1_IcuQueue.IcuQueueMain import penaltyFunction1
from Part_2_CareGiver.CareGiverMain import penaltyFunction2
import random
import matplotlib.colors as mcolors
import os


random_seed = 123
random.seed(random_seed)
np.random.seed(random_seed)


from Part_1_IcuQueue.DepartureProcessWithFIFO import simultaneously_return as fifo_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithPQ import simultaneously_return as pq_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithDPQ import simultaneously_return as dpq_simultaneously_return

from Part_1_IcuQueue.DepartureProcessWithReservedBeds import simultaneously_return as ReservedBeds_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithPQandReservedBeds import simultaneously_return as PQandReservedBeds_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithDPQandReservedBeds import simultaneously_return as DPQandReservedBeds_simultaneously_return

original_num_beds = 100
original_num_caregivers = 50
strategies = ["FIFO", "PQ", "DPQ", "Reserved", "Reserved+PQ", "Reserved+DPQ"]

m_1 = 1
alpha_1 = 0.005
m_2 = 0.01
alpha_2 = 0.1

# Parameters for optimization
budget = 100
price_bed = 10
price_caregiver = 1
max_percentage_of_reservation = 0.2

neighbor_width_pareto = 2
neighbor_width_reserved_beds = 10

initial_guess = (5, 50, "FIFO", 0)


# Find out and print the combinations on the Pareto frontier
def is_pareto_optimal(candidate, solutions):
    for other in solutions:
        if other[0] >= candidate[0] and other[1] >= candidate[1] and other != candidate:
            return False
    return True

def pareto_solutions_bed_caregiver(budget, price_bed, price_caregiver, is_pareto_optimal = is_pareto_optimal):
    solutions = []
    for beds in range(int(budget // price_bed) + 1):
        for caregivers in range(int(budget // price_caregiver) + 1):
            if beds * price_bed + caregivers * price_caregiver <= budget:
                solutions.append((beds, caregivers))
    pareto_solutions = [sol for sol in solutions if is_pareto_optimal(sol, solutions)]
    return pareto_solutions

def neighbors(current_point, budget, price_bed, price_caregiver, strategies = strategies, 
              max_percentage_of_reservation = max_percentage_of_reservation, original_num_beds = original_num_beds,
              neighbor_width_pareto = neighbor_width_pareto, neighbor_width_reserved_beds = neighbor_width_reserved_beds):
    neighbor_points = []

    current_bed, current_caregiver = current_point[0], current_point[1]
    current_reserved_bed = current_point[3]
    current = (current_bed, current_caregiver)
    pareto_solutions = pareto_solutions_bed_caregiver(budget, price_bed, price_caregiver)
    current_index = pareto_solutions.index(current)
    #print(current_index)
    pareto_solutions_in_neighbor = []
    
    index = 0
    for pareto_solution in pareto_solutions:
        if abs(index - current_index) <= neighbor_width_pareto:
            pareto_solutions_in_neighbor.append(pareto_solution)
        index += 1

    for solution in pareto_solutions_in_neighbor:

        point_bed = solution[0]
        point_caregiver = solution[1]

        beds = original_num_beds + solution[0]
        max_reserved_beds = math.floor(max_percentage_of_reservation * beds)
        for strategy in strategies:
            point_strategy = strategy
            if strategy in ["Reserved", "Reserved+PQ", "Reserved+DPQ"]:
                for reserved_beds in range(1, max_reserved_beds):
                    if abs(reserved_beds - current_reserved_bed) <= neighbor_width_reserved_beds:
                        point_reserved_beds = reserved_beds
                        point = (point_bed, point_caregiver, point_strategy, point_reserved_beds)
                        neighbor_points.append(point)
            else:
                point_reserved_beds = 0
                point = (point_bed, point_caregiver, point_strategy, point_reserved_beds)
                neighbor_points.append(point)

    #print(neighbor_points)
    return neighbor_points
                    
def tabu_search(initial_guess, budget, price_bed, price_caregiver, original_num_beds, original_num_caregivers,
                m_1 = m_1, alpha_1 = alpha_1, m_2 = m_2, alph2_2 = alpha_2):
    tabu_list = []
    current_point = initial_guess

    capacity = original_num_beds + current_point[0]
    num_caregivers = original_num_caregivers + current_point[1]
    reserved_beds = current_point[3]

    if current_point[2] == "FIFO":
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = fifo_simultaneously_return(capacity = capacity)
    elif current_point[2] == "PQ":
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = pq_simultaneously_return(capacity = capacity)
    elif current_point[2] == "DPQ":
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = dpq_simultaneously_return(capacity = capacity)
    elif current_point[2] == "Reserved":
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = ReservedBeds_simultaneously_return(capacity = capacity, reserved_capacity = reserved_beds)
    elif current_point[2] == "Reserved+PQ":
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = PQandReservedBeds_simultaneously_return(capacity = capacity, reserved_capacity = reserved_beds)
    elif current_point[2] == "Reserved+DPQ":
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = DPQandReservedBeds_simultaneously_return(capacity = capacity, reserved_capacity = reserved_beds)

    service_waiting_times, severity_cor_waiting_times = simulate_service_process(
        start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list,
        arrival_times=arrival_times, capacity=capacity, number_of_care_givers=num_caregivers
    )

    IcuQueue_penalty = penaltyFunction1(m_1, alpha_1, severity_level_list=severity_level_list, waiting_times=waiting_times)
    CareRequest_penalty = penaltyFunction2(m_2, alpha_2, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
    total_penalty = IcuQueue_penalty + CareRequest_penalty

    tabu_list.append(current_point)

    print(f'iteration 0')
    print(f'initial guess: added beds:{current_point[0]}, added caregivers:{current_point[1]}, strategy:{current_point[2]}, reserved_beds:{current_point[3]}')
    print(f'penalty:{total_penalty}')
    print('-' * 50)

    current_minimum = total_penalty
    current_minimizer = current_point

    iteration = 1
    optimal_point_current_iter = current_minimizer
    while True:
        neighbor_points = neighbors(optimal_point_current_iter, budget, price_bed, price_caregiver)
        for neighbor_point in neighbor_points:
            if neighbor_point not in tabu_list:
                current_point = neighbor_point

                capacity = original_num_beds + current_point[0]
                num_caregivers = original_num_caregivers + current_point[1]
                reserved_beds = current_point[3]

                if current_point[2] == "FIFO":
                    arrival_times, severity_level_list, start_times, departure_times, waiting_times = fifo_simultaneously_return(capacity = capacity)
                elif current_point[2] == "PQ":
                    arrival_times, severity_level_list, start_times, departure_times, waiting_times = pq_simultaneously_return(capacity = capacity)
                elif current_point[2] == "DPQ":
                    arrival_times, severity_level_list, start_times, departure_times, waiting_times = dpq_simultaneously_return(capacity = capacity)
                elif current_point[2] == "Reserved":
                    arrival_times, severity_level_list, start_times, departure_times, waiting_times = ReservedBeds_simultaneously_return(capacity = capacity, reserved_capacity = reserved_beds)
                elif current_point[2] == "Reserved+PQ":
                    arrival_times, severity_level_list, start_times, departure_times, waiting_times = PQandReservedBeds_simultaneously_return(capacity = capacity, reserved_capacity = reserved_beds)
                elif current_point[2] == "Reserved+DPQ":
                    arrival_times, severity_level_list, start_times, departure_times, waiting_times = DPQandReservedBeds_simultaneously_return(capacity = capacity, reserved_capacity = reserved_beds)

                service_waiting_times, severity_cor_waiting_times = simulate_service_process(
                    start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list,
                    arrival_times=arrival_times, capacity=capacity, number_of_care_givers=num_caregivers
                )

                IcuQueue_penalty = penaltyFunction1(m_1, alpha_1, severity_level_list=severity_level_list, waiting_times=waiting_times)
                CareRequest_penalty = penaltyFunction2(m_2, alpha_2, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
                total_penalty = IcuQueue_penalty + CareRequest_penalty

                tabu_list.append(current_point)

                if total_penalty < current_minimum:
                    current_minimum = total_penalty
                    current_minimizer = current_point

        if current_minimizer == optimal_point_current_iter:
            print('already find the local minimizer, terminate the program!')
            print('-' * 50)
            print(f'local minimizer: added beds:{current_minimizer[0]}, added caregivers:{current_minimizer[1]}, strategy:{current_minimizer[2]}, reserved_beds:{current_minimizer[3]}')
            print(f'penalty:{current_minimum}')
            break

        print(f'iteration {iteration}')
        print(f'current_minimizer: added beds:{current_minimizer[0]}, added caregivers:{current_minimizer[1]}, strategy:{current_minimizer[2]}, reserved_beds:{current_minimizer[3]}')
        print(f'penalty:{current_minimum}')
        print('-' * 50)

        optimal_point_current_iter = current_minimizer
        iteration += 1

tabu_search(initial_guess, budget, price_bed, price_caregiver, original_num_beds, original_num_caregivers)