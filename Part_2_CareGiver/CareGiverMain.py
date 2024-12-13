from CareRequest import simulate_service_process
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
import os
from scipy import stats
import sys

project_root = '/Users/sizheli/Desktop/INDENG_174/IND-ENG-174'
sys.path.append(project_root)

from Part_1_IcuQueue.DepartureProcessWithFIFO import simultaneously_return

random_seed = 5
random.seed(random_seed)
np.random.seed(random_seed)
sample_size = 5


m_2 = 0.01 # penalty scale
alpha_2 = 0.1 # time sensitivity

def penaltyFunction2(m_2, alpha_2, service_waiting_times, severity_cor_waiting_times):
    total_penalty = 0
    for i in range(len(service_waiting_times)):
        severity = severity_cor_waiting_times[i]
        waiting_time = service_waiting_times[i]
        total_penalty += m_2 * (np.exp(alpha_2 * severity * waiting_time) - 1)
    return total_penalty


# Function to run 100 simulations and aggregate the results
def run_multiple_simulations(num_simulations = sample_size, bin_size =1):
    """
    Runs multiple simulations and returns the aggregated waiting times and severity levels.
    """
    # Placeholder for aggregated data
    aggregated_data = []

    # Run simulations
    for _ in range(num_simulations):
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = simultaneously_return()
        service_waiting_times, severity_cor_waiting_times = simulate_service_process(start_times, departure_times, severity_level_list, arrival_times)
        df = pd.DataFrame({'service_waiting_times': service_waiting_times, 'severity_cor_waiting_times': severity_cor_waiting_times})
        aggregated_data.append(df)
        print(_)
    
    # Concatenate all simulation results
    combined_df = pd.concat(aggregated_data, ignore_index=True)

    # Define bins for waiting times
    max_waiting_time = int(np.ceil(combined_df['service_waiting_times'].max() / bin_size) * bin_size)
    bins = np.arange(0, max_waiting_time + bin_size, bin_size)
    combined_df['time_bins'] = pd.cut(combined_df['service_waiting_times'], bins=bins, right=False)
    
    # Group by time bins and severity levels, then compute the average count
    grouped = combined_df.groupby(['time_bins', 'severity_cor_waiting_times']).size().unstack(fill_value=0)
    grouped_avg = grouped / num_simulations  # Average count per simulation

    return grouped_avg

#print(run_multiple_simulations())

# Function to plot the averaged discrete severity distribution
def plot_average_severity_distribution(grouped_avg, bin_size = 1, save_path = None):
    """
    Plots the average distribution of waiting times with stacked bars representing severity levels.
    """
    bar_positions = np.arange(len(grouped_avg))

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(bar_positions, grouped_avg[1], color='#4e79a7', label='Mild', width=0.9)
    ax.bar(bar_positions, grouped_avg[2], bottom=grouped_avg[1], color='#f28e2c', label='Moderate', width=0.9)
    ax.bar(bar_positions, grouped_avg[3], bottom=grouped_avg[1] + grouped_avg[2], color='#e15759', label='Severe', width=0.9)
    
    ax.set_xlabel('Waiting Time (hours)', fontsize=12)
    ax.set_ylabel('Average Number of Patients', fontsize=12)
    ax.set_title('Average Distribution of Waiting Times by Severity Level', fontsize=15, fontweight='bold')
    ax.legend(title="Severity Level")
    ax.set_xticks(bar_positions)
    ax.set_xticklabels([f"{int(interval.left)}-{int(interval.right)}" for interval in grouped_avg.index], rotation=45)
    plt.tight_layout()
    
    # Save plot if save_path is provided
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to {save_path}")
    plt.show()



# Create output directories
output_dir = "Part_2_Caregiver"
figures_dir = os.path.join(output_dir, "figures")
os.makedirs(figures_dir, exist_ok=True)

# Save the plot to the figures folder
plot_path = os.path.join(figures_dir, "baseline.png") 

grouped_avg = run_multiple_simulations(num_simulations=sample_size, bin_size=1)
plot_average_severity_distribution(grouped_avg, bin_size=1, save_path=plot_path)


# calculate the average penalty and CI of penalties

def penalty_average(sample_size, m_2 = m_2, alpha_2 = alpha_2):
    penalty_list = []
    for i in range(sample_size):
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = simultaneously_return()
        service_waiting_times, severity_cor_waiting_times = simulate_service_process(start_times, departure_times, severity_level_list, arrival_times)
        penalty = float(penaltyFunction2(m_2, alpha_2, service_waiting_times, severity_cor_waiting_times))
        penalty_list.append(penalty)
        average_penalty = np.average(penalty_list)
    return average_penalty, penalty_list

average_penalty, penalty_list = penalty_average(sample_size)
print(penalty_list)

def calculate_confidence_interval(data = penalty_list, confidence=0.95):
    mean = np.mean(data)
    
    se = stats.sem(data)
    
    z = stats.norm.ppf((1 + confidence) / 2)

    lower_bound = float(mean - z * se)
    upper_bound = float(mean + z * se)
    
    return (lower_bound, upper_bound)

print("Average Penalty:", average_penalty)
print("95% Confidence Interval:", calculate_confidence_interval())


# Create a penalties subdirectory
penalties_dir = os.path.join(output_dir, "penalties")
os.makedirs(penalties_dir, exist_ok=True)

# Save the average penalty to a file
penalty_file_name = "baseline.txt" 
penalty_path = os.path.join(penalties_dir, penalty_file_name)

with open(penalty_path, "w") as f:
    f.write(f"Penalty 2(Average): {average_penalty}\n")
    f.write(f"95% Confidence Interval:: {calculate_confidence_interval()}\n")

print(f"Penalty result saved to {penalty_path}")
