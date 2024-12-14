import heapq
import numpy as np
import random

# 参数默认值
request_frequency = 2  # 每小时平均服务请求频率
number_of_care_givers = 50  # 护理人员数量
capacity = 100  # ICU 容量
time_horizon = 10  # 模拟时间范围 (天)
service_type = [1, 2, 3]  # 服务类型: 1-小型, 2-中型, 3-大型
mean_service_time = [0.2, 0.5, 1]  # 服务时间 (小时)
b_1 = 0.2  # 第一阶段结束点
b_2 = 0.9  # 第二阶段结束点
average_length_of_stays = [3, 7, 15]  # 患者平均住院时间 (天)

service_probabilities = {
    1: {  # 轻度病例
        'first': [0.1, 0.3, 0.6],
        'middle': [0.3, 0.5, 0.2],
        'last': [0.6, 0.3, 0.1],
    },
    2: {  # 中度病例
        'first': [0.1, 0.2, 0.7],
        'middle': [0.2, 0.5, 0.3],
        'last': [0.5, 0.3, 0.2],
    },
    3: {  # 重度病例
        'first': [0.1, 0.1, 0.8],
        'middle': [0.2, 0.3, 0.5],
        'last': [0.5, 0.3, 0.2],
    },
}
def modify_parameters(arrival_rate_multiplier=1.0, service_time_multiplier=1.0, 
                      request_frequency_val=None, cutoff_points=None, departure_rate_multiplier=1.0):
    global request_frequency, mean_service_time, b_1, b_2, average_length_of_stays

    # 修改服务请求频率
    if request_frequency_val:
        request_frequency = request_frequency_val
    else:
        request_frequency *= arrival_rate_multiplier  # 使用到达率调整

    # 修改服务时间
    mean_service_time = [x * service_time_multiplier for x in mean_service_time]

    # 修改阶段分割点
    if cutoff_points:
        b_1, b_2 = cutoff_points

    # 修改离开率
    average_length_of_stays = [x * departure_rate_multiplier for x in average_length_of_stays]

# 模拟服务过程
def simulate_service_process(start_times, departure_times, severity_level_list, arrival_times,
                             request_frequency=request_frequency, capacity=capacity, 
                             number_of_care_givers=number_of_care_givers, time_horizon=time_horizon,
                             service_type=service_type, mean_service_time=mean_service_time, b_1=b_1, b_2=b_2):
    # 初始化状态和数据结构
    patient_states = [0] * len(arrival_times)
    service_start_times = [-1] * capacity
    service_end_times = [-1] * capacity
    index_list = [-1] * capacity
    service_waiting_times = []
    severity_cor_waiting_times = []
    care_giver_heap = []

    service_lambda_max = request_frequency * capacity
    t = 0

    while t < time_horizon * 24:
        t += np.random.exponential(1 / service_lambda_max)

        if t > time_horizon * 24:
            break

        number_of_patients = len(start_times)

        # 更新患者状态
        for i in range(number_of_patients):
            if t >= start_times[i] and t < departure_times[i] and patient_states[i] == 0:
                patient_states[i] = 1

        for i in range(number_of_patients):
            if t >= departure_times[i]:
                if patient_states[i] == 2:
                    bed_index = index_list.index(i)
                    service_start_times[bed_index] = -1
                    service_end_times[bed_index] = -1
                patient_states[i] = 0

        for i in range(number_of_patients):
            if patient_states[i] == 2:
                bed_index = index_list.index(i)
                if service_end_times[bed_index] > 0 and service_end_times[bed_index] <= t:
                    patient_states[i] = 1
                    service_start_times[bed_index] = -1
                    service_end_times[bed_index] = -1

        number_of_state_1_patients = patient_states.count(1)

        if number_of_state_1_patients > 0 and random.uniform(0, 1) < number_of_state_1_patients / capacity:
            selection = np.where(np.array(patient_states) == 1)[0]
            patient_request_service = random.choice(selection)
            patient_states[patient_request_service] = 2
            severity = severity_level_list[patient_request_service]

            elapsed_time = t - start_times[patient_request_service]
            total_stay_duration = departure_times[patient_request_service] - start_times[patient_request_service]
            fraction_elapsed = elapsed_time / total_stay_duration

            if fraction_elapsed <= b_1:
                phase = 'first'
            elif fraction_elapsed <= b_2:
                phase = 'middle'
            else:
                phase = 'last'

            probabilities = service_probabilities[severity][phase]
            service = np.random.choice(service_type, p=probabilities)
            service_time = np.random.exponential(mean_service_time[service - 1])

            if -1 in service_start_times:
                choice = service_start_times.index(-1)
            else:
                continue

            if len(care_giver_heap) >= number_of_care_givers:
                earliest_available_time = heapq.heappop(care_giver_heap)
                service_start_time = max(earliest_available_time, t)
            else:
                service_start_time = t

            service_start_times[choice] = service_start_time
            service_end_time = min(service_start_time + service_time, departure_times[patient_request_service])
            service_end_times[choice] = service_end_time
            index_list[choice] = patient_request_service

            heapq.heappush(care_giver_heap, service_end_time)

            service_waiting_times.append(service_start_time - t)
            severity_cor_waiting_times.append(severity_level_list[patient_request_service])

    service_waiting_times = [x * 60 for x in service_waiting_times]
    return service_waiting_times, severity_cor_waiting_times