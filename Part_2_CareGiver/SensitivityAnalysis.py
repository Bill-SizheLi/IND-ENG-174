from CareRequest import simulate_service_process
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
import os
from scipy import stats
import sys
import seaborn as sns

project_root = '/Users/kennychan/Downloads/IND-ENG-174'
sys.path.append(project_root)

from Part_1_IcuQueue.DepartureProcessWithFIFO import simultaneously_return

random_seed = 5
np.random.seed(random_seed)

# 惩罚函数参数
m_2 = 0.01  # 惩罚比例系数
alpha_2 = 0.1  # 时间敏感性系数

# 定义惩罚函数
def penaltyFunction2(m_2, alpha_2, service_waiting_times, severity_cor_waiting_times):
    total_penalty = 0
    for i in range(len(service_waiting_times)):
        severity = severity_cor_waiting_times[i]
        waiting_time = service_waiting_times[i]
        total_penalty += m_2 * (np.exp(alpha_2 * severity * waiting_time) - 1)
    return total_penalty

# 动态调整参数函数
def modify_parameters(arrival_rate_multiplier=1.0, service_time_multiplier=1.0, 
                      request_frequency_val=None, cutoff_points=None, departure_rate_multiplier=1.0):
    global request_frequency, mean_service_time, b_1, b_2, average_length_of_stays

    # 修改服务请求频率
    if request_frequency_val:
        request_frequency = request_frequency_val

    # 修改服务时间
    mean_service_time = [x * service_time_multiplier for x in mean_service_time]

    # 修改阶段分割点
    if cutoff_points:
        b_1, b_2 = cutoff_points

    # 修改离开率
    average_length_of_stays = [x * departure_rate_multiplier for x in average_length_of_stays]


# 单次仿真
def single_simulation(arrival_rate, departure_rate, sample_size=5):
    """
    针对给定的 arrival_rate 和 departure_rate 运行模拟，并返回平均惩罚值。
    """
    # 修改参数
    modify_parameters(
        arrival_rate_multiplier=arrival_rate,
        departure_rate_multiplier=departure_rate,
        service_time_multiplier=1.0,  # 固定服务时间
        request_frequency_val=2,      # 固定请求频率
        cutoff_points=(0.2, 0.9)      # 固定分段点
    )

    # 运行仿真
    penalties = []
    for _ in range(sample_size):
        # 生成模拟数据
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = simultaneously_return()
        # 运行服务过程模拟
        service_waiting_times, severity_cor_waiting_times = simulate_service_process(
            start_times, departure_times, severity_level_list, arrival_times
        )
        # 计算惩罚值
        penalty = penaltyFunction2(m_2, alpha_2, service_waiting_times, severity_cor_waiting_times)
        penalties.append(penalty)
    
    return np.mean(penalties)  # 返回平均惩罚值


# 敏感性分析
def run_arrival_vs_departure_analysis(arrival_rates, departure_rates, sample_size=5):
    """
    针对 arrival_rate 和 departure_rate 进行灵敏度分析，返回结果 DataFrame。
    """
    results = []

    # 并行运行所有参数组合
    for arrival_rate in arrival_rates:
        for departure_rate in departure_rates:
            avg_penalty = single_simulation(arrival_rate, departure_rate, sample_size)
            results.append({
                "arrival_rate": arrival_rate,
                "departure_rate": departure_rate,
                "avg_penalty": avg_penalty
            })
    
    return pd.DataFrame(results)


# 计算瞬时变化率
def calculate_instantaneous_change_heatmap(results_df):
    """
    计算热图中每个点的瞬时变化率。
    """
    # 创建透视表
    pivot_table = results_df.pivot_table(
        index="arrival_rate",
        columns="departure_rate",
        values="avg_penalty"
    )
    
    # 转换为 NumPy 数组
    Z = pivot_table.values
    X = pivot_table.index.values
    Y = pivot_table.columns.values

    # 初始化变化率矩阵
    total_change_rate = np.zeros_like(Z)

    # 计算瞬时变化率
    for i in range(len(X)):
        for j in range(len(Y)):
            # 计算到达率方向的变化率
            if i < len(X) - 1:
                delta_arrival = (Z[i + 1, j] - Z[i, j]) / (X[i + 1] - X[i])
            else:
                delta_arrival = 0  # 边界点设为 0

            # 计算离开率方向的变化率
            if j < len(Y) - 1:
                delta_departure = (Z[i, j + 1] - Z[i, j]) / (Y[j + 1] - Y[j])
            else:
                delta_departure = 0  # 边界点设为 0

            # 合并变化率
            total_change_rate[i, j] = np.sqrt(delta_arrival**2 + delta_departure**2)

    return X, Y, total_change_rate


# 热力图可视化
def visualize_instantaneous_change_heatmap(X, Y, Z):
    """
    可视化瞬时变化率的热图。
    """
    # 创建 DataFrame 以便用 Seaborn 绘图
    df = pd.DataFrame(Z, index=X, columns=Y)

    # 绘制热图
    plt.figure(figsize=(10, 8))
    sns.heatmap(df, annot=True, fmt=".2f", cmap="coolwarm", cbar_kws={'label': 'Change Rate'})
    plt.title("Sensitivity Analysis: Instantaneous Change Rate", fontsize=15, fontweight="bold")
    plt.xlabel("Departure Rate Multiplier", fontsize=12)
    plt.ylabel("Arrival Rate Multiplier", fontsize=12)
    plt.show()


# 主程序
if __name__ == "__main__":
    # 参数范围
    arrival_rate_multipliers = [0.8, 1.0, 1.2]  # 到达率的取值范围
    departure_rate_multipliers = [0.8, 1.0, 1.2]  # 离开率的取值范围

    # 运行分析
    print("Running sensitivity analysis...")
    results_df = run_arrival_vs_departure_analysis(arrival_rate_multipliers, departure_rate_multipliers, sample_size=1)

    # 计算瞬时变化率
    X, Y, total_change_rate = calculate_instantaneous_change_heatmap(results_df)

    # 绘制热图
    visualize_instantaneous_change_heatmap(X, Y, total_change_rate)
