import sys
import os

current_dir = os.path.dirname(__file__)

part_1_path = os.path.abspath(os.path.join(current_dir, "..", "Part_1_IcuQueue"))
sys.path.append(part_1_path)

part_2_path = os.path.abspath(os.path.join(current_dir, "..", "Part_2_CareGiver"))
sys.path.append(part_2_path)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from CareGiverMain import penalty_average_2
from IcuQueueMain import penalty_average_1


random_seed = 5
np.random.seed(random_seed)

def run_standardized_sensitivity_analysis(sample_size=2, 
                                          delta_arrival=0.1, 
                                          delta_length_of_stays=0.05, 
                                          delta_request_frequency=0.1, 
                                          delta_mean_service_time=0.05):
    
    results = []
    
    baseline_penalty_1 = penalty_average_1(sample_size)[0]
    baseline_penalty_2 = penalty_average_2(sample_size)[0]
    baseline_total_penalty = baseline_penalty_1 + baseline_penalty_2
    
    parameters = [
        {"name": "Arrival_Rates", "delta": delta_arrival},
        {"name": "length_of_stays", "delta": delta_length_of_stays},
        {"name": "request_frequency", "delta": delta_request_frequency},
        {"name": "mean_service_time", "delta": delta_mean_service_time},
    ]
    
    for param in parameters:
        delta = param["delta"]
        
        if param["name"] == "Arrival_Rates":
            new_penalty_1 = penalty_average_1(sample_size, delta_arrival=delta)[0]
            new_penalty_2 = penalty_average_2(sample_size, delta_arrival=delta)[0]
        elif param["name"] == "length_of_stays":
            new_penalty_1 = penalty_average_1(sample_size, delta_length_of_stays=delta)[0]
            new_penalty_2 = penalty_average_2(sample_size, delta_length_of_stays=delta)[0]
        elif param["name"] == "request_frequency":
            new_penalty_1 = penalty_average_1(sample_size)[0]
            new_penalty_2 = penalty_average_2(sample_size, delta_request_frequency=delta)[0]
        elif param["name"] == "mean_service_time":
            new_penalty_1 = penalty_average_1(sample_size)[0]
            new_penalty_2 = penalty_average_2(sample_size, delta_mean_service_time=delta)[0]
        
        new_total_penalty = new_penalty_1 + new_penalty_2
        
        sensitivity_index = (new_total_penalty - baseline_total_penalty) / (baseline_total_penalty * delta)
        results.append({"Parameter": param["name"], "Sensitivity Index": sensitivity_index})
    
    results_df = pd.DataFrame(results).sort_values(by="Sensitivity Index", ascending=False)
    return results_df, baseline_total_penalty

def plot_sensitivity_chart(results_df):

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(results_df["Parameter"], results_df["Sensitivity Index"], color="steelblue")
    ax.set_xlabel("Standardized Sensitivity Index", fontsize=12)
    ax.set_ylabel("Parameters", fontsize=12)
    ax.set_title("Standardized Sensitivity Analysis", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    sensitivity_results, baseline_penalty = run_standardized_sensitivity_analysis(sample_size=2)
    print("Baseline Total Penalty:", baseline_penalty)
    print(sensitivity_results)

    plot_sensitivity_chart(sensitivity_results)
