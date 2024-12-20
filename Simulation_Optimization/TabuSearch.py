import sys
import os

current_dir = os.path.dirname(__file__)

part_1_path = os.path.abspath(os.path.join(current_dir, "..", "Part_1_IcuQueue"))
sys.path.append(part_1_path)

part_2_path = os.path.abspath(os.path.join(current_dir, "..", "Part_2_CareGiver"))
sys.path.append(part_2_path)

import numpy as np
import time
import math
import matplotlib.pyplot as plt
from CareRequest import simulate_service_process
from IcuQueueMain import penaltyFunction1
from CareGiverMain import penaltyFunction2
import random
import matplotlib.pyplot as plt


random_seed = 123
random.seed(random_seed)
np.random.seed(random_seed)


from DepartureProcessWithFIFO import simultaneously_return as fifo_simultaneously_return
from DepartureProcessWithPQ import simultaneously_return as pq_simultaneously_return
from DepartureProcessWithDPQ import simultaneously_return as dpq_simultaneously_return

from DepartureProcessWithReservedBeds import simultaneously_return as ReservedBeds_simultaneously_return
from DepartureProcessWithPQandReservedBeds import simultaneously_return as PQandReservedBeds_simultaneously_return
from DepartureProcessWithDPQandReservedBeds import simultaneously_return as DPQandReservedBeds_simultaneously_return

original_num_beds = 100
original_num_caregivers = 50
strategies = ["FIFO", "PQ", "DPQ", "Reserved", "Reserved+PQ", "Reserved+DPQ"]

m_1 = 1
alpha_1 = 0.005
m_2 = 0.01
alpha_2 = 0.1

# Parameters for optimization
budget = 50
price_bed = 10
price_caregiver = 1
max_percentage_of_reservation = 0.2

neighbor_width_pareto = 2
neighbor_width_reserved_beds = 1

# initial_guess is of the form (additional_num_beds, additonal_num_caregivers, strategy, num_reserved_beds)
initial_guess = (4, 10, "FIFO", 0)




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
                m_1 = m_1, alpha_1 = alpha_1, m_2 = m_2, alpha_2 = alpha_2):
    tabu_list = []
    current_point = initial_guess

    capacity = original_num_beds + current_point[0]
    num_caregivers = original_num_caregivers + current_point[1]
    reserved_beds = current_point[3]


    best_results = {
    "FIFO": None,
    "PQ": None,
    "DPQ": None,
    "Reserved": None,
    "Reserved+PQ": None,
    "Reserved+DPQ": None
    }# Store the optimal solution for each strategy


    start_time = time.time()

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


    if current_point[2] in ["FIFO", "PQ", "DPQ"]:
        best_results[current_point[2]] = (capacity, num_caregivers, 0, total_penalty)
    else:
         best_results[current_point[2]] = (capacity, num_caregivers, reserved_beds, total_penalty)




    tabu_list.append(current_point)

    print(f'iteration 0')
    print(f'initial guess: added beds:{current_point[0]}, added caregivers:{current_point[1]}, strategy:{current_point[2]}, reserved_beds:{current_point[3]}')
    print(f'penalty:{total_penalty}')
    print('The first iteration takes longer time')
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
                print(current_point)
                print(total_penalty)
                print('-'*50)
                tabu_list.append(current_point)

                if total_penalty < current_minimum:
                    current_minimum = total_penalty
                    current_minimizer = current_point
                    

        if current_minimizer == optimal_point_current_iter:
            print('already find the local minimizer, terminate the program!')
            print('-' * 50)
            print(f'local minimizer: added beds:{current_minimizer[0]}, added caregivers:{current_minimizer[1]}, strategy:{current_minimizer[2]}, reserved_beds:{current_minimizer[3]}')
            print(f'penalty:{current_minimum}')

            end_time = time.time() 
            elapsed_time = end_time - start_time 
            print(f"\nFunction Execution Time: {elapsed_time:.2f} seconds")
            break

        print(f'iteration {iteration}')
        print(f'current_minimizer: added beds:{current_minimizer[0]}, added caregivers:{current_minimizer[1]}, strategy:{current_minimizer[2]}, reserved_beds:{current_minimizer[3]}')
        print(f'penalty:{current_minimum}')
        print('-' * 50)

        best_results[current_minimizer[2]] = (original_num_beds + current_minimizer[0], original_num_caregivers + current_minimizer[1], current_minimizer[3], current_minimum)  # Update to the current point

        optimal_point_current_iter = current_minimizer
        iteration += 1
    return best_results




best_results = tabu_search(initial_guess, budget, price_bed, price_caregiver, original_num_beds, original_num_caregivers)
print(best_results)

def plot_best_points(best_results, strategies):
    """
    Plot the 3D chart of the optimal point for each strategy, 
    where the X-axis represents the combination of (number of beds, number of caregivers), 
    the Y-axis represents the number of reserved beds, and the Z-axis represents the strategy
    """
    # Mapping strategies to Z-axis indices
    strategy_indices = {strategy: i for i, strategy in enumerate(strategies)}

    # Extract optimal point for each strategy
    x_vals = []  # (number of beds, number of caregivers)  
    y_vals = []  # number of reserved beds
    z_vals = []  # strategy index
    penalties = []  # total penalty



    for strategy, value in best_results.items():
        if value is not None:  
            beds, caregivers, reserved_beds, penalty = value
            x_vals.append((beds, caregivers))
            y_vals.append(reserved_beds)
            z_vals.append(strategy_indices[strategy])
            penalties.append(penalty)

    x_indices = list(range(len(x_vals)))
    x_labels = [f"{x[0]}, {x[1]}" for x in x_vals]

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(
        x_indices, y_vals, z_vals, c=penalties, cmap='inferno_r', s=100, edgecolors='black'
    )

    for i in range(len(penalties)):
        # Vertical line to the (X, Y) plane
        ax.plot(
            [x_indices[i], x_indices[i]], [y_vals[i], y_vals[i]], [0, z_vals[i]],
            linestyle="--", color="gray", alpha=0.7
        )
        # Vertical line to the (Y, Z) plane
        ax.plot(
            [x_indices[i], x_indices[i]], [y_vals[i], y_vals[i] + 30], [z_vals[i], z_vals[i]],
            linestyle="--", color="gray", alpha=0.7
        )

    for i in range(len(penalties)):
        ax.text(
            x_indices[i], y_vals[i], z_vals[i] + 0.2, f"{penalties[i]:.2f}",
            color='black', fontsize=10, ha='center'
        )

    ax.set_xticks(x_indices)
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    ax.set_xlabel('(Beds, Caregivers)', labelpad=15)
    ax.set_ylabel('Reserved Beds', labelpad=15)
    ax.set_zlabel('Strategy', labelpad=15)

    ax.set_zticks(list(strategy_indices.values()))
    ax.set_zticklabels(list(strategy_indices.keys()))

    ax.set_title("Best Points for Each Strategy", pad=20)

    colorbar = fig.colorbar(scatter, ax=ax, pad=0.1)
    colorbar.set_label('Total Penalty')

    plt.show()



strategies = ["FIFO", "PQ", "DPQ", "Reserved", "Reserved+PQ", "Reserved+DPQ"]


plot_best_points(best_results, strategies)




'''
Parameters:
original_num_beds = 100
original_num_caregivers = 50
m_1 = 1
alpha_1 = 0.005
m_2 = 0.01
alpha_2 = 0.1

budget = 100
price_bed = 10
price_caregiver = 1
max_percentage_of_reservation = 0.2

neighbor_width_pareto = 2
neighbor_width_reserved_beds = 10

initial_guess = (4, 10, "FIFO", 0)




Running Results:
iteration 0
initial guess: added beds:5, added caregivers:50, strategy:FIFO, reserved_beds:0
penalty:854.7585519492178
--------------------------------------------------
iteration 1
current_minimizer: added beds:5, added caregivers:50, strategy:Reserved, reserved_beds:2
penalty:140.65469495553143
--------------------------------------------------
already find the local minimizer, terminate the program!
--------------------------------------------------
local minimizer: added beds:5, added caregivers:50, strategy:Reserved, reserved_beds:2
penalty:140.65469495553143

Function Execution Time: 1148.31 seconds
best_results: {'FIFO': (106, 90, 0, 296.57766041026383), 'PQ': (105, 100, 0, 169.00067892412636), 'DPQ': (104, 110, 0, 542.8668084600171), 
'Reserved': (105, 100, 2, 140.65469495553143), 'Reserved+PQ': (106, 90, 2, 152.6189195361217), 'Reserved+DPQ': (103, 120, 8, 2697.1821754053008)}
'''