import heapq
from ArrivalProcess import simulate_arrival_process, rate_distribution_pdf, generate_length_of_stays

capacity = 100  # Maximum ICU capacity
average_length_of_stays = [3, 7, 15]
def simulate_departure_process_priority(arrival_times, severity_level_list, length_of_stays, capacity=capacity):
    departure_times = [None] * len(arrival_times)
    current_ICU_departures = []   
    start_times = [None] * len(arrival_times)
    waiting_queue = []  # Priority queue to manage patients waiting for ICU admission
    

    for i in range(len(arrival_times)):
        temporary_departure_time_list = []
        arrival_time = arrival_times[i]
        severity = severity_level_list[i]
        length_of_stay = length_of_stays[i]

        while current_ICU_departures and arrival_time >= current_ICU_departures[0][0]:
            previous_departure_time, departure_index = heapq.heappop(current_ICU_departures)
            departure_times[departure_index] = previous_departure_time
            temporary_departure_time_list.append(previous_departure_time)


            if waiting_queue:
                _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)
                start_time = temporary_departure_time_list.pop(0)
                start_times[waiting_index] = start_time

                # Calculate departure time and add to ICU
                departure_time = start_time + length_of_stays[waiting_index] * 24
                departure_times[waiting_index] = departure_time
                heapq.heappush(current_ICU_departures, (departure_time, waiting_index))
                

        # If there is an available bed in the ICU
        if len(current_ICU_departures) < capacity:
            
            start_time = arrival_time
            start_times[i] = start_time

            # Calculate departure time and add to ICU
            departure_time = start_time + length_of_stay * 24
            departure_times[i] = departure_time
            heapq.heappush(current_ICU_departures, (departure_time, i))
            
        else:
            # If ICU is full, add the patient to the waiting queue
            heapq.heappush(waiting_queue, (-severity, severity, i))  # Use negative severity to implement a max heap
    
      
    # Process remaining patients in the waiting queue
    current_time = arrival_times[-1]
    while waiting_queue:
        while current_ICU_departures and current_time >= current_ICU_departures[0][0]:
            previous_departure_time, departure_index = heapq.heappop(current_ICU_departures)
            departure_times[departure_index] = previous_departure_time
            temporary_departure_time_list.append(previous_departure_time)

            _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)
            start_time = temporary_departure_time_list.pop(0)
            start_times[waiting_index] = start_time

            # Calculate departure time and add to ICU
            departure_time = start_time + length_of_stays[waiting_index] * 24
            departure_times[waiting_index] = departure_time
            heapq.heappush(current_ICU_departures, (departure_time, waiting_index))
          

        if len(current_ICU_departures) < capacity:
            _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)
            start_time = current_time
            start_times[waiting_index] = start_time

            # Calculate departure time and add to ICU
            departure_time = start_time + length_of_stays[waiting_index] * 24
            departure_times[waiting_index] = departure_time
            heapq.heappush(current_ICU_departures, departure_time)


        else:
            earliest_available_time, departure_index = heapq.heappop(current_ICU_departures) 
            _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)

            # Assign the bed to the patient in the waiting queue
            start_time = earliest_available_time
            start_times[waiting_index] = start_time

            # Calculate departure time and add to ICU
            departure_time = start_time + length_of_stays[waiting_index] * 24
            departure_times[waiting_index] = departure_time
            heapq.heappush(current_ICU_departures, (departure_time, waiting_index))
            current_time = start_time
  
    return departure_times, start_times



# Calculate waiting times
def calculate_waiting_times(arrival_times, start_times):
    waiting_times = []
    for i in range(len(arrival_times)):
        waiting_time = start_times[i] - arrival_times[i]
        waiting_times.append(waiting_time)
    return waiting_times


# Package the results for return
def simultaneously_return(delta_arrival = 0.00, delta_length_of_stays=0.00, capacity=capacity):
    arrival_times, severity_level_list = simulate_arrival_process(delta_arrival=delta_arrival)
    length_of_stays = generate_length_of_stays(severity_level_list,average_length_of_stays=[days + delta_length_of_stays for days in average_length_of_stays])
    departure_times, start_times = simulate_departure_process_priority(arrival_times, severity_level_list, length_of_stays, capacity)
    waiting_times = calculate_waiting_times(arrival_times, start_times)
    return arrival_times, severity_level_list, start_times, departure_times, waiting_times



'''
# Visualize the distribution of waiting times (only for admitted patients)
import matplotlib.pyplot as plt

valid_waiting_times = [wt for wt in waiting_times]
plt.hist(valid_waiting_times, bins=100, alpha=0.7)
plt.xlabel("Waiting Time")
plt.ylabel("Number of Patients")
plt.title("Distribution of Waiting Times (hours)")
plt.show()
'''