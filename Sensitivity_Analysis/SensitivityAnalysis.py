import sys
import os

# 设置项目路径
project_root = '/Users/kennychan/Downloads/IND-ENG-174'
sys.path.append(project_root)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from Part_2_CareGiver.CareGiverMain import penalty_average_2
from Part_1_IcuQueue.IcuQueueMain import penalty_average_1


# 固定随机种子
random_seed = 5
np.random.seed(random_seed)

def run_standardized_sensitivity_analysis(sample_size=2, 
                                          delta_arrival=0.1, 
                                          delta_length_of_stays=0.05, 
                                          delta_request_frequency=0.1, 
                                          delta_mean_service_time=0.05):
    """
    运行标准化敏感性分析，计算标准化敏感性指数。
    """
    results = []
    
    # 计算基准罚分
    baseline_penalty_1 = penalty_average_1(sample_size)[0]
    baseline_penalty_2 = penalty_average_2(sample_size)[0]
    baseline_total_penalty = baseline_penalty_1 + baseline_penalty_2
    
    # 定义待分析的参数及对应的 delta
    parameters = [
        {"name": "Arrival_Rates", "delta": delta_arrival},
        {"name": "length_of_stays", "delta": delta_length_of_stays},
        {"name": "request_frequency", "delta": delta_request_frequency},
        {"name": "mean_service_time", "delta": delta_mean_service_time},
    ]
    
    # 逐个参数进行敏感性分析
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
        
        # 计算敏感性指数
        sensitivity_index = (new_total_penalty - baseline_total_penalty) / (baseline_total_penalty * delta)
        results.append({"Parameter": param["name"], "Sensitivity Index": sensitivity_index})
    
    # 转换为 DataFrame 并排序
    results_df = pd.DataFrame(results).sort_values(by="Sensitivity Index", ascending=False)
    return results_df, baseline_total_penalty

def plot_sensitivity_chart(results_df):
    """
    绘制标准化敏感性指数的 Tornado 图。
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(results_df["Parameter"], results_df["Sensitivity Index"], color="steelblue")
    ax.set_xlabel("Standardized Sensitivity Index", fontsize=12)
    ax.set_ylabel("Parameters", fontsize=12)
    ax.set_title("Standardized Sensitivity Analysis", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 运行标准化敏感性分析
    sensitivity_results, baseline_penalty = run_standardized_sensitivity_analysis(sample_size=2)
    print("Baseline Total Penalty:", baseline_penalty)
    print(sensitivity_results)
    
    # 绘制标准化敏感性分析图
    plot_sensitivity_chart(sensitivity_results)
