import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from Part_2_CareGiver.CareGiverMain import run_multiple_simulations, penalty_average_2
from Part_1_IcuQueue.IcuQueueMain import run_multiple_simulations, penalty_average_1
import sys

project_root = '/Users/李奕瑶/IND-ENG-174'
sys.path.append(project_root)


random_seed = 5
np.random.seed(random_seed)

def run_sensitivity_analysis( sample_size=5, delta_arrival=0.05, delta_length_of_stays =0.05):
   
    results = []

    origin_average_penalty_1 = penalty_average_1(sample_size)[0]
    origin_average_penalty_2 = penalty_average_2(sample_size)[0]
    origin_total_penalty = origin_average_penalty_1 + origin_average_penalty_2
    new_average_penalty_1 = penalty_average_1(sample_size, delta_arrival=delta_arrival,delta_length_of_stays=0.00)[0]
    new_average_penalty_2 = penalty_average_2(sample_size, delta_arrival=delta_arrival,delta_length_of_stays=0.00)[0]
    new_total_penalty = new_average_penalty_1 + new_average_penalty_2
    effect = (new_total_penalty - origin_total_penalty) / delta_arrival
    results.append({"Parameter": "Arrival_Rates", "Effect": effect})
    new_average_penalty_1 = penalty_average_1(sample_size, delta_arrival=0.00,delta_length_of_stays=delta_length_of_stays)[0]
    new_average_penalty_2 = penalty_average_2(sample_size, delta_arrival=0.00,delta_length_of_stays=delta_length_of_stays)[0]
    new_total_penalty = new_average_penalty_1 + new_average_penalty_2
    effect = (new_total_penalty - origin_total_penalty) / delta_length_of_stays
    results.append({"Parameter": "length_of_stays", "Effect": effect})
    return pd.DataFrame(results)


def plot_tornado_chart(results_df):
    """
    根据灵敏度分析的结果绘制 Tornado 图。
    """
    results_df = results_df.sort_values(by="Effect", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(results_df["Parameter"], results_df["Effect"], color="steelblue")
    ax.set_xlabel("Effect on Penalty", fontsize=12)
    ax.set_ylabel("Parameters", fontsize=12)
    ax.set_title("Tornado Chart: Sensitivity Analysis", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()


sensitivity_results = run_sensitivity_analysis()

plot_tornado_chart(sensitivity_results)
