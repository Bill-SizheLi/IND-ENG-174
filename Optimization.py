import numpy as np
import time
import matplotlib.pyplot as plt
from Part_2_CareGiver.CareRequest import simulate_service_process
from Part_1_IcuQueue.IcuQueueMain import penaltyFunction1
from Part_2_CareGiver.CareGiverMain import penaltyFunction2
import random

random_seed = 5
random.seed(random_seed)
np.random.seed(random_seed)


from Part_1_IcuQueue.DepartureProcessWithFIFO import simultaneously_return as fifo_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithPQ import simultaneously_return as pq_simultaneously_return
from Part_1_IcuQueue.DepartureProcessWithDPQ import simultaneously_return as dpq_simultaneously_return
func_list = [fifo_simultaneously_return, pq_simultaneously_return, dpq_simultaneously_return]


# Parameters for optimization
budget = 105.5
price_bed = 10
price_caregiver = 1
original_num_beds = 100
original_num_caregivers = 50





# Find out all feasible bed and caregiver combinations and print 
solutions = []
for beds in range(int(budget // price_bed) + 1):
    for caregivers in range(int(budget // price_caregiver) + 1):
        if beds * price_bed + caregivers * price_caregiver <= budget:
            solutions.append((beds, caregivers))

print("All feasible bed and caregiver combinations (number of beds, number of caregivers):")
for solution in solutions:
   print(solution)




# Find out and print the combinations on the Pareto frontier
def is_pareto_optimal(candidate, solutions):
    for other in solutions:
        if other[0] >= candidate[0] and other[1] >= candidate[1] and other != candidate:
            return False
    return True

pareto_solutions = [sol for sol in solutions if is_pareto_optimal(sol, solutions) and sol[0] > 0 and sol[1] > 0]

print("Pareto frontier bed and caregiver combinations (number of beds, number of caregivers):")
for solution in pareto_solutions:
    print(solution)




# Optimization function
def optimize_capacity_and_caregivers(pareto_solutions, func):
    """
    Perform brute-force search for optimal capacity and numbers of care givers.
    Returns a result dictionary containing waiting times and penalties for each combination.
    """
    results = {}

    #Record running time of optimization process
    start_time = time.time()

    for num_capacity, num_care_givers in pareto_solutions:
        random.seed(42)
        np.random.seed(42)
        num_capacity = num_capacity + original_num_beds
        num_care_givers = num_care_givers + original_num_caregivers
        print(f"Running simulation for Capacity: {num_capacity}, Care Givers: {num_care_givers}")

        # Simulate ICU Queue (Part 1)
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = func(capacity=num_capacity)
        # Simulate Caregiver Queue (Part 2)
        service_waiting_times, severity_cor_waiting_times = simulate_service_process(start_times=start_times, departure_times=departure_times, severity_level_list=severity_level_list, arrival_times=arrival_times,
                             capacity=num_capacity, number_of_care_givers=num_care_givers)
        # Calculate average waiting time
        avg_queueing_waiting_time = np.mean(waiting_times) 
        avg_service_waiting_time = np.mean(service_waiting_times) 
        
        # Calculate penalties
        IcuQueue_penalty = penaltyFunction1(1, 0.005, severity_level_list=severity_level_list, waiting_times=waiting_times)
        CareRequest_penalty = penaltyFunction2(0.01, 0.1, service_waiting_times=service_waiting_times, severity_cor_waiting_times=severity_cor_waiting_times)
        Total_penalty = IcuQueue_penalty + CareRequest_penalty
        
        results[(num_capacity, num_care_givers)] = (avg_queueing_waiting_time, avg_service_waiting_time, IcuQueue_penalty, CareRequest_penalty, Total_penalty)
        
        print(f"Average Queueing Waiting Time: {avg_queueing_waiting_time:.2f} hours")
        print(f"Average Service Waiting Time: {avg_service_waiting_time:.2f} minutes")
        print(f"Icu Queue Penalty: {IcuQueue_penalty:.2f}")
        print(f"Care Request Penalty: {CareRequest_penalty:.2f}")
        print(f"Total Penalty: {Total_penalty:.2f}")

    end_time = time.time() 
    elapsed_time = end_time - start_time 
    print(f"\nFunction Execution Time: {elapsed_time:.2f} seconds")
    return results, elapsed_time


func_list = [
    ("FIFO", fifo_simultaneously_return),
    ("PQ", pq_simultaneously_return),
    ("DPQ", dpq_simultaneously_return)
]

all_results = {}
execution_times = {}

for func_name, func in func_list:
    print(f"Running optimization with strategy: {func_name}")
    results, elapsed_time = optimize_capacity_and_caregivers(pareto_solutions, func)
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

print("\nBest Strategy and Optimal Configuration:")
print(f"Strategy: {best_strategy}")
print(f"Capacity: {best_config[0]}, Number of Care Givers: {best_config[1]}")
print(f"Additional Capacity: {best_config[0] - original_num_beds}, Additional Number of Care Givers: {best_config[1] - original_num_caregivers}")
print(f"Average Queueing Waiting Time: {optimal_avg_queueing_waiting_time:.2f} minutes")
print(f"Average Service Waiting Time: {optimal_avg_service_waiting_time:.2f} minutes")
print(f"ICU Queue Penalty: {optimal_IcuQueue_penalty:.2f}")
print(f"Care Request Penalty: {optimal_CareRequest_penalty:.2f}")
print(f"Total Penalty: {optimal_Total_penalty:.2f}")


print("\nExecution Times for Each Strategy:")
for func_name, elapsed_time in execution_times.items():
    print(f"{func_name} Strategy: {elapsed_time:.2f} seconds")


















'''

# Find the optimal configuration
optimal_config = min(results, key=lambda x: results[x][4])  # Minimize Total_penalty
optimal_avg_queueing_waiting_time, optimal_avg_service_waiting_time, optimal_IcuQueue_penalty, optimal_CareRequest_penalty, optimal_Total_penalty = results[optimal_config]

print("\nOptimal Configuration:")
print(f"Capacity: {optimal_config[0]}, Number of Care Givers: {optimal_config[1]}")
print(f"Additional Capacity: {optimal_config[0] - original_num_beds}, Additional Number of Care Givers: {optimal_config[1] - original_num_caregivers}")
print(f"Average Queueing Waiting Time: {optimal_avg_queueing_waiting_time:.2f} minutes")
print(f"Average Service Waiting Time: {optimal_avg_service_waiting_time:.2f} minutes")
print(f"ICU Queue Penalty: {optimal_IcuQueue_penalty:.2f}")
print(f"Care Request Penalty: {optimal_CareRequest_penalty:.2f}")
print(f"Total Penalty: {optimal_Total_penalty:.2f}")
'''
'''
# Plot the results
capacity_list, care_givers_list, avg_queueing_waiting_times, avg_service_waiting_times, total_penalties = zip(*[(k[0], k[1], v[0], v[1], v[4]) for k, v in results.items()])



plt.figure(figsize=(10, 6))
sc = plt.scatter(capacity_list, care_givers_list, c=total_penalties, cmap='viridis', s=100, edgecolors='k', vmin=min(total_penalties), vmax=max(total_penalties))
plt.colorbar(sc, label='Total Penalty')
plt.xlabel('Bed Capacity')
plt.ylabel('Number of Care Givers')
plt.title('Optimization of Capacity and Number of Care Givers using Tabu Search')

for i, txt in enumerate(total_penalties):
    plt.annotate(f"{txt:.1f}", (capacity_list[i], care_givers_list[i]), fontsize=9, ha='right', va='bottom')

plt.grid(True)
plt.show()
'''







# Plot the results separately for each strategy
for func_name, results in all_results.items():
    capacity_list, care_givers_list, avg_queueing_waiting_times, avg_service_waiting_times, total_penalties = zip(
        *[(k[0], k[1], v[0], v[1], v[4]) for k, v in results.items()]
    )
    
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(
        capacity_list,
        care_givers_list,
        c=total_penalties,
        cmap='viridis',
        s=100,
        edgecolors='k',
        vmin=min(total_penalties),
        vmax=max(total_penalties)
    )
    plt.colorbar(sc, label='Total Penalty')
    plt.xlabel('Bed Capacity')
    plt.ylabel('Number of Care Givers')
    plt.title(f'Optimization of Capacity and Number of Care Givers using {func_name} Strategy')
    
    for i, txt in enumerate(total_penalties):
        plt.annotate(f"{txt:.1f}", (capacity_list[i], care_givers_list[i]), fontsize=9, ha='right', va='bottom')

    plt.grid(True)
    plt.show()





'''
plt.figure(figsize=(12, 8))

# 使用不同的标记和颜色来区分策略
markers = {'FIFO': 'o', 'PQ': 's', 'DPQ': 'D'}
colors = {'FIFO': 'Blues', 'PQ': 'Greens', 'DPQ': 'Reds'}

for func_name, results in all_results.items():
    # 提取当前策略的结果数据
    capacity_list, care_givers_list, avg_queueing_waiting_times, avg_service_waiting_times, total_penalties = zip(
        *[(k[0], k[1], v[0], v[1], v[4]) for k, v in results.items()]
    )
    
    # 绘制散点图
    sc = plt.scatter(
        capacity_list,
        care_givers_list,
        c=total_penalties,
        cmap=colors[func_name],
        marker=markers[func_name],
        s=100,
        edgecolors='k',
        label=f"{func_name} Strategy"
    )
    plt.colorbar(sc, label=f'Total Penalty ({func_name})')

# 图形设置
plt.xlabel('Bed Capacity')
plt.ylabel('Number of Care Givers')
plt.title('Optimization of Capacity and Number of Care Givers for Different Strategies')
plt.legend()
plt.grid(True)
plt.show()
'''






