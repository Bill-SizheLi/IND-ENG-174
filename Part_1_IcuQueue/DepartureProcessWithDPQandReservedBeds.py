import numpy as np
import heapq
from Part_1_IcuQueue.ArrivalProcess import simulate_arrival_process, generate_length_of_stays, rate_distribution_pdf

# Parameters
m_1 = 1  # Penalty scale
alpha_1 = 0.01  # Time sensitivity
capacity = 100  # ICU capacity
reserved_capacity = 30  # Reserved bed capacity
regular_capacity = capacity - reserved_capacity  # Regular ICU beds
average_length_of_stays = [3, 7, 15]
# Penalty function
def penalty_function(m_1, alpha_1, severity, waiting_time):
    return m_1 * (severity ** 2) + alpha_1 * (waiting_time ** 1.5) * severity

def simulate_departure_process_with_dynamic_priority_and_reserved(arrival_times, severity_level_list, length_of_stays, capacity, reserved_capacity, m_1, alpha_1):
    num_patients = len(arrival_times)
    start_times = [None] * num_patients
    departure_times = [None] * num_patients
    current_regular_ICU_departures = []  # Regular ICU beds (departure_time, index)
    current_reserved_ICU_departures = []  # Reserved ICU beds (departure_time, index)
    waiting_queue = []  # Dynamic priority queue (Penalty value, arrival_time, index)

    for i in range(num_patients):
        arrival_time = arrival_times[i]
        severity = severity_level_list[i]

        # Remove patients who have already departed
        while current_regular_ICU_departures and current_regular_ICU_departures[0][0] <= arrival_time:
            heapq.heappop(current_regular_ICU_departures)
        
        while current_reserved_ICU_departures and current_reserved_ICU_departures[0][0] <= arrival_time:
            heapq.heappop(current_reserved_ICU_departures)

        # Dynamically update priorities in the waiting queue
        updated_waiting_queue = []
        for _, w_arrival_time, w_index in waiting_queue:
            waiting_time = arrival_time - w_arrival_time
            dynamic_penalty = -penalty_function(m_1, alpha_1, severity_level_list[w_index], waiting_time)
            updated_waiting_queue.append((dynamic_penalty, w_arrival_time, w_index))
        heapq.heapify(updated_waiting_queue)  # Rebuild the heap with updated priorities
        waiting_queue = updated_waiting_queue

        # Calculate the penalty for the current patient and add them to the waiting queue
        penalty = -penalty_function(m_1, alpha_1, severity, 0)  # Initial penalty
        heapq.heappush(waiting_queue, (penalty, arrival_time, i))

        # Assign ICU beds if available
        while len(current_regular_ICU_departures) < regular_capacity and waiting_queue:
            _, w_arrival_time, w_index = heapq.heappop(waiting_queue)
            w_start_time = max(w_arrival_time, arrival_time)
            start_times[w_index] = w_start_time
            w_departure_time = w_start_time + length_of_stays[w_index] * 24
            departure_times[w_index] = w_departure_time
            heapq.heappush(current_regular_ICU_departures, (w_departure_time, w_index))

        # Assign reserved bed for severe patients if available
        if severity == 3 and len(current_reserved_ICU_departures) < reserved_capacity:
            if waiting_queue:  # Only pop if there are elements in the queue
                _, w_arrival_time, w_index = heapq.heappop(waiting_queue)
                w_start_time = max(w_arrival_time, arrival_time)
                start_times[w_index] = w_start_time
                w_departure_time = w_start_time + length_of_stays[w_index] * 24
                departure_times[w_index] = w_departure_time
                heapq.heappush(current_reserved_ICU_departures, (w_departure_time, w_index))

    # Process remaining patients in the waiting queue after all arrivals
    current_time = arrival_times[-1]
    while waiting_queue:
        # Dynamically update priorities in the waiting queue
        updated_waiting_queue = []
        for _, w_arrival_time, w_index in waiting_queue:
            waiting_time = current_time - w_arrival_time
            dynamic_penalty = -penalty_function(m_1, alpha_1, severity_level_list[w_index], waiting_time)
            updated_waiting_queue.append((dynamic_penalty, w_arrival_time, w_index))
        heapq.heapify(updated_waiting_queue)  # Rebuild the heap with updated priorities
        waiting_queue = updated_waiting_queue

        # Ensure the queue is not empty before popping
        if waiting_queue:
            _, w_arrival_time, w_index = heapq.heappop(waiting_queue)
            if current_regular_ICU_departures:
                earliest_departure_time, _ = heapq.heappop(current_regular_ICU_departures)
                start_time = max(w_arrival_time, earliest_departure_time)
            else:
                start_time = current_time
            start_times[w_index] = start_time
            departure_time = start_time + length_of_stays[w_index] * 24
            departure_times[w_index] = departure_time
            heapq.heappush(current_regular_ICU_departures, (departure_time, w_index))

    return departure_times, start_times


def simultaneously_return(m_1=m_1, alpha_1=alpha_1, delta_arrival=0, delta_length_of_stays=0.00):
    """
    Package and return simulation results for external use
    """
    arrival_times, severity_level_list = simulate_arrival_process(delta_arrival=delta_arrival)
    length_of_stays = generate_length_of_stays(severity_level_list,average_length_of_stays=[days + delta_length_of_stays for days in average_length_of_stays])

    departure_times, start_times = simulate_departure_process_with_dynamic_priority_and_reserved(
        arrival_times, severity_level_list, length_of_stays, capacity, reserved_capacity, m_1, alpha_1
    )
    waiting_times = [start_times[i] - arrival_times[i] for i in range(len(arrival_times))]
    return arrival_times, severity_level_list, start_times, departure_times, waiting_times
