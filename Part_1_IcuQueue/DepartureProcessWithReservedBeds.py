import sys

project_root = '/Users/kennychan/Downloads/IND-ENG-174'
sys.path.append(project_root)

from ArrivalProcess import simulate_arrival_process, generate_length_of_stays
import numpy as np
import heapq


capacity = 100 # If you want to modify this parameter, please simultaneously modify 'capacity' in Part_2_CareGiver/CareRequest.py
reserved_capacity = 30


def simulate_departure_process_with_reserved_beds(arrival_times, severity_level_list,
                                               capacity=capacity, reserved_capacity=reserved_capacity):
    regular_capacity = capacity - reserved_capacity 
    length_of_stays = generate_length_of_stays(severity_level_list)

    departure_times = []
    start_times = []

    current_regular_ICU_departures = []  
    current_reserved_ICU_departures = []  

    for i in range(len(arrival_times)):
        arrival_time = arrival_times[i]
        severity = severity_level_list[i]
        length_of_stay = length_of_stays[i]


        while current_regular_ICU_departures and arrival_time >= current_regular_ICU_departures[0][0]:
            previous_departure_time, departure_index = heapq.heappop(current_regular_ICU_departures)
            departure_times[departure_index] = previous_departure_time


        while current_reserved_ICU_departures and arrival_time >= current_reserved_ICU_departures[0][0]:
            previous_departure_time, departure_index = heapq.heappop(current_reserved_ICU_departures)
            departure_times[departure_index] = previous_departure_time


        if severity in [1, 2]:
            # if regular beds not full
            if len(current_regular_ICU_departures) < regular_capacity:
                start_time = arrival_time
            else:
                earliest_available_time, available_index = heapq.heappop(current_regular_ICU_departures)
                start_time = max(arrival_time, earliest_available_time)
            
            departure_time = start_time + length_of_stay * 24  
            heapq.heappush(current_regular_ICU_departures, (departure_time, i))

        elif severity == 3:
            # if regular beds are not full
            if len(current_regular_ICU_departures) < regular_capacity:
                start_time = arrival_time
                departure_time = start_time + length_of_stay * 24
                heapq.heappush(current_regular_ICU_departures, (departure_time, i))
            # if regular beds full but reserved beds are not full
            elif len(current_reserved_ICU_departures) < reserved_capacity:
                start_time = arrival_time
                departure_time = start_time + length_of_stay * 24
                heapq.heappush(current_reserved_ICU_departures, (departure_time, i))
            # if regular and reserved beds are both full
            else:
                next_regular_available = current_regular_ICU_departures[0][0] 
                next_reserved_available = current_reserved_ICU_departures[0][0] 

                earliest_available_time = min(next_regular_available, next_reserved_available)
                start_time = max(arrival_time, earliest_available_time)
                if earliest_available_time == next_regular_available:
                    heapq.heappop(current_regular_ICU_departures)
                    departure_time = start_time + length_of_stay * 24
                    heapq.heappush(current_regular_ICU_departures, (departure_time, i))
                else:
                    heapq.heappop(current_reserved_ICU_departures)
                    departure_time = start_time + length_of_stay * 24
                    heapq.heappush(current_reserved_ICU_departures, (departure_time, i))

        start_times.append(start_time)
        departure_times.append(departure_time)

    return departure_times, start_times


def calculate_waiting_times(arrival_times, start_times):
    waiting_times = []

    for i in range(len(arrival_times)):
        waiting_time = start_times[i] - arrival_times[i]
        waiting_times.append(waiting_time)

    return waiting_times


def simultaneously_return():
    arrival_times, severity_level_list = simulate_arrival_process()
    departure_times, start_times = simulate_departure_process_with_reserved_beds(arrival_times, severity_level_list)
    waiting_times = calculate_waiting_times(arrival_times, start_times)
    return arrival_times, severity_level_list, start_times, departure_times, waiting_times


