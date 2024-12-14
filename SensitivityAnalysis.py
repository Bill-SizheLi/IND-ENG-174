import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from CareRequest import simulate_service_process, modify_parameters
import sys

# 设置项目路径
project_root = '/Users/kennychan/Downloads/IND-ENG-174'
sys.path.append(project_root)

from Part_1_IcuQueue.DepartureProcessWithFIFO import simultaneously_return

# 设置随机种子
random_seed = 5
np.random.seed(random_seed)

# 灵敏度分析的变量范围和基本参数
base_params = {
    "arrival_rate": 1.0,
    "service_time": 1.0,
    "request_frequency": 2.0,
    "cutoff_point": (0.2, 0.9),
    "departure_rate": 1.0
}
delta = 0.1  # 参数变化量

# 惩罚函数
def penaltyFunction2(m_2, alpha_2, service_waiting_times, severity_cor_waiting_times):
    total_penalty = 0
    for i in range(len(service_waiting_times)):
        severity = severity_cor_waiting_times[i]
        waiting_time = service_waiting_times[i]
        total_penalty += m_2 * (np.exp(alpha_2 * severity * waiting_time) - 1)
    return total_penalty

def multi_simulation(params, num_simulations=5):
    """
    根据输入参数运行多次仿真，并返回平均惩罚值。
    
    参数：
    - params: 字典，包含要修改的仿真参数。
    - num_simulations: 运行仿真的次数。
    
    返回：
    - 平均惩罚值。
    """
    total_penalty = 0

    for _ in range(num_simulations):
        modify_parameters(
            arrival_rate_multiplier=params["arrival_rate"],
            service_time_multiplier=params["service_time"],
            request_frequency_val=params["request_frequency"],
            cutoff_points=params["cutoff_point"],
            departure_rate_multiplier=params["departure_rate"]
        )

        # 模拟并计算惩罚值
        arrival_times, severity_level_list, start_times, departure_times, waiting_times = simultaneously_return()
        service_waiting_times, severity_cor_waiting_times = simulate_service_process(
            start_times, departure_times, severity_level_list, arrival_times
        )
        total_penalty += penaltyFunction2(
            m_2=0.01,
            alpha_2=0.1,
            service_waiting_times=service_waiting_times,
            severity_cor_waiting_times=severity_cor_waiting_times
        )

    # 返回平均惩罚值
    return total_penalty / num_simulations


# 灵敏度分析
def run_sensitivity_analysis(base_params, delta, num_simulations=5):
    """
    对指定的参数进行灵敏度分析，计算每个参数的相对变化对平均惩罚值的影响。
    """
    results = []

    for param_name in base_params.keys():
        # 计算基准值
        base_penalty = multi_simulation(base_params, num_simulations=num_simulations)

        # 增加参数
        increased_params = base_params.copy()
        if param_name == "cutoff_point":
            increased_params[param_name] = (base_params[param_name][0] + delta, base_params[param_name][1] + delta)
        else:
            increased_params[param_name] += delta
        increased_penalty = multi_simulation(increased_params, num_simulations=num_simulations)

        # 计算相对变化量
        relative_effect = (increased_penalty - base_penalty) / base_penalty
        results.append({"Parameter": param_name, "Effect": relative_effect})

    return pd.DataFrame(results)


# Tornado 图绘制
def plot_tornado_chart(results_df):
    """
    根据灵敏度分析的结果绘制 Tornado 图。
    """
    # 按变化量排序
    results_df = results_df.sort_values(by="Effect", ascending=False)

    # 创建 Tornado 图
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(results_df["Parameter"], results_df["Effect"], color="steelblue")
    ax.set_xlabel("Effect on Penalty", fontsize=12)
    ax.set_ylabel("Parameters", fontsize=12)
    ax.set_title("Tornado Chart: Sensitivity Analysis", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 参数范围
    delta = 0.1  # 参数变化幅度
    num_simulations = 5  # 仿真次数

    # 运行灵敏度分析
    sensitivity_results = run_sensitivity_analysis(base_params, delta, num_simulations)

    # 绘制 Tornado 图
    plot_tornado_chart(sensitivity_results)
