from ArrivalProcess import simulate_arrival_process, rate_distribution_pdf, generate_length_of_stays
import heapq


arrival_times, severity_level_list = simulate_arrival_process()
average_length_of_stays = [3, 7, 15] # averagely, Mild - 3 days; Moderate - 7 days; Severe - 15 days.
capacity = 100 # If you want to modify this parameter, please simultaneously modify 'capacity' in Part_2_CareGiver/CareRequest.py
# This function tracks the departure times of patients under the assumption of FIFO.
def simulate_departure_process_FIFO(arrival_times, severity_level_list, length_of_stays, capacity = capacity):
    departure_times = []
    current_ICU_departures = [] # tracks the departure times of those patients currently in ICU.
    start_times = []

    for i in range(len(arrival_times)):
        arrival_time = arrival_times[i]
        length_of_stay = length_of_stays[i] # in days

        if len(current_ICU_departures) >= capacity:
            earliest_available_time = heapq.heappop(current_ICU_departures)  
            start_time = max(arrival_time, earliest_available_time)
        else:
            start_time = arrival_time 

        start_times.append(start_time)

        departure_time = start_time + length_of_stay * 24
        departure_times.append(departure_time)

        heapq.heappush(current_ICU_departures, departure_time)

    return departure_times, start_times
        

#print(arrival_times)
#print(start_times)
#print(simulate_departure_process_FIFO())

def calculate_waiting_times(arrival_times, start_times):
    waiting_times = []

    for i in range(len(arrival_times)):
        waiting_time = start_times[i] - arrival_times[i]
        waiting_times.append(waiting_time)

    return waiting_times

#print(calculate_waiting_times())


#print(len(severity_level_list))
#print(len(waiting_times))

# To resolve the in-consistency issue.
def simultaneously_return(delta_arrival=0, delta_length_of_stays=0.00, capacity = capacity):
    """
    Package and return simulation results for external use
    """
    arrival_times, severity_level_list = simulate_arrival_process(delta_arrival=delta_arrival)
    length_of_stays = generate_length_of_stays(severity_level_list,average_length_of_stays=[days + delta_length_of_stays for days in average_length_of_stays])
    
    departure_times, start_times = simulate_departure_process_FIFO(arrival_times, severity_level_list, length_of_stays, capacity)
    
    waiting_times = calculate_waiting_times(arrival_times, start_times)
    return arrival_times, severity_level_list, start_times, departure_times, waiting_times
