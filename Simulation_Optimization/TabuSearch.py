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
func_list = [fifo_simultaneously_return, pq_simultaneously_return, dpq_simultaneously_return]

from Part_1_IcuQueue.DepartureProcessWithDPQandReservedBeds import simultaneously_return as DPQandReservedBeds_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithPQandReservedBeds import simultaneously_return as PQandReservedBeds_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithReservedBeds import simultaneously_return as ReservedBeds_simultaneously_return
func_list_with_reserevd_beds = [DPQandReservedBeds_simultaneously_return, PQandReservedBeds_simultaneously_return, ReservedBeds_simultaneously_return]


# Parameters for optimization
budget = 300
price_bed = 10
price_caregiver = 1
original_num_beds = 100
original_num_caregivers = 50
original_num_reserved_beds = 0
max_percentage_of_reservation = 0.1




# Find out and print the combinations on the Pareto frontier
def is_pareto_optimal(candidate, solutions):
    for other in solutions:
        if other[0] >= candidate[0] and other[1] >= candidate[1] and other != candidate:
            return False
    return True








# Find out all feasible bed and caregiver combinations and print 
solutions = []
for beds in range(int(budget // price_bed) + 1):
    for caregivers in range(int(budget // price_caregiver) + 1):
        if beds * price_bed + caregivers * price_caregiver <= budget:
            solutions.append((beds, caregivers))

print("All feasible bed and caregiver combinations (number of beds, number of caregivers):")
for solution in solutions:
   print(solution)



pareto_solutions = [sol for sol in solutions if is_pareto_optimal(sol, solutions)]

print("Pareto frontier bed and caregiver combinations (number of beds, number of caregivers):")
for solution in pareto_solutions:
    print(solution)







# Find out all feasible bed, caregiver, and reserved bed combinations and print
solutions_with_reserved_beds = []

for solution in pareto_solutions:
    beds, caregivers = solution
    for reserved_beds in range(1, math.floor((original_num_beds + beds) * max_percentage_of_reservation) + 1):
        solutions_with_reserved_beds.append((beds, caregivers, reserved_beds))

print("All feasible bed, caregiver, and reserved bed combinations (beds, caregivers, reserved beds):")
for solution in solutions_with_reserved_beds:
    print(solution)








def generate_neighborhood(pareto_solutions, current_solution, tabu_list):
    """
    Generate neighboring solutions of the current solution by selecting adjacent solutions from the pareto_solutions. 
    This includes two solutions before and after the current solution. 
    If a neighboring solution is in the Tabu List, it is not included in the neighborhood
    """
    idx = pareto_solutions.index(current_solution)
    neighbors = []

    if idx > 1:
        neighbors.append(pareto_solutions[idx - 1])
        neighbors.append(pareto_solutions[idx - 2])
    
    if idx < len(pareto_solutions) - 2:
        neighbors.append(pareto_solutions[idx + 1])
        neighbors.append(pareto_solutions[idx + 2])

    neighbors = [neighbor for neighbor in neighbors if neighbor not in tabu_list]

    return neighbors



def generate_neighborhood_with_reserved_beds(pareto_solutions, current_solution, tabu_list):
    """
    Generate neighboring solutions of the current solution by selecting adjacent solutions from the pareto_solutions. 
    This includes two solutions before and after the current solution. 
    If a neighboring solution is in the Tabu List, it is not included in the neighborhood
    """
    idx = pareto_solutions.index(current_solution)
    neighbors = []

    if idx > 9:
        neighbors.append(pareto_solutions[idx - 9])
        neighbors.append(pareto_solutions[idx - 10])
    
    if idx < len(pareto_solutions) - 10:
        neighbors.append(pareto_solutions[idx + 9])
        neighbors.append(pareto_solutions[idx + 10])

    neighbors = [neighbor for neighbor in neighbors if neighbor not in tabu_list]

    return neighbors


def tabu_search(pareto_solutions, func):
    """
    Use Tabu Search to optimize the allocation of capacity and nursing staff until a local optimum is found
    """
    # 1. Evaluate initial solution
    random_offset = random.randint(-3, 3)
    current_index = len(pareto_solutions) // 2 + random_offset
    current_index = max(0, min(current_index, len(pareto_solutions) - 1))
    current_solution = pareto_solutions[current_index]

    num_capacity, num_care_givers = current_solution
    num_capacity = num_capacity + original_num_beds
    num_care_givers = num_care_givers + original_num_caregivers

    # Simulate ICU Queue (Part 1)
    arrival_times, severity_level_list, start_times, departure_times, waiting_times = func(capacity=num_capacity)
    # Simulate Caregiver Queue (Part 2)
    service_waiting_times, severity_cor_waiting_times = simulate_service_process(
        start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list,
        arrival_times=arrival_times, capacity=num_capacity, number_of_care_givers=num_care_givers
    )
    avg_queueing_waiting_time = np.mean(waiting_times)
    avg_service_waiting_time = np.mean(service_waiting_times)
    IcuQueue_penalty = penaltyFunction1(1, 0.005, severity_level_list=severity_level_list, waiting_times=waiting_times)
    CareRequest_penalty = penaltyFunction2(0.01, 0.1, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
    total_penalty = IcuQueue_penalty + CareRequest_penalty
    best_solution = current_solution
    best_total_penalty = total_penalty

    tabu_list = []  # Tabu List is used to store the solutions that have been explored
    
    results = {}

    #Record running time of optimization process
    start_time = time.time()

    iteration = 0
    flag = True
    while flag:  # Repeat infinitely until a local optimum is found
        iteration += 1
        neighborhood = generate_neighborhood(pareto_solutions, current_solution, tabu_list)
        print('-'*25)
        print(f'Iteration {iteration}')
        print(f'Current solution capacity number:{num_capacity}, care givers number:{num_care_givers}')
        print(f'Current solution total penalty:{best_total_penalty}')

        # 2. Traverse the solutions in the neighborhood and break if we find one better than current solution
        for neighbor in neighborhood:
            num_capacity, num_care_givers = neighbor
            num_capacity = num_capacity + original_num_beds
            num_care_givers = num_care_givers + original_num_caregivers
            print(f'Searching neighbor capacity number:{num_capacity}, care givers number:{num_care_givers}')

            # Simulate ICU Queue (Part 1)
            arrival_times, severity_level_list, start_times, departure_times, waiting_times = func(capacity=num_capacity)

            # Simulate Caregiver Queue (Part 2)
            service_waiting_times, severity_cor_waiting_times = simulate_service_process(
                start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list,
                arrival_times=arrival_times, capacity=num_capacity, number_of_care_givers=num_care_givers
            )
            avg_queueing_waiting_time = np.mean(waiting_times)
            avg_service_waiting_time = np.mean(service_waiting_times)
            IcuQueue_penalty = penaltyFunction1(1, 0.005, severity_level_list=severity_level_list, waiting_times=waiting_times)
            CareRequest_penalty = penaltyFunction2(0.01, 0.1, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
            total_penalty = IcuQueue_penalty + CareRequest_penalty

            tabu_list.append(neighbor)

            print(f'Neighbor total penalty:{total_penalty}')

            # The neighbor is better than current solution 
            if total_penalty < best_total_penalty:
                best_solution = neighbor
                best_total_penalty = total_penalty
                current_solution = best_solution
                break 
        else:
            flag = False



    print('Local optimal found:', best_solution)
    results[(num_capacity, num_care_givers)] = (avg_queueing_waiting_time, avg_service_waiting_time, IcuQueue_penalty, CareRequest_penalty, best_total_penalty)
    end_time = time.time() 
    elapsed_time = end_time - start_time 
    print(f"\nFunction Execution Time: {elapsed_time:.2f} seconds")
        

    return results, elapsed_time





def tabu_search_with_reserved_beds(pareto_solutions, func):
    """
    Use Tabu Search to optimize the allocation of capacity and nursing staff until a local optimum is found
    """
    # 1. Evaluate initial solution
    random_offset = random.randint(-3, 3)
    current_index = len(pareto_solutions) // 2 + random_offset
    current_index = max(0, min(current_index, len(pareto_solutions) - 1))
    current_solution = pareto_solutions[current_index]

    num_capacity, num_care_givers, num_reserved_beds = current_solution
    num_capacity = num_capacity + original_num_beds
    num_care_givers = num_care_givers + original_num_caregivers

    # Simulate ICU Queue (Part 1)
    arrival_times, severity_level_list, start_times, departure_times, waiting_times = func(capacity=num_capacity, reserved_capacity = num_reserved_beds)
    # Simulate Caregiver Queue (Part 2)
    service_waiting_times, severity_cor_waiting_times = simulate_service_process(
        start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list,
        arrival_times=arrival_times, capacity=num_capacity, number_of_care_givers=num_care_givers
    )
    avg_queueing_waiting_time = np.mean(waiting_times)
    avg_service_waiting_time = np.mean(service_waiting_times)
    IcuQueue_penalty = penaltyFunction1(1, 0.005, severity_level_list=severity_level_list, waiting_times=waiting_times)
    CareRequest_penalty = penaltyFunction2(0.01, 0.1, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
    total_penalty = IcuQueue_penalty + CareRequest_penalty
    best_solution = current_solution
    best_total_penalty = total_penalty

    tabu_list = []  # Tabu List is used to store the solutions that have been explored
    
    results = {}

    #Record running time of optimization process
    start_time = time.time()

    iteration = 0
    flag = True
    while flag:  # Repeat infinitely until a local optimum is found
        iteration += 1
        neighborhood = generate_neighborhood_with_reserved_beds(pareto_solutions, current_solution, tabu_list)
        print('-'*25)
        print(f'Iteration {iteration}')
        print(f'Current solution capacity number:{num_capacity}, care givers number:{num_care_givers}, reserved beds number:{num_reserved_beds}')
        print(f'Current solution total penalty:{best_total_penalty}')


        # 2. Traverse the solutions in the neighborhood and break if we find one better than current solution
        for neighbor in neighborhood:
            num_capacity, num_care_givers, num_reserved_beds = neighbor
            num_capacity = num_capacity + original_num_beds
            num_care_givers = num_care_givers + original_num_caregivers
            print(f'Searching neighbor capacity number:{num_capacity}, care givers number:{num_care_givers}, reserved beds number:{num_reserved_beds}')

            # Simulate ICU Queue (Part 1)
            arrival_times, severity_level_list, start_times, departure_times, waiting_times = func(capacity=num_capacity, reserved_capacity = num_reserved_beds)

            # Simulate Caregiver Queue (Part 2)
            service_waiting_times, severity_cor_waiting_times = simulate_service_process(
                start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list,
                arrival_times=arrival_times, capacity=num_capacity, number_of_care_givers=num_care_givers
            )
            avg_queueing_waiting_time = np.mean(waiting_times)
            avg_service_waiting_time = np.mean(service_waiting_times)
            IcuQueue_penalty = penaltyFunction1(1, 0.005, severity_level_list=severity_level_list, waiting_times=waiting_times)
            CareRequest_penalty = penaltyFunction2(0.01, 0.1, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
            total_penalty = IcuQueue_penalty + CareRequest_penalty

            tabu_list.append(neighbor)

            print(f'Neighbor total penalty:{total_penalty}')

            # The neighbor is better than current solution 
            if total_penalty < best_total_penalty:
                best_solution = neighbor
                best_total_penalty = total_penalty
                current_solution = best_solution
                break 
        else:
            flag = False


    print('Local optimal found:', best_solution)
    results[(num_capacity, num_care_givers, num_reserved_beds)] = (avg_queueing_waiting_time, avg_service_waiting_time, IcuQueue_penalty, CareRequest_penalty, best_total_penalty)
    end_time = time.time() 
    elapsed_time = end_time - start_time 
    print(f"\nFunction Execution Time: {elapsed_time:.2f} seconds")
       
    return results, elapsed_time





all_results = {}
execution_times = {}





func_without_reserved_beds = [
    ("FIFO", fifo_simultaneously_return),
    ("PQ", pq_simultaneously_return),
    ("DPQ", dpq_simultaneously_return)
]


for func_name, func in func_without_reserved_beds:
    print('-'*50)
    print(f"Running optimization with strategy: {func_name}")
    results, elapsed_time = tabu_search(pareto_solutions, func)
    all_results[func_name] = results
    execution_times[func_name] = elapsed_time






func_with_reserevd_beds = [
    ("DPQ and Reserved Beds", DPQandReservedBeds_simultaneously_return),
    ("PQ and Reserved Beds", PQandReservedBeds_simultaneously_return),
    ("Reserved Beds", ReservedBeds_simultaneously_return)
]



for func_name, func in func_with_reserevd_beds:
    print('-'*50)
    print(f"Running optimization with strategy: {func_name}")
    results, elapsed_time = tabu_search_with_reserved_beds(solutions_with_reserved_beds, func)
    all_results[func_name] = results
    execution_times[func_name] = elapsed_time












# Find the configuration with the minimum penalty across all strategies
best_strategy = None
best_config = None
best_total_penalty = float('inf')

for func_name, results in all_results.items():
    current_optimal_config = min(results, key=lambda x: results[x][4])  
    current_total_penalty = results[current_optimal_config][4]

    if current_total_penalty < best_total_penalty:
        best_total_penalty = current_total_penalty
        best_strategy = func_name
        best_config = current_optimal_config
        best_results = results[current_optimal_config]


optimal_avg_queueing_waiting_time, optimal_avg_service_waiting_time, optimal_IcuQueue_penalty, optimal_CareRequest_penalty, optimal_Total_penalty = best_results



if best_strategy in ["FIFO", "PQ", "DPQ"]:
    print("\nBest Strategy and Optimal Configuration:")
    print(f"Strategy: {best_strategy}")
    print(f"Capacity: {best_config[0]}, Number of Care Givers: {best_config[1]}")
    print(f"Additional Capacity: {best_config[0] - original_num_beds}, Additional Number of Care Givers: {best_config[1] - original_num_caregivers}")
    print(f"Average Queueing Waiting Time: {optimal_avg_queueing_waiting_time:.2f} minutes")
    print(f"Average Service Waiting Time: {optimal_avg_service_waiting_time:.2f} minutes")
    print(f"ICU Queue Penalty: {optimal_IcuQueue_penalty:.2f}")
    print(f"Care Request Penalty: {optimal_CareRequest_penalty:.2f}")
    print(f"Total Penalty: {optimal_Total_penalty:.2f}")

else:
    print("\nBest Strategy and Optimal Configuration:")
    print(f"Strategy: {best_strategy}")
    print(f"Non-Reserved Capacity: {best_config[0]}, Number of Care Givers: {best_config[1]}, Number of Reserved Beds: {best_config[2]}")
    print(f"Additional Capacity: {best_config[0] - original_num_beds}, Additional Number of Care Givers: {best_config[1] - original_num_caregivers}, Additional Number of Reserved Beds: {best_config[2] - original_num_reserved_beds}")
    print(f"Average Queueing Waiting Time: {optimal_avg_queueing_waiting_time:.2f} minutes")
    print(f"Average Service Waiting Time: {optimal_avg_service_waiting_time:.2f} minutes")
    print(f"ICU Queue Penalty: {optimal_IcuQueue_penalty:.2f}")
    print(f"Care Request Penalty: {optimal_CareRequest_penalty:.2f}")
    print(f"Total Penalty: {optimal_Total_penalty:.2f}")


print("\nExecution Times for Each Strategy:")
for func_name, elapsed_time in execution_times.items():
    print(f"{func_name} Strategy: {elapsed_time:.2f} seconds")




for func_name, results in all_results.items():
    min_penalty = min(v[4] for v in results.values())
    min_penalty_point = [k for k, v in results.items() if v[4] == min_penalty][0]

    # If it is a strategy without reserved beds, plot a 2D chart
    if func_name in ["FIFO", "PQ", "DPQ"]:
        capacity_list, care_givers_list, avg_queueing_waiting_times, avg_service_waiting_times, total_penalties = zip(
            *[(k[0], k[1], v[0], v[1], v[4]) for k, v in results.items()]
        )

        norm = mcolors.LogNorm(vmin=max(min(total_penalties), 1e-3), vmax=max(total_penalties))

        plt.figure(figsize=(10, 6))
        sc = plt.scatter(
            capacity_list,
            care_givers_list,
            c=total_penalties,
            cmap='inferno_r',  # Reverse the 'inferno' colormap so that smaller penalty values correspond to lighter colors
            s=100,
            edgecolors='black',
            linewidth=1,
            alpha=0.85,
            norm=norm
        )

        # Mark the point with the minimum Total Penalty
        plt.scatter(min_penalty_point[0], min_penalty_point[1], c='red', edgecolors='white', s=150, linewidth=2, label='Min Penalty')

        plt.colorbar(sc, label='Total Penalty')
        plt.xlabel('Bed Capacity')
        plt.ylabel('Number of Care Givers')
        plt.title(f'Optimization of Capacity and Number of Care Givers using {func_name} Strategy')
        
        for i, txt in enumerate(total_penalties):
            plt.annotate(f"{txt:.1f}", (capacity_list[i], care_givers_list[i]), fontsize=9, ha='right', va='bottom')

        plt.grid(True)
        plt.legend()
        plt.show()

    # If the strategy includes reserved beds, plot a 3D chart
    else:
        capacity_list, care_givers_list, reserved_beds_list, total_penalties = zip(
            *[(k[0], k[1], k[2], v[4]) for k, v in results.items()]
        )

        min_penalty = min(total_penalties)
        min_penalty_point = [k for k, v in results.items() if v[4] == min_penalty][0]

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Color mapping, using LogNorm to ensure the color scale adapts to the range of values
        norm = mcolors.LogNorm(vmin=max(min(total_penalties), 1e-3), vmax=max(total_penalties))

        for i in range(len(total_penalties)):
            if total_penalties[i] == min_penalty:
                ax.scatter(
                    capacity_list[i],
                    care_givers_list[i],
                    reserved_beds_list[i],
                    c='red',
                    edgecolors='white',
                    s=150,
                    linewidth=2,
                    label='Min Penalty',
                    zorder=2  # Ensure the minimum penalty point is on the top layer
                )
            else:
                ax.scatter(
                    capacity_list[i],
                    care_givers_list[i],
                    reserved_beds_list[i],
                    c=total_penalties[i],
                    cmap='inferno_r',
                    norm=norm,
                    s=100,
                    edgecolors='black',
                    linewidth=1,
                    alpha=0.85,
                    zorder=1  # Others points are at the bottom
                )

        # Draw the annotations last and set the zorder to the highest
        ax.text(
            min_penalty_point[0],
            min_penalty_point[1],
            min_penalty_point[2] + 0.2,  # Add an offset to avoid overlapping
            f"{min_penalty:.2f}",
            color='red',
            fontsize=10,
            fontweight='bold',
            ha='center',
            zorder=3  # The annotation is displayed on the top layer
        )

        ax.set_xlabel('Bed Capacity')
        ax.set_ylabel('Number of Care Givers')
        ax.set_zlabel('Number of Reserved Beds')
        ax.set_title(f'3D Optimization Results for {func_name} Strategy')

        mappable = plt.cm.ScalarMappable(norm=norm, cmap='inferno_r')
        mappable.set_array(total_penalties)
        fig.colorbar(mappable, ax=ax, label='Total Penalty')

        plt.legend()
        plt.show()
